import pytest

from datetime import date
from pathlib import Path
import re
from types import ModuleType

from immutable import DeepImmutableProxy as DIP, ConstantAttributeError


class Outer():
    def __init__(self, mapping: dict, lst: list) -> None:
        self.mapping = dict(mapping)
        self.lst = list(lst)
    def __repr__(self) -> str:
        return f'{type(self).__qualname__}({self.mapping!r}, {self.lst!r})'

class Inner():
    def __init__(self, x: int) -> None:
        self.x = x
    def __repr__(self) -> str:
        return f'{type(self).__qualname__}({self.x!r})'


ImmutableOuter = DIP[Outer]

@pytest.fixture
def deep_proxy() -> ImmutableOuter:
    return DIP(Outer({'a': Inner(1)}, [Inner(2), Inner(3)]))


def test_get_registered_immutable() -> None:
    some_already_registered = {int, float, complex, str, bytes, type(None)}
    registered = set(DIP.get_registered_immutable())
    assert some_already_registered <= registered

def test_get_registered_proxies() -> None:
    some_already_registered = {tuple, list, dict}
    registered = set(DIP.get_registered_proxies())
    assert some_already_registered <= registered

def test_None_proxy_is_None() -> None:
    assert DIP(None) is None

def test_repr(deep_proxy: ImmutableOuter) -> None:
    expected = (
        "DeepImmutableProxy(Outer({'a': Inner(1)}, [Inner(2), Inner(3)]))"
    )
    assert repr(deep_proxy) == expected

def test_cannot_be_modified_if_delegated_to_tuple() -> None:
    class Main():
        def __init__(self, x: int) -> None:
            self.x = x
            self.delegate = (self,)
    obj = Main(3)
    obj.delegate[0].x = 5
    assert obj.delegate[0].x == 5
    proxy: DIP = DIP(Main(3))
    with pytest.raises(ConstantAttributeError):
        proxy.delegate[0].x = 5


class TestTupleProxy():
    @pytest.fixture
    def tuple_proxy(self) -> DIP:
        return DIP(('immutable', ['mutable']))

    def test_proxy_is_special(self) -> None:
        proxy: DIP = DIP((1, 2))
        assert isinstance(proxy, DIP)
        assert type(proxy) != DIP

    def test_getitem(self, tuple_proxy: DIP) -> None:
        assert tuple_proxy[0] == 'immutable'

    def test_access_method_after_getitem(self, tuple_proxy: DIP) -> None:
        assert tuple_proxy[0].upper() == 'IMMUTABLE'

    def test_deep_immutability(self, tuple_proxy: DIP) -> None:
        with pytest.raises(TypeError):
            tuple_proxy[1] = 3

    def test_even_deeper_immutability(self, tuple_proxy: DIP) -> None:
        with pytest.raises(TypeError):
            tuple_proxy[1][0] = 3

    def test_can_access_immutable_methods(self, tuple_proxy: DIP) -> None:
        assert tuple_proxy[1].index('mutable') == 0

    def test_cannot_access_methods_that_mutate(self, tuple_proxy: DIP) -> None:
        with pytest.raises(AttributeError):
            tuple_proxy[1].append(0)

    def test_immutable_method_works_normally(self, tuple_proxy: DIP) -> None:
        assert tuple_proxy.index('immutable') == 0

    def test_mutable_tuple_bug(self) -> None:
        mutable_tuple_proxy: DIP = DIP(('immutable', ['mutable']))
        assert mutable_tuple_proxy[1].index('mutable') == 0


class TestDictProxy():
    def test_getitem(self, deep_proxy: ImmutableOuter) -> None:
        assert deep_proxy.mapping['a'].x == 1

    def test_getitem_return_immutable_proxy(
        self, deep_proxy: ImmutableOuter
    ) -> None:
        assert isinstance(deep_proxy.mapping['a'], DIP)

    def test_get(self, deep_proxy: ImmutableOuter) -> None:
        assert deep_proxy.mapping.get('a', '5').x == 1

    def test_get_returns_immutable_proxy(
        self, deep_proxy: ImmutableOuter
    ) -> None:
        assert isinstance(deep_proxy.mapping.get('a', '5'), DIP)

    def test_items(self, deep_proxy: ImmutableOuter) -> None:
        items = tuple(deep_proxy.mapping.items()) 
        assert items[0][0] == 'a'
        assert items[0][1].x == 1

    def test_keys(self, deep_proxy: ImmutableOuter) -> None:
        assert tuple(deep_proxy.mapping.keys()) == ('a',)

    def test_values(self, deep_proxy: ImmutableOuter) -> None:
        assert tuple(deep_proxy.mapping.values())[0].x == 1

    def test_non_attribute_raise_exception(
        self, deep_proxy: ImmutableOuter
    ) -> None:
        with pytest.raises(AttributeError):
            deep_proxy.mapping.nonattr

    def test_invalid_raise_exception(self, deep_proxy: ImmutableOuter) -> None:
        with pytest.raises(AttributeError):
            deep_proxy.mapping.update({'b': 3})


