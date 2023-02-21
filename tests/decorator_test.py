import pytest

from typing import Union

from immutable import immutable, ConstantAttributeError

@immutable
class A():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    def get_x(self) -> int:
        return self.x

@immutable
class B(A):
    def __init__(self, x: int, y: int, z: int) -> None:
        super().__init__(x, y)
        self.z = z
    def get_x(self) -> int:
        x = super().get_x()
        return x

class C():
    def __init__(self, x: int) -> None:
        self.x = x
    def get_x(self) -> int:
        return self.x

@immutable
class D(C):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x)
        self.y = y
    def get_x(self) -> int:
        x = super().get_x()
        return x


Fixture = Union[A, B, D]

@pytest.fixture(params=[A(0, 1), B(0, 1, 2), D(0, 1)], ids=['A', 'B', 'D'])
def obj(request) -> Fixture:
    return request.param


def test_access_attributes_normally(obj: Fixture) -> None:
    assert (obj.x, obj.y) == (0, 1)

def test_access_new_attribute_normally() -> None:
    obj = B(0, 1, 2)
    assert (obj.x, obj.y, obj.z) == (0, 1, 2)

def test_cannot_change_attribute(obj: Fixture) -> None:
    with pytest.raises(ConstantAttributeError):
        obj.x = 2 # type: ignore 

def test_cannot_delete_attribute(obj: Fixture) -> None:
    with pytest.raises(ConstantAttributeError):
        del obj.y # type: ignore

def test_cannot_add_attribute(obj: Fixture) -> None:
    with pytest.raises(ConstantAttributeError):
        obj.t = 'value' # type: ignore

def test_can_access_method_normally(obj: Fixture) -> None:
    assert obj.get_x() == 0

def test_can_delete_attribute_in__init__() -> None:
    @immutable
    class Other():
        def __init__(self, x):
            self.x = x
            del self.x
    obj = Other(42)
    with pytest.raises(AttributeError):
        obj.x # type: ignore # what we test
