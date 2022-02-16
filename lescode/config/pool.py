import asyncio
import json
import logging
import time
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from threading import Thread
from typing import *
from typing import Callable

from yaml import Loader, load

from ..functional import partial_update
from ..scheduler import call_after
from ..namespace import asclass, asdict, read

NoneType = type(None)


def load_yaml(stream):
    return load(stream, Loader=Loader) or {}


LOADER = {".json": json.load, ".yaml": load_yaml, ".yml": load_yaml}


class Config:
    def __init__(self):
        self.__detail = None

    @property
    def detail(self):
        return self.__detail

    @detail.setter
    def detail(self, params: Dict[Hashable, Any]):
        self.__detail = asclass(params)

    def get(self, *keys, shallow_search: bool = True, default: Any = None, **kwargs):
        return read(self.detail, *keys, shallow_search=shallow_search, default=default)

    def __update(self, data: Dict[Hashable, Any], partial: bool = True):
        self.detail = partial_update(asdict(self.detail), data) if partial else data

    async def watch_async(
        self,
        loop: asyncio.AbstractEventLoop,
        emitter: Callable,
        refresh: bool = True,
        partial: bool = True,
        logger: Optional[logging.Logger] = None,
        **timedetail,
    ):

        if not asyncio.iscoroutinefunction(emitter):
            emitter = asyncio.coroutine(emitter)

        @call_after(loop, repeated=refresh, **timedetail)
        async def observer(ignore_exception: bool = True):
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

    def watch(
        self,
        emitter: Callable,
        refresh: bool = True,
        partial: bool = True,
        logger: Optional[logging.Logger] = None,
        **timedetail,
    ):
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


@lru_cache(typed=True)
def get_config(*args, **kwargs):
    return Config()


def load_config(*args, path: Union[str, Path, NoneType] = None, **kwargs):
    params = {}

    if path:
        if type(path) is str:
            path = Path(path)

        with open(path, encoding="utf-8") as f:
            loader = LOADER.get(path.suffix)
            if loader is None:
                raise Exception(f"file format {path.suffix} is not supported")

            params = loader(f)

    config = get_config(*args, **kwargs)
    config.detail = params
    return config
