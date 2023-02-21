'''
deep.py is a module that defines a class that acts as an immutable proxy of its
content and its attributes recurrently.
'''

from typing import Any, TypeVar, ClassVar, Generic

from .proxy import ImmutableProxy

T = TypeVar('T')


###############################################################################
class DeepImmutableProxy(ImmutableProxy, Generic[T]):
    '''
    DeepImmutableProxy(instance) is a wrapper around instance whose attributes
    at all levels cannot be mutated.
    '''
    def __getattr__(self, attr: str) -> Any:
        attribute = ImmutableProxy.__getattr__(self, attr)
        if callable(getattr(self._instance, attr)):
            return attribute
        return type(self)(attribute)

    def __getitem__(self, key: Any) -> Any:
        return type(self)(self._instance[key])

