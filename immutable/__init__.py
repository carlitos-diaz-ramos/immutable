__version__ = "0.1.0"

###############################################################################
__all__ = [
    'Immutable', 'ConstantAttributeError', 'ConstantIndexError', 'immutable',
    'ImmutableProxy', 'DeepImmutableProxy', 
    'get_type', 'is_instance',
]

import datetime
import pathlib
import re
import types

from .immutable import Immutable
from .exceptions import ConstantAttributeError, ConstantIndexError
from .proxy import ImmutableProxy   
from .deep import DeepImmutableProxy
from .decorator import immutable
from .checktype import get_type, is_instance
from .extraproxies import (
    DictImmutableProxy, ListImmutableProxy, TupleImmutableProxy,
)


###############################################################################
_builtin_registered = (
    bytes, int, float, complex, str, type(None), 
    re.Pattern, re.Match, datetime.date, pathlib.Path, types.ModuleType, 
)
for type_ in _builtin_registered:
    ImmutableProxy.register_immutable(type_)

ImmutableProxy.register_proxy(tuple, TupleImmutableProxy)
ImmutableProxy.register_proxy(dict, DictImmutableProxy)
ImmutableProxy.register_proxy(list, ListImmutableProxy)
