__version__ = "0.1.1"

__all__ = [
    'Immutable', 'ConstantAttributeError', 'ConstantIndexError', 'immutable',
    'ImmutableProxy', 'DeepImmutableProxy', 
    'get_type', 'is_instance',
]

from .immutable import Immutable
from .exceptions import ConstantAttributeError, ConstantIndexError
from .proxy import ImmutableProxy   
from .deep import DeepImmutableProxy
from .decorator import immutable
from .checktype import get_type, is_instance
from . import register

