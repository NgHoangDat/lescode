import functools
from collections import OrderedDict
from typing import *
from typing import Callable, ClassVar


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


def singleton(_cls: Optional[type] = None):
    def wrap(_cls):
        class Singleton:

            __OBJECT_CLASS: Type[_cls] = _cls
            __instance: Optional[_cls] = None

            @classmethod
            def get(cls) -> Optional[_cls]:
                return cls.__instance

            @classmethod
            def set(cls, *args, **kwargs):
                cls.__instance = cls.__OBJECT_CLASS(*args, **kwargs)

            def __init_subclass__(cls):
                cls.__OBJECT_CLASS = type(cls, (_cls,), dict(cls.__dict__))
                cls.__instance: Optional[cls.__OBJECT_CLASS] = None

            def __instancecheck__(self, inst):
                return isinstance(inst, self.__OBJECT_CLASS)

        return Singleton

    if _cls is None:
        return wrap

    return wrap(_cls)


def chain(
    _func: Optional[Callable[[Optional[Tuple[Any, ...]]], Tuple[Any, ...]]] = None,
    prev: Optional[Callable[[Optional[Tuple[Any, ...]]], Tuple[Any, ...]]] = None,
):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(pack: Tuple[Any, ...]):
            return func(pack)

        setattr(wrapper, "__prevs", [])
        if prev:
            prevs = getattr(prev, "__prevs", [])
            wrapper.__prevs.extend(prevs)
            wrapper.__prevs.append(prev)

        def step(start: int, end: Optional[int] = None):
            steps = wrapper.__prevs[start:end]
            if end is None:
                steps.append(wrapper)

            def call(pack: Optional[Tuple[Any, ...]] = None):
                return functools.reduce(lambda param, step: step(param), steps, pack)

            return call

        setattr(wrapper, "step", step)
        return wrapper

    if _func:
        return decorator(_func)

    return decorator
