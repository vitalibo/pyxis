import pytest

from bootstrap import objects


def test_require_not_none():
    obj = object()

    actual = objects.require_not_none(obj)

    assert hash(obj) == hash(actual)


def test_require_not_none_raise():
    with pytest.raises(ValueError) as e:
        objects.require_not_none(None)

    assert e.value.args == ()


def test_require_not_none_with_msg():
    obj = object()

    actual = objects.require_not_none(obj, 'foo')

    assert hash(obj) == hash(actual)


def test_require_not_none_raise_with_msg():
    with pytest.raises(ValueError) as e:
        objects.require_not_none(None, 'foo')

    assert e.value.args == ('foo',)


def test_is_none_false():
    actual = objects.is_none('foo')

    assert not actual


def test_is_none_true():
    actual = objects.is_none(None)

    assert actual


def test_not_none_false():
    actual = objects.not_none(None)

    assert not actual


def test_not_none_true():
    actual = objects.not_none('foo')

    assert actual


def test_identity():
    obj = object()

    actual = objects.identity(obj)

    assert hash(obj) == hash(actual)
