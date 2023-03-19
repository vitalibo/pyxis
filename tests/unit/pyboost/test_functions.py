import dataclasses
from typing import Optional
from unittest import mock

import pytest

from pyboost import functions


# pylint: disable=missing-class-docstring

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
        name: str
        age: int

    user = User()
    user.name = 'foo'
    user.age = 12

    assert User.name is not None
    assert User.name(user) == 'foo'
    assert User.age(user) == 12


def test_dataclass_pydantic():
    @functions.dataclass
    class User:
        name: str
        age: int

    user = User('foo', 'bar')

    with pytest.raises(ValueError, match='age'):
        user.__pydantic_validate_values__()  # pylint: disable=no-member


@mock.patch('pydantic.dataclasses')
def test_dataclass_no_pydantic(mock_dataclasses):
    mock_dataclasses.side_effect = ImportError

    @functions.dataclass
    class User:
        name: str
        age: int

    user = User('foo', 'bar')

    with pytest.raises(AttributeError, match="'User' object has no attribute '__pydantic_validate_values__'"):
        user.__pydantic_validate_values__()  # pylint: disable=no-member


def test_identity():
    obj = object()

    actual = functions.identity(obj)

    assert hash(obj) == hash(actual)


def test_one_instance_only():
    class ClassA(metaclass=functions.SingletonMeta):
        pass

    obj1 = ClassA()
    obj2 = ClassA()

    assert obj1 is obj2


def test_multiple_classes():
    class ClassA(metaclass=functions.SingletonMeta):
        pass

    class ClassB(metaclass=functions.SingletonMeta):
        pass

    obj1 = ClassA()
    obj2 = ClassB()

    assert obj1 is not obj2


def test_return_values_as_list():
    @functions.return_values_as(list)
    def func():
        yield from [1, 2, 3, 2, 1]

    actual = func()

    assert actual == [1, 2, 3, 2, 1]


def test_return_values_as_set():
    @functions.return_values_as(set)
    def func():
        yield from [1, 2, 3, 2, 1]

    actual = func()

    assert actual == {1, 2, 3}


def test_return_values_as_dict():
    @functions.return_values_as(dict)
    def func():
        yield from [('foo', 1), ('bar', 2), ('baz', 3)]

    actual = func()

    assert actual == {'foo': 1, 'bar': 2, 'baz': 3}
