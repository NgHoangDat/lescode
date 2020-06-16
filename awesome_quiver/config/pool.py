import json
from pathlib import Path
from typing import *

from yaml import Loader, load

from ..functional import curry
from .layer import BaseLayer, asclass


def load_yaml(stream):
    return load(stream, Loader=Loader) or {}


LOADER = {
    '.json': json.load,
    '.yaml': load_yaml,
    '.yml': load_yaml
}


@curry
def read(_layer:BaseLayer, *keys, shallow_search:bool=True, default:Any=None):
    curr = _layer
    for key in keys:
        if type(curr) in (list, tuple, dict):
            curr = curr[key]
        elif hasattr(curr, key):
            curr = getattr(curr, key)
        elif shallow_search:
            return default
        else:
            return None

    return curr


class Config:

    def __init__(self):
        self.__detail = None

    @property
    def detail(self):
        return self.__detail

    @detail.setter
    def detail(self, params:Dict[Hashable, Any]):
        self.__detail = asclass(params)

    def read(self, *keys, shallow_search:bool=True, default:Any=None, **kwargs):
        return read(self.detail, *keys, shallow_search=shallow_search, default=default)


class ConfigPool:

    __CONF_DATA:Dict[str, Config] = {}

    @classmethod
    def load(cls, path:Union[str, Path], name:str='default', encoding:str='utf-8', *args, **kwargs):
        if type(path) is str:
            path = Path(path)

        with open(path, encoding='utf-8') as f:
            loader = LOADER.get(path.suffix)
            if loader is None:
                raise Exception(f"file format {path.suffix} is not supported")

            params = loader(f)
            config = cls.get(name)
            config.detail = params
        return config

    @classmethod
    def get(cls, name:str='default', **kwargs) -> Config:
        if name not in cls.__CONF_DATA:
            cls.__CONF_DATA[name] = Config()

        return cls.__CONF_DATA[name]
