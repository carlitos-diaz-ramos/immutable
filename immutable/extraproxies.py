'''
extraproxies.py is a module that contains several ad-hoc proxies for built-in
classes.
'''

from collections.abc import Callable
from functools import wraps
from typing import Any

from .deep import DeepImmutableProxy


###############################################################################
class BuiltinImmutableProxy(DeepImmutableProxy):
    '''
    BuiltinImmutableProxy(object) is a base class from immutable proxies of
    built-in types.
    '''
    def __init__(self, data: Any) -> None:
        self._data = data

    def __getattr__(self, attr: str) -> Any:
        if attr in type(self)._get_immutable_methods():
            method = getattr(self._data, attr)
            return self._define_builtin_method(method)
        msg = (
            f'Object of type "{type(self).__qualname__}" does not have '
            f'attribute "{attr}".'
        )
        raise AttributeError(msg)

    def __getitem__(self, key: Any) -> Any:
        return DeepImmutableProxy(self._data[key])

    def _define_builtin_method(self, method: Callable) -> Callable:
        @wraps(method)
        def _proxy_method(*args, **kwargs):
            return DeepImmutableProxy(method(*args, **kwargs))
        return _proxy_method        

    @classmethod
    def _get_immutable_methods(cls) -> tuple[str, ...]: # pragma: no cover
        msg = 'Method to be overloaded in derived classes.'
        raise NotImplementedError(msg)


class TupleImmutableProxy(BuiltinImmutableProxy):
    '''
    TupleImmutableProxy(lst) is an immutable proxy for a tuple object.
    '''
    @classmethod
    def _get_immutable_methods(cls) -> tuple[str, ...]:
        return filter(lambda method: not method.startswith('__'), dir(tuple))

class DictImmutableProxy(BuiltinImmutableProxy):
    '''
    DictImmutableProxy(dictionary) is an immutable proxy for a dict object.
    '''
    @classmethod
    def _get_immutable_methods(cls) -> tuple[str, ...]:
        return ('get', 'items', 'keys', 'values')


class ListImmutableProxy(BuiltinImmutableProxy):
    '''
    ListImmutableProxy(lst) is an immutable proxy for a list object.
    '''
    @classmethod
    def _get_immutable_methods(cls) -> tuple[str, ...]:
        return ('index', 'count')

