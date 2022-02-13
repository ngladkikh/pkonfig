from pkonfig.base import is_user_attr


def test_is_user_attr():
    class Test:
        f = 1
        _f = 0

        def m(self):
            pass

        def _m(self):
            pass

    attrs = []
    for name in dir(Test):
        attrs.append((name, getattr(Test, name)))

    user_attrs = set(
        map(lambda x: x[0],
            filter(
                lambda x: is_user_attr(*x),
                attrs
            )
            )
    )
    assert user_attrs == {"f"}
