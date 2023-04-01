'''
superpatch.py is a module that defines a replacement for built-in super().
'''

from inspect import currentframe, getmro, ismemberdescriptor
from typing import Iterable, Any, Optional, Union, Final, final

from .immutable import _ImmutableWrapper


###############################################################################
def super_patch(
    type_: Optional[type] = None, 
    obj_or_type: Union[type, object, None] = None, /
) -> '_ClassProxy':
    '''
    super_patch() is a replacement for super() that calculates the superclass 
    of the instance wrapped by a subclass of Immutable.
    Its use is essential in ImmutableProxy.
    '''
    if _called_with_args(type_, obj_or_type):
        return _ClassProxy(getmro(type_), obj_or_type)
    klass, first_arg = _get_class_and_instance()
    if isinstance(first_arg, type) and issubclass(first_arg, klass):
        return _ClassProxy(getmro(klass), None)
    else:
        if isinstance(first_arg, _ImmutableWrapper):
            instance_cls = first_arg.get_type()
        else:
            instance_cls = type(first_arg)
        mro = getmro(instance_cls)
        index = mro.index(klass)
        return _ClassProxy(mro[index:], first_arg)

def _called_with_args(
    type_: Optional[type], 
    obj_or_type: Union[type, object, None]
) -> bool:
    if type_ is not None:
        if obj_or_type is None:
            raise AttributeError(_ONE_ARGUMENT_ERROR)
        return True
    return False

def _get_class_and_instance() -> tuple[type, object]:
    try:
        # Problems with python implementation are detected in except clause
        frame = currentframe().f_back.f_back
        local = frame.f_locals
        args = frame.f_code.co_varnames
        return (local['__class__'], local[args[0]])
    except AttributeError as error:
        raise RuntimeError(_INSPECT_ERROR) from error


_ONE_ARGUMENT_ERROR: Final = "'super' with a single argument not supported."
_INSPECT_ERROR: Final = (
    'This python implementation does not suport frame introspection.'
)


@final
class _ClassProxy():
    '''
    _ClassProxy(mro, instance) is an auxiliary class that is used to get the 
    attributes of super_patch().
    '''
    def __init__(
        self, 
        mro: tuple[type,...], 
        instance: Union[type, object, '_ImmutableWrapper', None],
    ) -> None:
        self._mro = mro
        self._instance = instance

    def __repr__(self) -> str: # pragma: no cover
        mro = object.__getattribute__(self, '_mro')
        instance = object.__getattribute__(self, '_instance')
        return f'_ClassProxy({mro!r}, {instance!r})'

    def __getattribute__(self, attr: str) -> Any:
        mro = object.__getattribute__(self, '_mro')
        instance = object.__getattribute__(self, '_instance')
        attribute = _find_attribute(mro, attr) 
        if instance is None:
            return attribute
        if ismemberdescriptor(attribute):
            # This descriptor seems to check the type for functions written in 
            # C, so we cannot return a function as in the subsequent code; 
            # thus we called __get__ directly on the descriptor.
            return attribute.__get__(instance, None)
        def _method(*args, **kwargs):
            return attribute(instance, *args, **kwargs)
        return _method


def _find_attribute(mro: Iterable[type], attr: str) -> Any:
    '''
    _find_attribute(mro, attr) finds attribute "attr" in the iterable of types 
    "mro".  "mro" is supposed to represent the mro of a class.
    '''
    mro = iter(mro)
    parent = next(mro)
    for cls in mro:
        try:
            return getattr(cls, attr)
        except AttributeError: 
            pass
    else:
        msg = f"Type object '{parent}' has no attribute '{attr}'."
        raise AttributeError(msg)

