import dataclasses
from typing import Optional
from unittest import mock

import pytest

from pyboost.dataclasses import dataclass, reference


# pylint: disable=missing-class-docstring

def test_field_reference():
    @reference
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
    @dataclass
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
    @dataclass(init=False)
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
    @dataclass
    class User:
        name: str
        age: int

    user = User('foo', 'bar')

    with pytest.raises(ValueError, match='age'):
        user.__pydantic_validate_values__()  # pylint: disable=no-member


@mock.patch('pydantic.dataclasses')
def test_dataclass_no_pydantic(mock_dataclasses):
    mock_dataclasses.side_effect = ImportError

    @dataclass
    class User:
        name: str
        age: int

    user = User('foo', 'bar')

    with pytest.raises(AttributeError, match="'User' object has no attribute '__pydantic_validate_values__'"):
        user.__pydantic_validate_values__()  # pylint: disable=no-member
