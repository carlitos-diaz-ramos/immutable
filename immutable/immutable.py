'''
immutable.py defines a class that forces immutable behaviour.
'''

from collections.abc import Mapping
from typing import Any

from .exceptions import ConstantAttributeError, set_error, del_error


################################################################################
def _setattr(self, attr: str, value: Any) -> Any:
    if self.__frozen:
        raise ConstantAttributeError(set_error(self, attr))
    else:
        return object.__setattr__(self, attr, value)
    
def _delattr(self, attr: str) -> None:
    if self.__frozen:
        raise ConstantAttributeError(del_error(self, attr))
    else:
        object.__delattr__(self, attr)

################################################################################
class ImmutableMeta(type):
    def __new__(
        cls, 
        name: str, 
        bases: tuple[type, ...], 
        namespace: Mapping
    ) -> 'ImmutableMeta':
        new = super().__new__(cls, name, bases, namespace)
        new.__setattr__ = _setattr
        new.__delattr__ = _delattr
        return new

    def __call__(cls, *args: Any, **kwargs: Any) -> 'Immutable':
        instance = cls.__new__(cls, *args, **kwargs)
        if not isinstance(instance, cls):
            return instance
        object.__setattr__(instance, '__frozen', False)
        instance.__init__(*args, **kwargs)
        object.__setattr__(instance, '__frozen', True)
        return instance


################################################################################
class Immutable(metaclass=ImmutableMeta):
    '''
    Immutable(...) is an abstract class that represents immutable content.
    Instance initialization takes place normally in __init__.
    '''
    def cls_name(self) -> str:
        return type(self).__qualname__


class _ImmutableWrapper(Immutable):
    '''Base class for ImmutableProxy.'''
    _instance: Any
    
    def get_type(self) -> type:
        '''
        _ImmutableWrapper.get_type() returns the type of a wrapped object.
        '''
        return type(self._instance)

    def cls_name(self) -> str:
        return f'{Immutable.cls_name(self)}[{self.get_type().__qualname__}]'
        
