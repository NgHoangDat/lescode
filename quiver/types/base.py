import copy
import datetime
from functools import partial
from typing import *

import msgpack
from dataclasses import dataclass, field, fields, is_dataclass, _is_dataclass_instance

from ..functional import curry


def get_datetime_decoder(fmt:str="%Y-%m-%d %H:%M:%S.%f"):
    
    def decode_datetime(obj):
        if '__datetime__' in obj:
            obj = datetime.datetime.strptime(obj["as_str"], fmt)
        return obj
    
    return decode_datetime


def get_datetime_encoder(fmt:str="%Y-%m-%d %H:%M:%S.%f"):
    
    def encode_datetime(obj):
        if isinstance(obj, datetime.datetime):
            return {'__datetime__': True, 'as_str': obj.strftime(fmt)}
        return obj

    return encode_datetime


@curry
def asclass(cls, data:Union[Dict[str, Any], Any]):

    if is_dataclass(cls):
        properties = {
            _field.metadata.get('property', _field.name): _field.name for _field in fields(cls)
        }

        types = {
            _field.name: _field.type for _field in fields(cls)
        }
        return cls(**{
            properties[key]: asclass(types[properties[key]], value) 
            for key, value in data.items() if key in properties
        })

    origin = getattr(cls, '__origin__', None)
    if origin:
        if origin in (List, list):
            return [asclass(cls.__args__[0], item) for item in data]

        if origin in (Tuple, tuple):
            return tuple(asclass(cls.__args__[0], item) for item in data)

        if origin in (dict, Dict):
            return {key: asclass(cls.__args__[1], value) for key, value in data.items()}

    return data


def _asdict_inner(obj, dict_factory):
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.metadata.get('property', f.name), value))
        return dict_factory(result)
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_asdict_inner(v, dict_factory) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)((_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory))
                          for k, v in obj.items())
    else:
        return copy.deepcopy(obj)


def asdict(obj, *, dict_factory=dict):
    if not _is_dataclass_instance(obj):
        raise TypeError("asdict() should be called on dataclass instances")
    return _asdict_inner(obj, dict_factory)


def serialize(obj, datetime_fmt:str="%Y-%m-%d %H:%M:%S.%f", **kwargs):
    return msgpack.packb(asdict(obj), default=get_datetime_encoder(datetime_fmt), use_bin_type=True, **kwargs)


def deserialize(cls, dump:Optional[bytes]=None, accept_none:bool=False, datetime_fmt:str="%Y-%m-%d %H:%M:%S.%f", **kwargs):
    if dump is None and not accept_none:
        return partial(deserialize, cls, accept_none=True)
    return asclass(cls, msgpack.unpackb(dump, object_hook=get_datetime_decoder(datetime_fmt), raw=False, **kwargs))
