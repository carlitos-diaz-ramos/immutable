import pytest

from copy import copy, deepcopy

from immutable.deep import DeepImmutableProxy as DIP, ImmutableProxy
from immutable.exceptions import ConstantAttributeError


class Inner:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    def __repr__(self) -> str:
        return f'{type(self).__qualname__}({self.x!r}, {self.y!r})'
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

class Outer:
    def __init__(self, a: Inner, b: Inner) -> None:
        self.a = a
        self.b = b
    def __repr__(self) -> str:
        return f'{type(self).__qualname__}({self.a!r}, {self.b!r})'
    def set_a(self, a: Inner) -> None:
        'Sets a.'
        self.a = a
    def get_a(self) -> Inner:
        return self.a
    @property
    def b(self) -> Inner:
        return self.__dict__['b']
    @b.setter
    def b(self, value: Inner) -> None:
        self.__dict__['b'] = value
    @classmethod
    def get_name(cls) -> str:
        'Another Docstring'
        return cls.__name__
    @staticmethod
    def get_something() -> str:
        return 'another something'

ImmutableInner = DIP[Inner]
ImmutableOuter = DIP[Outer]


################################################################################
class TestProxy():
    @pytest.fixture
    def obj(self) -> ImmutableOuter:
        return DIP(Outer(Inner(1, 2), Inner(3, 4)))
    
    class TestEquallity():
        def test_repr(self, obj: ImmutableOuter) -> None:
            expected = 'DeepImmutableProxy(Outer(Inner(1, 2), Inner(3, 4)))'
            assert repr(obj) == expected

        def test_is_idempotent(self, obj: ImmutableOuter) -> None:
            deep_proxy: DIP = DIP(obj)
            assert repr(deep_proxy) == repr(obj)
            assert deep_proxy is obj

        def test_shallow_cannot_override_deep_proxy(
            self, obj: ImmutableOuter
        ) -> None:
            shallow_proxy = ImmutableProxy(obj)
            assert repr(shallow_proxy) == repr(obj)
            assert shallow_proxy is obj

        def test_deep_overrides_shallow_proxy(self) -> None:
            shallow_proxy = ImmutableProxy(Outer(Inner(1, 2), Inner(3, 4)))
            deep_proxy: DIP = DIP(shallow_proxy)
            expected = 'DeepImmutableProxy(Outer(Inner(1, 2), Inner(3, 4)))'
            assert repr(deep_proxy) == expected
            assert deep_proxy is not shallow_proxy

        def test_equal_if_underlying_equal(self) -> None:
            obj = Outer(Inner(1, 2), Inner(3, 4))
            assert DIP(obj) == obj
            assert obj == DIP(obj)

        def test_different_if_underlying_different(self) -> None:
            obj = Outer(Inner(1, 2), Inner(3, 4))
            inside = Outer(Inner(11, 12), Inner(13, 14))
            other: DIP = DIP(inside)
            assert obj != other
            assert other != obj

        def test_equal_if_underlying_equal_idempotent(
            self, obj: ImmutableOuter
        ) -> None:
            assert DIP(obj) == obj
            assert obj == DIP(obj)

        def test_different_if_underlying_different_idempotent(
            self, obj: ImmutableOuter
        ) -> None:
            other: ImmutableOuter = DIP(
                Outer(Inner(11, 12), 
                Inner(13, 14))
            )
            assert obj != other
            assert other != obj

    class TestAttributeAccess():
        def test_can_access_attribute_normally(
            self, obj: ImmutableOuter
        ) -> None:
            assert obj.a.x == 1

        def test_cannot_change_attribute(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.a = 2 # type: ignore # what we test

        def test_cannot_change_inner_attribute(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.a.x = 2

        def test_cannot_delete_attribute(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                del obj.a # type: ignore # what we test

        def test_cannot_delete_inner_attribute(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                del obj.a.x

        def test_cannot_add_attribute(self, obj: ImmutableOuter) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.z = 0 # type: ignore

        def test_cannot_add_inner_attribute(self, obj: ImmutableOuter) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.b.z = 0

        def test_getattr_produces_bug_solved(
            self, obj: ImmutableOuter
        ) -> None:
            from immutable import Immutable
            with pytest.raises(ConstantAttributeError):
                obj.set_a(2)
            class Other(Immutable):
                'The bug arised after creating another Immutable subclass.'

        def test_cannot_change_attribute_indirectly(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.set_a(2)

        def test_cannot_change_inner_attribute_indirectly(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.a.set_x(2)

        def test_underlying_object_can_be_changed(self) -> None:
            original = Outer(Inner(1, 2), Inner(3, 4))
            proxy: ImmutableOuter = DIP(original)
            original.a = Inner(11, 12)
            assert proxy.a.x == 11

        def test_inner_underlying_object_can_be_changed(self) -> None:
            original = Outer(Inner(1, 2), Inner(3, 4))
            proxy: ImmutableOuter = DIP(original)
            original.a.x = 11
            assert proxy.a.x == 11

        def test_access_method_normally(self, obj: ImmutableOuter) -> None:
            assert obj.get_a().y == 2

        def test_access_inner_method_normally(
            self, obj: ImmutableOuter
        ) -> None:
            assert obj.get_a().get_x() == 1

        def test_access_method_normally_but_cannot_modify_result(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.get_a().set_x(12)

        def test_method_docstring(self, obj: ImmutableOuter) -> None:
            assert obj.set_a.__doc__ == 'Sets a.'

        def test_inner_method_docstring(self, obj: ImmutableOuter) -> None:
            assert obj.a.set_x.__doc__ == 'Sets x.'

        def test_method_annotations(self, obj: ImmutableOuter) -> None:
            assert obj.set_a.__annotations__ == {'a': Inner, 'return': None}

        def test_inner_method_annotations(self, obj: ImmutableOuter) -> None:
            assert obj.a.set_x.__annotations__ == {'x': int, 'return': None}

        def test_can_access_property_normally(
            self, obj: ImmutableOuter
        ) -> None:
            assert obj.b.y == 4

        def test_cannot_change_property(self, obj: ImmutableOuter) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.b = 5 # type: ignore # what we test

        def test_cannot_change_inner_property(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                obj.b.y = 5

        def test_cannot_delete_property(self, obj: ImmutableOuter) -> None:
            with pytest.raises(ConstantAttributeError):
                del obj.b # type: ignore # what we test

        def test_cannot_delete_inner_property(
            self, obj: ImmutableOuter
        ) -> None:
            with pytest.raises(ConstantAttributeError):
                del obj.b.y

        def test_can_access_class_method(self, obj: ImmutableOuter) -> None:
            assert obj.get_name() == 'Outer'

        def test_can_access_inner_class_method(
            self, obj: ImmutableOuter
        ) -> None:
            assert obj.get_a().get_name() == 'Inner'

        def test_can_access_inner_class_method_through_class(
            self, obj: ImmutableOuter
        ) -> None:
            assert type(copy(obj.get_a())).get_name() == 'Inner'

        def test_class_method_docstring(self, obj: ImmutableOuter) -> None:
            assert obj.get_name.__doc__ == 'Another Docstring'

        def test_inner_class_method_docstring(self, obj: ImmutableOuter) -> None:
            assert obj.get_a().get_name.__doc__ == 'Docstring'

        def test_class_method_annotations(self, obj: ImmutableOuter) -> None:
            assert obj.get_name.__annotations__ == {'return': str}

        def test_inner_class_method_annotations(self, obj: ImmutableOuter) -> None:
            assert obj.get_a().get_name.__annotations__ == {'return': str}

        def test_can_access_static_method(self, obj: ImmutableOuter) -> None:
            assert obj.get_something() == 'another something'

        def test_can_access_inner_static_method(
            self, obj: ImmutableOuter
        ) -> None:
            assert obj.get_a().get_something() == 'something'

        def test_can_access_inner_static_method_through_class(
            self, obj: ImmutableOuter
        ) -> None:
            assert type(copy(obj.get_a())).get_something() == 'something'

        def test_underlying_object_properties_can_be_changed(self) -> None:
            original = Outer(Inner(1, 2), Inner(3, 4))
            proxy: ImmutableOuter = DIP(original)
            original.b = Inner(13, 14)
            assert proxy.b.y == 14

        def test_can_change_underlying_inner_object_properties(self) -> None:
            original = Outer(Inner(1, 2), Inner(3, 4))
            proxy: ImmutableOuter = DIP(original)
            original.b.y = 14
            assert proxy.b.y == 14

    class TestCopy():
        def test_copy(self, obj: ImmutableOuter) -> None:
            other = copy(obj)
            result = (other.a.x, other.a.y, other.b.x, other.b.y)
            expected = (obj.a.x, obj.a.y, obj.b.x, obj.b.y)
            assert result == expected

        def test_copy_type(self, obj: ImmutableOuter) -> None:
            other = copy(obj)
            assert isinstance(other, Outer)

        def test_copy_inner_type(self, obj: ImmutableOuter) -> None:
            other = copy(obj)
            assert isinstance(other.a, Inner)

        def test_copy_identity(self, obj: ImmutableOuter) -> None:
            one = copy(obj)
            two = copy(obj)
            assert one is not two

        def test_copy_inner_identity(self, obj: ImmutableOuter) -> None:
            one = copy(obj)
            two = copy(obj)
            assert one.a is two.a

        def test_deepcopy(self, obj: ImmutableOuter) -> None:
            other = deepcopy(obj)
            result = (other.a.x, other.a.y, other.b.x, other.b.y)
            expected = (obj.a.x, obj.a.y, obj.b.x, obj.b.y)
            assert result == expected

        def test_deepcopy_type(self, obj: ImmutableOuter) -> None:
            other = deepcopy(obj)
            assert isinstance(other, Outer)

        def test_deepcopy_inner_type(self, obj: ImmutableOuter) -> None:
            other = deepcopy(obj)
            assert isinstance(other.a, Inner)

        def test_deepcopy_identity(self, obj: ImmutableOuter) -> None:
            one = deepcopy(obj)
            two = deepcopy(obj)
            assert one is not two

        def test_deepcopy_inner_identity(self, obj: ImmutableOuter) -> None:
            one = deepcopy(obj)
            two = deepcopy(obj)
            assert one.a is not two.a


def test_cannot_be_modified_if_delegated() -> None:
    class Main():
        def __init__(self, x: int) -> None:
            self.x = x
            self.delegate = Modifier(self)
    class Modifier():
        def __init__(self, obj: Main) -> None:
            self.back = obj
        def reset(self, x: int) -> None:
            self.back.x = x
    obj = Main(3)
    obj.delegate.back.x = 5
    assert obj.delegate.back.x == 5
    proxy: DIP[Main] = DIP(Main(3))
    with pytest.raises(ConstantAttributeError):
        proxy.delegate.back.x = 5
    with pytest.raises(ConstantAttributeError):
        proxy.delegate.reset(5)

def test_super_for_unrelated_object() -> None:
    class Main():
        def __init__(self, x: int) -> None:
            self.x = x
        def do(self) -> int:
            return Other(self.x).make()
    class Base():
        def __init__(self, x: int) -> None:
            self.x = x
        def make(self) -> int:
            if not isinstance(self, Base):
                raise TypeError(f'"{self}" is not of type "Base".')
            return self.x
    class Other(Base):
        def make(self) -> int:
            return 2*super().make()
    obj = Main(42)
    assert obj.do() == 84
    proxy: DIP[Main] = DIP(Main(42))
    assert proxy.do() == 84


###############################################################################
class Descriptor():
    def __set__(self, instance: 'Example', value: int) -> None:
        instance.__dict__['x'] = value
    def __get__(self, instance: 'Example', owner) -> int:
        return instance.__dict__['x']

class Example():
    x = Descriptor()
    def __init__(self, x: int) -> None:
        self.x = x

class Derived(Example):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x)
        self.y = y

class Other():
    def make(self) -> int:
        result = Derived(4, 2).x
        if not isinstance(result, int):
            raise TypeError(f'"{result}" is not of type "int".')
        return result


def test_super_with_descriptor() -> None:
    example = Example(42)
    assert example.x == 42
    proxy: DIP[Example] = DIP(Example(42))
    assert proxy.x == 42

def test_super_with_descriptor_from_other_object() -> None:
    other = Other()
    assert other.make() == 4
    proxy: DIP[Example] = DIP(Other())
    assert proxy.make() == 4

    