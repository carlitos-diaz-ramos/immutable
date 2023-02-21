import pytest

from copy import copy, deepcopy

from immutable import ImmutableProxy, ConstantAttributeError


class A:
    'Dummy class for testing.'
    def __init__(self, x: int, y: int = 0) -> None:
        self.x = x
        self.y = y
    def __repr__(self) -> str:
        return f'{type(self).__qualname__}({self.x!r}, {self.y!r})'
    def __str__(self) -> str:
        return f'({self.x!r}, {self.y!r})'
    def __format__(self, format_spec: str) -> str:
        assert format_spec == '%x'
        return str(self.x)
    def __bool__(self) -> bool:
        return bool(self.x)
    def set_x(self, x: int) -> None:
        'Sets x.'
        self.x = x
    def get_x(self) -> int:
        return self.x
    @property
    def y(self) -> int:
        return self.__dict__['y']
    @y.setter
    def y(self, value: int) -> None:
        self.__dict__['y'] = value
    @classmethod
    def get_name(cls) -> str:
        'Docstring'
        return cls.__name__
    @staticmethod
    def get_something() -> str:
        return 'something'

class B(A):
    def __init__(self, x: int, y: int = 0, z: int = -1) -> None:
        super().__init__(x, y)
        self.z = z
    def __repr__(self) -> str:
        return f'{type(self).__qualname__}({self.x!r}, {self.y!r}, {self.z!r})'
    def set_x(self, x: int) -> None:
        'Sets x in child.'
        return super().set_x(x)
    def get_x(self) -> int:
        return super().get_x()
    @classmethod
    def get_name(cls) -> str:
        'Child Docstring'
        return super().get_name()
    @staticmethod
    def get_something() -> str:
        return 'something'


ImmutableA = ImmutableProxy[A]
ImmutableB = ImmutableProxy[B]


################################################################################
class TestProxy():
    @pytest.fixture
    def obj(self) -> ImmutableA:
        return ImmutableProxy(A(3))

    def test_repr(self, obj: ImmutableA) -> None:
        assert repr(obj) == 'ImmutableProxy(A(3, 0))'

    def test_str(self, obj: ImmutableA) -> None:
        assert str(obj) == '(3, 0)'

    def test_format(self, obj: ImmutableA) -> None:
        assert f'{obj:%x}' == '3'

    def test_bool_true(self, obj: ImmutableA) -> None:
        assert obj

    def test_bool_false(self) -> None:
        obj = ImmutableProxy(A(0))
        assert not obj

    def test_is_idempotent(self, obj: ImmutableA) -> None:
        assert repr(ImmutableProxy(obj)) == repr(obj)

    def test_proxy_of_hashable_returns_hasable(self) -> None:
        text = 'text'
        assert ImmutableProxy(text) is text

    def test_proxy_of_hashable_container_returns_special_proxy(self) -> None:
        proxy = ImmutableProxy(('text', ('mutable',)))
        assert isinstance(proxy, ImmutableProxy)
        assert type(proxy) != ImmutableProxy

    def test_proxy_of_nonhashable_returns_proxy(self) -> None:
        mutable = ('text', ['mutable'])
        proxy = ImmutableProxy(mutable) 
        assert proxy is not mutable
        assert isinstance(proxy, ImmutableProxy)

    def test_equal_if_underlying_equal(self) -> None:
        obj = A(3)
        assert ImmutableProxy(obj) == obj
        assert obj == ImmutableProxy(obj)

    def test_different_if_underlying_different(self) -> None:
        obj = A(3)
        other = ImmutableProxy(A(4))
        assert obj != other
        assert other != obj

    def test_equal_if_underlying_idempotent(self, obj: ImmutableA) -> None:
        assert ImmutableProxy(obj) == obj
        assert obj == ImmutableProxy(obj)

    def test_different_if_underlying_idempotent_different(
        self, obj: ImmutableA
    ) -> None:
        other = ImmutableProxy(A(4))
        assert obj != other
        assert other != obj

    def test_get_type(self, obj: ImmutableA) -> None:
        assert obj.get_type() == A

    def test_can_access_attribute_normally(self, obj: ImmutableA) -> None:
        assert obj.x == 3

    def test_cannot_change_attribute(self, obj: ImmutableA) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.x = 2 # type: ignore

    def test_error_when_attribute_changed(self, obj: ImmutableA) -> None:
        with pytest.raises(ConstantAttributeError) as excinfo:
            obj.x = 2 # type: ignore
        assert '[A]' in str(excinfo.value)

    def test_cannot_delete_attribute(self, obj: ImmutableA) -> None:
        with pytest.raises(ConstantAttributeError):
            del obj.x

    def test_error_when_attribute_deleted(self, obj: ImmutableA) -> None:
        with pytest.raises(ConstantAttributeError) as excinfo:
            del obj.x  # type: ignore
        assert '[A]' in str(excinfo.value)

    def test_cannot_add_attribute(self, obj: ImmutableA) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.z = 0 # type: ignore

    def test_cannot_change_attribute_indirectly(self, obj: ImmutableA) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.set_x(2)

    def test_underlying_object_can_be_changed(self) -> None:
        original = A(3)
        proxy = ImmutableProxy(original)
        original.x = 5
        assert proxy.x == 5

    def test_access_method_normally(self, obj: ImmutableA) -> None:
        assert obj.get_x() == 3

    def test_method_docstring(self, obj: ImmutableA) -> None:
        assert obj.set_x.__doc__ == 'Sets x.'

    def test_method_annotations(self, obj: ImmutableA) -> None:
        assert obj.set_x.__annotations__ == {'x': int, 'return': None}

    def test_can_access_property_normally(self, obj: ImmutableA) -> None:
        assert obj.y == 0

    def test_cannot_change_property(self, obj: ImmutableA) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.y = 5 # type: ignore

    def test_cannot_delete_property(self, obj: ImmutableA) -> None:
        with pytest.raises(ConstantAttributeError):
            del obj.y

    def test_can_access_class_method(self, obj: ImmutableA) -> None:
        assert obj.get_name() == 'A'

    def test_class_method_docstring(self, obj: ImmutableA) -> None:
        assert obj.get_name.__doc__ == 'Docstring'

    def test_class_method_annotations(self, obj: ImmutableA) -> None:
        assert obj.get_name.__annotations__ == {'return': str}

    def test_can_access_static_method(self, obj: ImmutableA) -> None:
        assert obj.get_something() == 'something'

    def test_underlying_object_properties_can_be_changed(self) -> None:
        original = A(3)
        proxy = ImmutableProxy(original)
        original.y = 5
        assert proxy.y == 5

    def test_copy(self, obj: ImmutableA) -> None:
        other = copy(obj)
        assert (other.x, other.y) == (obj.x, obj.y)

    def test_copy_type(self, obj: ImmutableA) -> None:
        other = copy(obj)
        assert isinstance(other, A)

    def test_deepcopy(self, obj: ImmutableA) -> None:
        other = deepcopy(obj)
        assert (other.x, other.y) == (obj.x, obj.y)

    def test_deep_copy_type(self, obj: ImmutableA) -> None:
        other = deepcopy(obj)
        assert isinstance(other, A)


