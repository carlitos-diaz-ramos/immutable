'''
decorator.py defines a decorator that transforms a class into immutable.
'''

from .immutable import ImmutableMeta


###############################################################################
def _cls_name(self) -> str:
    return type(self).__qualname__


def immutable(cls: type):
    '''
    immutable(cls) is a class decorator that makes the decorated class 
    immutable.
    '''
    return ImmutableMeta(cls.__name__, (cls,), {'cls_name': _cls_name})
