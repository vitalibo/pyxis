from __future__ import annotations

from dataclasses import field
from typing import Optional, List

import pydantic
import pytest

from bootstrap.dataclasses import dataclass


@dataclass
class ClassA:  # pylint: disable=missing-class-docstring,invalid-name
    f1: str
    f2: int
    f3: List[str] = field(default_factory=lambda: ['def1', 'def2'])
    f4: Optional[ClassA] = None


@dataclass
class ClassB:  # pylint: disable=missing-class-docstring,invalid-name
    f1: str
    f2: int


def test_dataclass():
    actual = ClassA(f1='v1', f2=123, f3=['v2', 'v3'], f4=ClassA(f1='v4', f2=321))

    assert actual.f1 == 'v1'
    assert actual.f2 == 123
    assert actual.f3 == ['v2', 'v3']
    assert actual.f4.f1 == 'v4'
    assert actual.f4.f2 == 321
    assert actual.f4.f3 == ['def1', 'def2']
    assert actual.f4.f4 is None


def test_dataclass_incorrect():
    actual = ClassB(f1='v1', f2='v2')

    assert actual.f1 == 'v1'
    assert actual.f2 == 'v2'


def test_dataclass_validation():
    actual = ClassB(f1='v1', f2='123')

    actual.__pydantic_validate_values__()  # pylint: disable=no-member

    assert actual.f1 == 'v1'
    assert actual.f2 == 123


def test_dataclass_validation_incorrect():
    actual = ClassB(f1='v1', f2='v2')

    with pytest.raises(pydantic.error_wrappers.ValidationError) as ex:
        actual.__pydantic_validate_values__()  # pylint: disable=no-member

    errors = ex.value.raw_errors
    assert len(errors) == 1
    assert errors[0].loc_tuple() == ('f2',)


def test_method_reference():
    actual = ClassA(f1='v1', f2=123, f3=['v2', 'v3'], f4=ClassA(f1='v4', f2=321))

    assert ClassA.f1(actual) == 'v1'
    assert ClassA.f2(actual) == 123
    assert ClassA.f3(actual) == ['v2', 'v3']  # pylint: disable=not-callable
    assert ClassA.f3[::-1](actual) == ['v3', 'v2']  # pylint: disable=unsubscriptable-object
    assert ClassA.f4.f1(actual) == 'v4'
    assert ClassA.f4.f2(actual) == 321
    assert ClassA.f4.f3(actual) == ['def1', 'def2']
    assert ClassA.f4.f3(actual)[0] == 'def1'
    assert ClassA.f4.f4(actual) is None


def test_method_reference_not_exists():
    actual = ClassB(f1='v1', f2=123)

    with pytest.raises(AttributeError) as e:
        ClassB.f3(actual)  # pylint: disable=no-member
    assert str(e.value) == "type object 'ClassB' has no attribute 'f3'"
