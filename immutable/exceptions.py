'''
exceptions.py is a module that defines the exceptions of this package.
'''

from typing import TYPE_CHECKING

if TYPE_CHECKING: # pragma: no cover
    from .immutable import Immutable


class ConstantAttributeError(AttributeError):
    '''
    Exception that is raised when an attribute is changed, created or deleted.
    '''

class ConstantIndexError(LookupError):
    '''
    Exception that is raised when an object's index is changed, created or 
    deleted.
    '''

# class NonPythonTypeError(TypeError):
#     '''
#     Exception that is raised when an immutable proxy is attempted to a type that
#     is not defined in pure Python.
#      '''


def set_error(instance: 'Immutable', attr: str) -> str:
    return _error(instance.cls_name(), attr, 'change')

def del_error(instance: 'Immutable', attr: str) -> str:
    return _error(instance.cls_name(), attr, 'delete')

def _error(cls_name: str, attr: str, action: str) -> str:
    return (
        f"'{cls_name}' object is immutable. "
        f"Cannot {action} attribute '{attr}' after initialization."
    )
