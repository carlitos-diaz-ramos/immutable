'''
checktype.py defines utility functions to check the type of an object wrapped
by ImmutableProxy.
'''

from typing import Union

from .proxy import ImmutableProxy


###############################################################################
def get_type(obj: object, /) -> type:
    '''
    get_type(obj) returns the type of object if it is not wrapped by
    ImmutableProxy;  if it is wrapped by ImmutableProxy, then the wrapped type
    is returned.
    '''
    if isinstance(obj, ImmutableProxy):
        return obj.get_type()
    return type(obj)


def is_instance(
    obj: object, cls_or_tuple: Union[type, tuple[type,...]]
) -> bool:
    return issubclass(get_type(obj), cls_or_tuple)
