import datetime
import pathlib
import re
import types

from .proxy import ImmutableProxy
from .extraproxies import (
    TupleImmutableProxy, DictImmutableProxy, ListImmutableProxy,
)

_builtin_registered = (
    bytes, int, float, complex, str, type(None), 
    re.Pattern, re.Match, datetime.date, pathlib.Path, types.ModuleType, 
)
for type_ in _builtin_registered:
    ImmutableProxy.register_immutable(type_)

ImmutableProxy.register_proxy(tuple, TupleImmutableProxy)
ImmutableProxy.register_proxy(dict, DictImmutableProxy)
ImmutableProxy.register_proxy(list, ListImmutableProxy)
