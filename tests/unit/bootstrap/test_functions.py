import pytest

from bootstrap import functions


def test_require_not_none():
    obj = object()

    actual = functions.require_not_none(obj)

    assert hash(obj) == hash(actual)


def test_require_not_none_raise():
    with pytest.raises(ValueError) as e:
        functions.require_not_none(None)

    assert e.value.args == ()


def test_require_not_none_with_msg():
    obj = object()

    actual = functions.require_not_none(obj, 'foo')

    assert hash(obj) == hash(actual)


def test_require_not_none_raise_with_msg():
    with pytest.raises(ValueError) as e:
        functions.require_not_none(None, 'foo')

    assert e.value.args == ('foo',)


def test_is_none_false():
    actual = functions.is_none('foo')

    assert not actual


def test_is_none_true():
    actual = functions.is_none(None)

    assert actual


def test_not_none_false():
    actual = functions.not_none(None)

    assert not actual


def test_not_none_true():
    actual = functions.not_none('foo')

    assert actual


def test_identity():
    obj = object()

    actual = functions.identity(obj)

    assert hash(obj) == hash(actual)