class TestProxyOfInheritedClass():
    @pytest.fixture
    def obj(self) -> ImmutableA:
        return ImmutableProxy(B(3, 2, 1))

    def test_repr(self, obj: ImmutableB) -> None:
        assert repr(obj) == 'ImmutableProxy(B(3, 2, 1))'

    def test_can_access_attribute_normally(self, obj: ImmutableB) -> None:
        assert obj.x == 3

    def test_cannot_change_attribute(self, obj: ImmutableB) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.x = 2 # type: ignore

    def test_cannot_delete_attribute(self, obj: ImmutableB) -> None:
        with pytest.raises(ConstantAttributeError):
            del obj.x

    def test_can_access_new_attribute_normally(self, obj: ImmutableB) -> None:
        assert obj.z == 1

    def test_cannot_change_new_attribute(self, obj: ImmutableB) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.z = 2 # type: ignore

    def test_cannot_delete_new_attribute(self, obj: ImmutableB) -> None:
        with pytest.raises(ConstantAttributeError):
            del obj.z

    def test_cannot_add_attribute(self, obj: ImmutableB) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.t = 0 # type: ignore

    def test_cannot_change_attribute_indirectly(self, obj: ImmutableB) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.set_x(2)

    def test_underlying_object_can_be_changed(self) -> None:
        original = B(3)
        proxy = ImmutableProxy(original)
        original.z = 5
        assert proxy.z == 5

    def test_access_method_normally(self, obj: ImmutableB) -> None:
        assert obj.get_x() == 3

    def test_method_docstring(self, obj: ImmutableB) -> None:
        assert obj.set_x.__doc__ == 'Sets x in child.'

    def test_method_annotations(self, obj: ImmutableB) -> None:
        assert obj.set_x.__annotations__ == {'x': int, 'return': None}

    def test_can_access_class_method(self, obj: ImmutableB) -> None:
        assert obj.get_name() == 'B'

    def test_class_method_docstring(self, obj: ImmutableB) -> None:
        assert obj.get_name.__doc__ == 'Child Docstring'

    def test_class_method_annotations(self, obj: ImmutableB) -> None:
        assert obj.get_name.__annotations__ == {'return': str}

    def test_can_access_static_method(self, obj: ImmutableB) -> None:
        assert obj.get_something() == 'something'

    def test_can_access_property_normally(self, obj: ImmutableB) -> None:
        assert obj.y == 2

    def test_cannot_change_property(self, obj: ImmutableB) -> None:
        with pytest.raises(ConstantAttributeError):
            obj.y = 5 # type: ignore

    def test_cannot_delete_property(self, obj: ImmutableB) -> None:
        with pytest.raises(ConstantAttributeError):
            del obj.y

    def test_underlying_object_properties_can_be_changed(self) -> None:
        original = B(3)
        proxy = ImmutableProxy(original)
        original.y = 5
        assert proxy.y == 5

    def test_copy(self, obj: ImmutableB) -> None:
        other = copy(obj)
        assert (other.x, other.y, other.z) == (obj.x, obj.y, obj.z)

    def test_copy_type(self, obj: ImmutableB) -> None:
        other = copy(obj)
        assert isinstance(other, B)

    def test_deepcopy(self, obj: ImmutableA) -> None:
        other = deepcopy(obj)
        assert (other.x, other.y, other.z) == (obj.x, obj.y, obj.z)

    def test_deep_copy_type(self, obj: ImmutableB) -> None:
        other = deepcopy(obj)
        assert isinstance(other, B)

