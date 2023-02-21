from immutable import get_type, is_instance, ImmutableProxy, DeepImmutableProxy

def test_get_type_of_regular_object() -> None:
    assert get_type('text') == str

def test_get_type_of_immutable_proxy() -> None:
    assert get_type(ImmutableProxy(['text'])) == list

def test_get_type_of_deep_immutable_proxy() -> None:
    assert get_type(DeepImmutableProxy(['text'])) == list

def test_is_instance_of_regular_object() -> None:
    assert is_instance('text', str)

def test_is_instance_of_immutable_proxy() -> None:
    assert is_instance(ImmutableProxy(['text']), list)

def test_is_instance_of_deep_immutable_proxy() -> None:
    assert is_instance(DeepImmutableProxy(['text']), list)
