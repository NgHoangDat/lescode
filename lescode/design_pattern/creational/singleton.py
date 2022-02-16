from typing import *


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
