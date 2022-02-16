from collections import OrderedDict
from typing import *


def object_pool(
    _cls: Optional[type] = None, *, max_size: int = 0, default_key: str = "default"
):
    def wrap(_cls):
        class Pool:
            __OBJECT_CLASS: Type[_cls] = _cls
            __OBJECTS_POOL: Dict[str, _cls] = OrderedDict()
            __DEFAULT_KEY: str = default_key
            __MAX_SIZE: int = max_size

            def __new__(cls, *args, **kwargs):
                return cls.__OBJECT_CLASS(*args, **kwargs)

            @classmethod
            def base(cls):
                return cls.__OBJECT_CLASS

            @classmethod
            def get(
                cls, _name: Optional[str] = None, overwrite: bool = True, **kwargs
            ) -> _cls:
                if _name is None:
                    _name = cls.__DEFAULT_KEY

                if _name not in cls.__OBJECTS_POOL:
                    if cls.__MAX_SIZE and len(cls.__OBJECTS_POOL) == cls.__MAX_SIZE:
                        if not overwrite:
                            raise Exception("pool overflowed")
                        cls.__OBJECTS_POOL.popitem(last=False)

                    cls.__OBJECTS_POOL[_name] = cls.__OBJECT_CLASS(**kwargs)

                return cls.__OBJECTS_POOL[_name]

            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                cls.__OBJECT_CLASS = type(cls.__name__, (_cls,), dict(cls.__dict__))
                cls.__OBJECTS_POOL: Dict[str, cls] = OrderedDict()

        return Pool

    if _cls is None:
        return wrap

    return wrap(_cls)
