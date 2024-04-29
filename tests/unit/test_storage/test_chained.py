from collections import ChainMap

import pytest

from pkonfig import DictStorage


def test_multilevel():
    first = DictStorage(**{"foo": "baz"})
    second = DictStorage(**{"foo": "biz", "inner": {"fiz": "buzz"}})
    third = DictStorage(**{"foo": "buz", "inner": {"some": "other"}})
    storage = ChainMap(first, second, third)

    assert storage[("foo",)] == "baz"
    assert storage[("inner", "fiz")] == "buzz"
    assert storage[("inner", "some")] == "other"
    with pytest.raises(KeyError):
        storage[("inner", "not_exists")]