class TestListProxy():
    def test_proxy_of_list(self) -> None:
        proxy: DIP = DIP([1, 2])
        assert proxy.index(1) == 0
        
    def test_getitem(self, deep_proxy: ImmutableOuter) -> None:
        assert deep_proxy.lst[0].x == 2

    def test_getitem_slice(self, deep_proxy: ImmutableOuter) -> None:
        assert deep_proxy.lst[:][0].x == 2

    def test_getitem_return_immutable_proxy(
        self, deep_proxy: ImmutableOuter
    ) -> None:
        assert isinstance(deep_proxy.lst[0], DIP)

    def test_non_attribute_raise_exception(
        self, deep_proxy: ImmutableOuter
    ) -> None:
        with pytest.raises(AttributeError):
            deep_proxy.lst.nonattr

    def test_immutable_method_works_normally(self) -> None:
        proxy: DIP = DIP(Outer({}, [1, 2, 3]))
        assert proxy.lst.index(2) == 1

    def test_invalid_method_raises_exception(
        self, deep_proxy: ImmutableOuter
    ) -> None:
        with pytest.raises(AttributeError):
            deep_proxy.lst.append(3)

    def test_deep_subscript_list(self) -> None:
        proxy: DIP = DIP([1, 2, 3])
        assert proxy[1] == 2
        assert isinstance(proxy[1], int)

    def test_deep_subscript_list_with_mutable(self) -> None:
        proxy: DIP = DIP([1, {2}, 3])
        assert proxy[1] == {2}
        assert isinstance(proxy[1], DIP)


class TestReProxies():
    class Outer():
        def __init__(self, pattern: re.Pattern) -> None:
            self.pattern = pattern

    def test_pattern_search_no_proxy(self) -> None:
        pattern = re.compile(r'(?P<number>\d+)')
        match = pattern.search('text 123.')
        assert isinstance(match, re.Match)
        assert int(match.group('number')) == 123

    def test_pattern_search(self) -> None:
        pattern = re.compile(r'(\d+)')
        obj = TestReProxies.Outer(pattern)
        proxy: DIP = DIP(obj)
        match = proxy.pattern.search('text 123.')
        assert isinstance(match, re.Match)
        assert int(match[0]) == 123      

    def test_match_group(self) -> None:
        pattern = re.compile(r'(?P<number>\d+)')
        obj = TestReProxies.Outer(pattern)
        proxy: DIP = DIP(obj)
        match = proxy.pattern.search('text 123.')
        assert isinstance(match, re.Match)
        assert int(match.group('number')) == 123      


class TestDatetimeProxies():
    class Outer():
        def __init__(self, date: date) -> None:
            self.date = date

    def test_format(self) -> None:
        a_date = date(2022, 12, 3)
        assert f'{a_date.day} of {a_date:%B}' == '3 of December'
        proxy: DIP[date] = DIP(a_date)
        assert f'{proxy.day} of {proxy:%B}' == '3 of December' # type: ignore
    
    def test_delta(self) -> None:
        start = TestDatetimeProxies.Outer(date(2022, 12, 3))
        end = TestDatetimeProxies.Outer(date(2022, 12, 6))
        delta = end.date - start.date
        assert delta.days == 3
        start_proxy: DIP[date] = DIP(start)
        end_proxy: DIP[date] = DIP(end)
        delta_proxy = end_proxy.date - start_proxy.date # type: ignore
        assert delta_proxy.days == 3


class TestPathProxies():
    class Outer():
        def __init__(self, path: Path) -> None:
            self.path = path

    def test_exists(self) -> None:
        file_path = Path(__file__)
        assert file_path.exists()
        proxy: DIP[Path] = DIP(file_path)
        assert proxy.exists() # type: ignore

    def test_inner_exists(self) -> None:
        obj = self.Outer(Path(__file__))
        assert obj.path.exists()
        proxy: DIP = DIP(obj)
        assert proxy.path.exists() # type: ignore


class TestModuleProxies():
    class Outer():
        def __init__(self, module: ModuleType) -> None:
            self.module = module

    def test_dict(self) -> None:
        assert 'match' in re.__dict__
        assert 'match' in DIP(re.__dict__) # type: ignore

    def test_inner_dict(self) -> None:
        obj = self.Outer(re)
        assert 'match' in obj.module.__dict__
        proxy: DIP = DIP(obj)
        assert 'match' in proxy.module.__dict__ # type: ignore
