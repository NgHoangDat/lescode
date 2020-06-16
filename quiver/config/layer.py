from typing import *

from ..functional import case, compose, is_instance, map


BaseLayer = type('BaseLayer', (Mapping,), {})


def build_layer(keys:Tuple[str, ...], values:Tuple[Any, ...]) -> BaseLayer:

    keys = tuple(keys)
    values = tuple(values)

    class Layer(BaseLayer):
        
        def __getattribute__(self, name:str):
            if name in keys:
                index = keys.index(name)
                return values[index]

            return super(Layer, self).__getattribute__(name)
        
        def __contains__(self, key:str):
            return key in keys

        def __getitem__(self, ind:Union[int, str]):
            return self.__getattribute__(ind)

        def __iter__(self):
            for key in keys:
                yield key
        
        def __repr__(self):
            return asdict(self).__repr__()

        def __len__(self):
            return len(keys)

    return Layer()


def itemsof(layer:BaseLayer) -> Iterator[Tuple[str, Any]]:
    for key in layer:
        yield key, layer[key]


def keysof(layer:BaseLayer) -> Iterator[str]:
    for key in layer:
        yield key


def valuesof(layer:BaseLayer) -> Iterator[Any]:
    for key in keysof(layer):
        yield layer[key]


def asdict(layer:BaseLayer):
    parse_tuple = lambda val: tuple(map(
        case(predicate=is_instance(BaseLayer), action=asdict),
        val
    ))

    parse = case(
        predicate=is_instance(BaseLayer),
        action=asdict,
        otherwise=case(
            predicate=is_instance(tuple),
            action=parse_tuple
        )
    )

    return {key: parse(value) for key, value in itemsof(layer)}


def asclass(data:Dict[str, Any]):
    parse_list = lambda val: tuple(map(
        case(
            predicate=is_instance(dict),
            action=asclass,
            otherwise=case(
                predicate=is_instance(list),
                action=parse_list
            )
        ),
        val
    ))

    parse = case(
        predicate=is_instance(dict),
        action=asclass,
        otherwise=case(
            predicate=is_instance(list),
            action=parse_list
        )
    )

    if data:
        keys, values = zip(*data.items())
        values = compose(tuple, map(parse))(values)
    else:
        keys, values = (), ()

    return build_layer(keys, values)
