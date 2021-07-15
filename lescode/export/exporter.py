from inspect import currentframe, getmembers, getouterframes, isclass
from importlib import import_module
from pathlib import Path
from typing import Callable, Dict, Any
from functools import lru_cache

__all__ = [
    'export',
    'export_subclass'
]


@lru_cache(maxsize=1)
def _get_cache():
    return set()


def export(predicate:Callable[[Any], bool], idx:int=1, module:Any=None, package:str=None, registry:Dict[str, Any]=None):
    curr_frame = currentframe()
    outer_frames = getouterframes(curr_frame)

    call_frame = outer_frames[idx]

    _globals = call_frame.frame.f_globals
    _locals = call_frame.frame.f_locals

    current_file = Path(_globals['__file__']).resolve()

    cached = _get_cache()
    if (current_file.as_posix(), call_frame.frame.f_lineno) in cached:
        return

    cached.add((current_file.as_posix(), call_frame.frame.f_lineno)) 
    current_dir = current_file.parent

    if package is None:
        package = __name__
        for frame in reversed(outer_frames):
            call_dir = Path(frame.frame.f_globals['__file__']).resolve().parent
            if current_dir.as_posix().startswith(call_dir.as_posix()):
                package = frame.frame.f_globals["__package__"]
                subpackage = current_dir.relative_to(call_dir).as_posix().replace('/', '.')
                package = f"{package}.{subpackage}" if package else subpackage
                break

    if '__all__' not in _globals:
        _globals['__all__'] = []

    __all = _globals['__all__']

    for fn in current_dir.rglob("*.py"):
        path = fn.relative_to(current_dir).as_posix()[:-3]
        target = module or import_module('.' + path.replace('/', '.'), package=package)

        members = getmembers(
            target, 
            predicate=predicate
        )

        for name, cls in members:
            if name not in _locals:
                _locals[name] = cls
                __all.append(name)
                
                if registry is not None:
                    registry[name] = cls


def export_subclass(*classes, module:Any=None, package:str=None, registry:Dict[str, Any]=None):
    predicate = lambda cls: isclass(cls) and issubclass(cls, classes)
    export(predicate, idx=2, module=module, package=package, registry=registry)


def export_instance(*classes, module:Any=None, package:str=None, registry:Dict[str, Any]=None):
    predicate = lambda ins: isinstance(ins, classes)
    export(predicate, idx=2, module=module, package=package, registry=registry)
