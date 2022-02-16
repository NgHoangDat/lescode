import functools
from typing import *
from typing import Callable


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
