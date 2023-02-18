import dataclasses
from typing import Optional

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


def test_field_ref():
    @functions.field_ref
    @dataclasses.dataclass
    class User:
        """ User """

        name: str
        age: int
        address: Optional[str]

    user = User('foo', 12, None)

    assert User.name is not None
    assert User.name(user) == 'foo'
    assert User.age(user) == 12
    assert User.address(user) is None


def test_identity():
    obj = object()

    actual = functions.identity(obj)

    assert hash(obj) == hash(actual)
