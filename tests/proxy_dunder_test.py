import pytest

from collections.abc import Iterator

from immutable import ImmutableProxy, ConstantAttributeError


def test_subscript_list() -> None:
    proxy = ImmutableProxy([1, 2, 3])
    assert proxy[1] == 2

def test_str_is_return_as_is() -> None:
    text = '123'
    proxy = ImmutableProxy(text)
    assert proxy == text

def test_subscript_str() -> None:
    proxy = ImmutableProxy('123')
    assert proxy[1] == '2'

def test_subscript_with_slice() -> None:
    proxy = ImmutableProxy('0123456789')
    assert proxy[3:6] == '345'

def test_unsubscriptable_object() -> None:
    proxy = ImmutableProxy(None)
    with pytest.raises(TypeError):
        proxy[1]

def test_nonsubscriptable_custom_object() -> None:
    class A():
        pass
    proxy = ImmutableProxy(A())
    with pytest.raises(TypeError):
        proxy[1]

def test_list_proxy_is_custom() -> None:
    proxy = ImmutableProxy([1, 2, 3])
    assert isinstance(proxy, ImmutableProxy)
    assert type(proxy) != ImmutableProxy

def test_cannot_assign_item() -> None:
    proxy = ImmutableProxy([1, 2, 3])
    with pytest.raises(TypeError):
        proxy[1] = 42

def test_list_proxy_index() -> None:
    proxy = ImmutableProxy([1, 2, 3])
    assert proxy.index(2) == 1

def test_list_cannot_be_appended() -> None:
    proxy = ImmutableProxy([1, 2, 3])
    with pytest.raises(AttributeError):
        proxy.append(4)

def test_cannot_assign_slice() -> None:
    proxy = ImmutableProxy([1, 2, 3, 4, 5])
    with pytest.raises(TypeError):
        proxy[1:3] = (42, 43)

def test_iter_subscriptable() -> None:
    proxy = ImmutableProxy([1, 2, 3])
    assert list(proxy) == [1, 2, 3]

def test_iter_nonsubscriptable() -> None:
    class MyIterable:
        def __iter__(self) -> Iterator[int]:
            yield 1
            yield 2
            yield 3
    assert list(MyIterable()) == [1, 2, 3]
    proxy = ImmutableProxy(MyIterable())
    assert list(proxy) == [1, 2, 3]

def test_iter_noniterable() -> None:
    proxy = ImmutableProxy(None)
    with pytest.raises(TypeError):
        iter(proxy)

def test_iter_custom_noniterable() -> None:
    class NotIterable():
        pass
    proxy = ImmutableProxy(NotIterable())
    with pytest.raises(TypeError):
        iter(proxy)       

def test_len_str() -> None:
    proxy = ImmutableProxy('123')
    assert len(proxy) == 3

def test_len_custom() -> None:
    class MyIterable:
        def __iter__(self) -> Iterator[int]: # pragma: no cover # dummy code
            yield 1
            yield 2
            yield 3
    proxy = ImmutableProxy(MyIterable())
    with pytest.raises(TypeError):
        len(proxy)

