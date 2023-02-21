import pytest

from typing import NoReturn, Any

from immutable import ImmutableProxy, DeepImmutableProxy
from immutable import superpatch


###############################################################################
def test_super_with_class_method_bug() -> None:
    class A():
        def make(self) -> int:
            return C.make()
    class B():
        @classmethod
        def make(cls) -> int:
            return 42
    class C(B):
        @classmethod
        def make(cls) -> int:
            return super().make()
    assert A().make() == 42
    assert ImmutableProxy(A()).make() == 42
    
def test_super_with_parameters_in_class_method() -> None:
    class A():
        def make(self) -> int:
            return C.make()
    class B():
        @classmethod
        def make(cls) -> int:
            return 42 # pragma: no cover # dummy code
    class C(B):
        @classmethod
        def make(cls) -> int:
            return super(cls).make() # type: ignore # what we test below
    with pytest.raises(AttributeError):
        A().make()
    with pytest.raises(AttributeError):
        ImmutableProxy(A()).make() == 42
    
def test_super_with_parameters_in_bound_method() -> None:
    class A():
        def make(self) -> int:
            return C().make()
    class B():
        def make(self) -> int:
            return 42
    class C(B):
        def make(self) -> int:
            return super(C, self).make()
    proxy = ImmutableProxy(A())
    assert proxy.make() == 42
    
def test_super_in_bound_method() -> None:
    class A():
        def make(self) -> int:
            return C().make()
    class B():
        def make(self) -> int:
            return 42
    class C(B):
        def make(self) -> int:
            return super().make()
    proxy = ImmutableProxy(A())
    assert proxy.make() == 42

def test_super_with_self_called_differently() -> None:
    class A():
        def make(self) -> int:
            return 42
    class B(A):
        def make(this) -> int:
            return super().make()
    proxy = ImmutableProxy(B())
    assert proxy.make() == 42

def test_super_returning_class_bug() -> None:
    class A():
        def __init__(self) -> None:
            super().__init__()
    class B():
        def do(self) -> A:
            return A()
    assert B().do() is not None
    assert ImmutableProxy(B()).do() is not None
     
def test_frame_error(monkeypatch) -> None:
    def current_frame_fake() -> NoReturn:
        raise AttributeError()
    monkeypatch.setattr(superpatch, 'currentframe', current_frame_fake)
    class A():
        def make(self) -> int:
            return 42 # pragma: no cover # test exception before getting called
    class B(A):
        def make(self) -> int:
            return super().make()
    proxy = ImmutableProxy(B())
    with pytest.raises(RuntimeError):
        proxy.make()    

def test_recursive_getattribute() -> None:
    class A():
        def __getattribute__(self, attr: str) -> Any:
            if attr == 'foo':
                return 'foo'
            return super().__getattribute__(attr)
    assert A().foo == 'foo'
    with pytest.raises(AttributeError):
        A().bar()
    proxy = ImmutableProxy(A())
    assert proxy.foo == 'foo'
    with pytest.raises(AttributeError):
        proxy.bar()

def test_super_with_method_before() -> None:
    class A():
        def do(self) -> int:
            return 42
    class B(A):
        def do(self) -> int:
            self.other()
            return super().do()
        def other(self) -> int:
            return 24
    assert B().do() == 42
    assert ImmutableProxy(B()).do() == 42

def test_super_with_method_in_grandparent() -> None:
    class A():
        def do(self) -> int:
            return 42
    class B(A):
        pass
    class C(B):
        def do(self) -> int:
            return super().do()
    assert C().do() == 42
    assert ImmutableProxy(C()).do() == 42

def test_super_with_multiple_inheritance() -> None:
    class A():
        def do(self) -> int:
            return 42
    class B:
        pass
    class C(B, A):
        def do(self) -> int:
            return super().do()
    assert C().do() == 42
    assert ImmutableProxy(C()).do() == 42

def test_super_method_not_in_ascendants() -> None:
    class A():
        pass
    class B(A):
        def do(self) -> None:
            super().do() # type: ignore # what we test
    with pytest.raises(AttributeError):
        B().do()
    with pytest.raises(AttributeError):
        ImmutableProxy(B()).do()

def test_super_inside_method_not_in_ascendants() -> None:
    class Outer():
        def __init__(self) -> None:
            self.b = B()
    class A():
        pass
    class B(A):
        def do(self) -> None:
            super().do() # type: ignore # what we test
    with pytest.raises(AttributeError):
        Outer().b.do() # type: ignore # what we test
    with pytest.raises(AttributeError):
        DeepImmutableProxy(Outer()).b.do()

