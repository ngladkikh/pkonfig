import pytest

from pkonfig import Storage


def test_multilevel():
    first = {"foo": "baz"}
    second = {"foo": "biz", "inner": {"fiz": "buzz"}}
    third = {"foo": "buz", "inner": {"some": "other"}}
    storage = Storage(first, second, third)

    assert storage[("foo",)] == "baz"
    assert storage[("inner", "fiz")] == "buzz"
    assert storage[("inner", "some")] == "other"
    with pytest.raises(KeyError):
        storage[("inner", "not_exists")]
