import asyncio
import json
import logging
import time
from datetime import timedelta
from functools import partial
from pathlib import Path
from threading import Thread
from time import sleep
from typing import *
from typing import Callable

from yaml import Loader, load

from ..functional import curry
from ..scheduler import call_after
from .layer import BaseLayer, asclass, asdict


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
    if keys:
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
    return partial(read, _layer, shallow_search=shallow_search, default=default)


def partial_update(origin:Dict[Hashable, Any], data:Dict[Hashable, Any]) -> Dict[Hashable, Any]:
    updated = origin.copy()
    for key, value in data.items():
        if key in updated:
            if type(updated[key]) is dict and type(value) is dict:
                updated[key] = partial_update(updated[key], value)
                continue
        updated[key] = value
    return updated


class Config:

    def __init__(self):
        self.__detail = None

    @property
    def detail(self):
        return self.__detail

    @detail.setter
    def detail(self, params:Dict[Hashable, Any]):
        self.__detail = asclass(params)

    def get(self, *keys, shallow_search:bool=True, default:Any=None, **kwargs):
        return read(self.detail, *keys, shallow_search=shallow_search, default=default)

    def get_conf(self, *keys, shallow_search:bool=True, default:Any=None, **kwargs):
        return self.get(*keys, shallow_search=shallow_search, default=default, **kwargs)

    def __update(self, data:Dict[Hashable, Any], partial:bool=True):
        if partial:
            self.detail = partial_update(asdict(self.detail), data)
        else:
            self.detail = data

    async def watch_async(self, loop:asyncio.AbstractEventLoop, emitter:Callable, refresh:bool=True, partial:bool=True, logger:Optional[logging.Logger]=None, **timedetail):

        if not asyncio.iscoroutinefunction(emitter):
            emitter = asyncio.coroutine(emitter)

        @call_after(loop, repeated=refresh, **timedetail)
        async def observer(ignore_exception:bool=True):
            try:
                data = await emitter()
                self.__update(data, partial)
            except Exception as e:
                if not ignore_exception:
                    raise e

                if logger:
                    logger.error(e)

        await observer(ignore_exception=False)
        observer.promise(ignore_exception=True)

    def watch(self, emitter:Callable, refresh:bool=True, partial:bool=True, logger:Optional[logging.Logger]=None, **timedetail):
        timestamp = timedelta(**timedetail).total_seconds()

        def observer():
            while True:
                time.sleep(timestamp)
                try:
                    self.__update(emitter(), partial)
                except Exception as e:
                    if logger:
                        logger.error(e)

        self.__update(emitter(), partial)
        task = Thread(target=observer)
        task.daemon = True
        task.start()


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
