'''
proxy.py is a module that defines a proxy for an object that whose attributes
cannot be modified.
'''

import builtins
from copy import copy, deepcopy
from functools import wraps
from types import (
    FunctionType, BuiltinFunctionType, MethodType, BuiltinMethodType
)
from collections.abc import Callable
import reprlib
from typing import Any, Iterator, TypeVar, Generic, ClassVar, Union

from .immutable import _ImmutableWrapper
from .superpatch import super_patch


T = TypeVar('T')


################################################################################
class ImmutableProxy(_ImmutableWrapper, Generic[T]):
    '''
    ImmutableProxy(instance) is a class wrapper that creates a proxy for 
    "instance" whose attributes cannot be modified.
    However, the instance's attributes might still be mutable.
    '''
    _instance: T

    _BUILTIN_IMMUTABLE: ClassVar[type] = []
    _REGISTERED_PROXIES: ClassVar[dict[type, type['ImmutableProxy']]] = {}

    def __new__(cls, wrapped: T, /) -> Union['ImmutableProxy', T]:
        if cls._is_already_immutable(wrapped):
            return wrapped
        obj = object.__new__(cls._get_class(wrapped))
        cls._set_instance(wrapped, obj)
        return obj

    @classmethod
    def _is_already_immutable(cls, wrapped: T) -> bool:
        return (
            isinstance(wrapped, tuple(cls._BUILTIN_IMMUTABLE)) or 
            isinstance(wrapped, cls)
        )

    @classmethod
    def _get_class(cls, wrapped: T) -> type['ImmutableProxy']:
        if isinstance(wrapped, tuple(cls._REGISTERED_PROXIES)):
            return cls._REGISTERED_PROXIES[type(wrapped)]
        return cls

    @classmethod
    def _set_instance(cls, wrapped: T, new_object: 'ImmutableProxy') -> None:
        if issubclass(cls, type(wrapped)):
            object.__setattr__(new_object, '_instance', wrapped._instance)
        else:
            object.__setattr__(new_object, '_instance', wrapped)

    def __repr__(self) -> str:
        custom_repr = reprlib.Repr()
        custom_repr.maxother = 50
        return f'{type(self).__qualname__}({custom_repr.repr(self._instance)})'

    def __str__(self) -> str:
        '''
        The str of an ImmutableProxy is the str of the wrapped object.
        '''
        return str(self._instance)

    def __bool__(self) -> bool:
        return bool(self._instance)

    def __eq__(self, other: Any) -> bool:
        return other == self._instance

    def __copy__(self) -> T:
        '''
        Copying an ImmutableProxy returns a copy of the wrapped object.
        '''
        return copy(self._instance)

    def __deepcopy__(self, memo: dict) -> T:
        '''
        Deepcopying an ImmutableProxy returns a deep copy of the wrapped 
        object.
        '''
        return deepcopy(self._instance, memo)

    def __getitem__(self, key: Any) -> Any:
        return self._instance[key]

    def __iter__(self) -> Iterator:
        return iter(self._instance)

    def __len__(self) -> int:
        return len(self._instance)

    def __format__(self, format_spec: str) -> str:
        return self._instance.__format__(format_spec)

    def __getattr__(self, attr: str) -> Any:
        if self._is_bound_method(attr):
            return self._define_method(attr)
        elif self._is_class_method(attr):
            return self._define_class_method(attr)
        elif self._is_static_method(attr):
            return self._define_class_method(attr)
        else:
            return getattr(self._instance, attr)

    def _is_bound_method(self, attr: str) -> bool:
        attribute = getattr(self._instance, attr)
        if isinstance(attribute, (MethodType, BuiltinMethodType)):
            method = getattr(type(self._instance), attr)
            return not isinstance(method, (MethodType, BuiltinMethodType))
        return False

    def _is_class_method(self, attr: str) -> bool:
        attribute = getattr(self._instance, attr)
        if isinstance(attribute, (MethodType, BuiltinMethodType)):
            method = getattr(type(self._instance), attr)
            return isinstance(method, (MethodType, BuiltinMethodType))
        return False

    def _is_static_method(self, attr: str) -> bool:
        attribute = getattr(self._instance, attr)
        return isinstance(attribute, (FunctionType, BuiltinFunctionType))

    def _define_class_method(self, attr: str) -> Callable:
        method = getattr(type(self._instance), attr)
        @wraps(method)
        def _proxy_method(*args, **kwargs):
            return method(*args, **kwargs)
        return _proxy_method

    def _define_method(self, attr: str) -> Callable:
        method = getattr(type(self._instance), attr)
        @wraps(method)
        def _proxy_method(*args, **kwargs):
            # Pass self, *not self._instance*, to prevent mutation in methods.
            # This requires a modification of super().
            old_super = super
            try:
                builtins.super = super_patch
                result = method(self, *args, **kwargs)
            finally:
                builtins.super = old_super
            return result
        return _proxy_method        

    def get_type(self) -> type[T]:
        return _ImmutableWrapper.get_type(self)

    @classmethod
    def register_immutable(cls, immutable_type: type) -> None:
        '''
        ImmutableProxy.register_immutable(type) registers "type" to be already
        immutable.
        '''
        cls._BUILTIN_IMMUTABLE.append(immutable_type)

    @classmethod
    def get_registered_immutable(cls) -> tuple[type,...]:
        '''
        ImmutableProxy.get_registered_immutable() returns a tuple with the
        immutable types registered so far.
        '''
        return tuple(cls._BUILTIN_IMMUTABLE)

    @classmethod
    def register_proxy(
        cls, 
        real_type: type, 
        proxy_type: type['ImmutableProxy']
    ) -> None:
        cls._REGISTERED_PROXIES |= {real_type: proxy_type}

    @classmethod
    def get_registered_proxies(cls) -> tuple[type,...]:
        '''
        ImmutableProxy.get_registered_proxies() returns a tuple with the
        proxies registered for types that are not pure Python.
        '''
        return tuple(cls._REGISTERED_PROXIES)
