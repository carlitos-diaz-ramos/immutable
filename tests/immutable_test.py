import pytest

from typing import Union

from immutable import Immutable, ConstantAttributeError


class A(Immutable):
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    def get_x(self) -> int:
        return self.x
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__
    @staticmethod
    def get_something() -> str:
        return 'something'

class B(A):
    def __init__(self, x: int, y: int, z: int) -> None:
        super().__init__(x, y)
        self.z = z
    def get_x(self) -> int:
        x = super().get_x()
        return x
    @classmethod
    def get_name(cls) -> str:
        return super().get_name()
    @staticmethod
    def get_something() -> str:
        return 'something'

A_or_B = Union[A, B]

@pytest.fixture(params=[A(0, 1), B(0, 1, 2)], ids=['A', 'B'])
def obj(request) -> Immutable:
    return request.param


def test_access_attributes_normally(obj: A_or_B) -> None:
    assert (obj.x, obj.y) == (0, 1)

def test_cannot_change_attribute(obj: A_or_B) -> None:
    with pytest.raises(ConstantAttributeError):
        obj.x = 2

def test_cannot_delete_attribute(obj: A_or_B) -> None:
    with pytest.raises(ConstantAttributeError):
        del obj.y

def test_cannot_add_attribute(obj: A_or_B) -> None:
    with pytest.raises(ConstantAttributeError):
        obj.t = 'value' # type: ignore

def test_can_delete_attribute_in__init__() -> None:
    class Other(Immutable):
        def __init__(self, x: int) -> None:
            self.x = x
            del self.x
    obj = Other(42)
    with pytest.raises(AttributeError):
        obj.x

def test_no__init__defined() -> None:
    class A(Immutable):
        pass
    a = A()
    with pytest.raises(AttributeError):
        a.x # type: ignore

def test_access_method_normally(obj: A_or_B) -> None:
    assert obj.get_x() == 0

def test_access_class_method_normally(obj: A_or_B) -> None:
    assert obj.get_name() in {'A', 'B'}

def test_access_static_method_normally(obj: A_or_B) -> None:
    assert obj.get_something() == 'something'
