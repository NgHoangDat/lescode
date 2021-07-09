from inspect import currentframe, getmembers, getouterframes, isclass
from importlib import import_module
from pathlib import Path
from typing import Callable, Dict, Any

__all__ = [
    'export',
    'export_subclass'
]


def export(predicate:Callable[[Any], bool], idx:int=1, module:Any=None) -> Dict[str, Any]:
    curr_frame = currentframe()
    outer_frames = getouterframes(curr_frame)

    call_frame = outer_frames[idx]
    orig_frame = outer_frames[-1]

    call_dir = Path(orig_frame.frame.f_globals['__file__']).resolve().parent

    _globals = call_frame.frame.f_globals
    _locals = call_frame.frame.f_locals

    current_file = Path(_globals['__file__']).resolve()
    current_dir = current_file.parent
    package = current_dir.relative_to(call_dir).as_posix().replace('/', '.')

    if '__all__' not in _globals:
        _globals['__all__'] = []

    __all = _globals['__all__']

    items = {}
    for fn in current_dir.rglob("*.py"):
        path = fn.relative_to(current_dir).as_posix()[:-3]
        if module is None:
            target = import_module('.' + path.replace('/', '.'), package=package)
        else:
            target = module

        members = getmembers(
            target, 
            predicate=predicate
        )

        for name, cls in members:
            if name not in _locals:
                _locals[name] = cls
                __all.append(name)

                items[name] = cls

    return items


def export_subclass(*classes, module:Any=None) -> Dict[str, Any]:
    predicate = lambda cls: isclass(cls) and issubclass(cls, classes)
    return export(predicate, idx=2, module=module)
