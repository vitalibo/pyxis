import dataclasses
from typing import Optional

import pytest

from pyboost import functions


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


def test_dataclass():
    @functions.dataclass
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


def test_dataclass_init_false():
    @functions.dataclass(init=False)
    class User:
        """ User """

        name: str
        age: int
        address: Optional[str]

    user = User()
    user.name = 'foo'
    user.age = 12
    user.address = None

    assert User.name is not None
    assert User.name(user) == 'foo'
    assert User.age(user) == 12
    assert User.address(user) is None


def test_identity():
    obj = object()

    actual = functions.identity(obj)

    assert hash(obj) == hash(actual)


def test_one_instance_only():
    class ClassA(metaclass=functions.SingletonMeta):
        """ Used for testing only """

    obj1 = ClassA()
    obj2 = ClassA()

    assert obj1 is obj2


def test_multiple_classes():
    class ClassA(metaclass=functions.SingletonMeta):
        """ Used for testing only """

    class ClassB(metaclass=functions.SingletonMeta):
        """ Used for testing only """

    obj1 = ClassA()
    obj2 = ClassB()

    assert obj1 is not obj2
