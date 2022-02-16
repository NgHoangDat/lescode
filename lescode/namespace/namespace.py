from typing import *
from copy import deepcopy
from functools import partial

from ..functional import case, compose, is_instance, map, curry


class BaseNamespace(Mapping):
    pass


def build(
    data: Optional[Dict[Hashable, Any]] = None, frozen: bool = False
) -> BaseNamespace:

    data = deepcopy(data) if data else {}

    class Namespace(BaseNamespace):
        def __getattribute__(self, key: str):
            if key in data:
                return data[key]

            return super(Namespace, self).__getattribute__(key)

        def __contains__(self, key: str):
            return key in data

        def __getitem__(self, ind: Union[int, str]):
            return self.__getattribute__(ind)

        def __setitem__(self, key: Hashable, value: Any):
            if frozen:
                raise Exception("Namespace is frozen")
            data[key] = value

        def __setattr__(self, key: Hashable, value: Any):
            self.__setitem__(key, value)

        def __iter__(self):
            for key in data:
                yield key

        def __repr__(self):
            return asdict(self).__repr__()

        def __len__(self):
            return len(data)

    return Namespace()


def itemsof(namespace: BaseNamespace) -> Iterator[Tuple[Hashable, Any]]:
    for key in namespace:
        yield key, namespace[key]


def keysof(namespace: BaseNamespace) -> Iterator[Hashable]:
    for key in namespace:
        yield key


def valuesof(namespace: BaseNamespace) -> Iterator[Any]:
    for key in namespace:
        yield namespace[key]


def asdict(namespace: BaseNamespace):
    parse_tuple = lambda val: tuple(
        map(case(predicate=is_instance(BaseNamespace), action=asdict), val)
    )

    parse = case(
        predicate=is_instance(BaseNamespace),
        action=asdict,
        otherwise=case(predicate=is_instance(tuple), action=parse_tuple),
    )

    return {key: parse(value) for key, value in itemsof(namespace)}


def asclass(data: Dict[Hashable, Any], **kwargs):
    parse_list = lambda val: tuple(
        map(
            case(
                predicate=is_instance(dict),
                action=partial(asclass, **kwargs),
                otherwise=case(predicate=is_instance(list), action=parse_list),
            ),
            val,
        )
    )

    parse = case(
        predicate=is_instance(dict),
        action=partial(asclass, **kwargs),
        otherwise=case(predicate=is_instance(list), action=parse_list),
    )

    if data:
        keys, values = zip(*data.items())
        values = compose(tuple, map(parse))(values)
    else:
        keys, values = (), ()

    return build(dict(zip(keys, values)), **kwargs)


@curry
def read(
    _layer: BaseNamespace, *keys, shallow_search: bool = True, default: Any = None
):
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
