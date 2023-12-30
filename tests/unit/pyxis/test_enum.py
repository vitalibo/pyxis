from enum import Enum

import pytest

from pyxis.enum import EnumMixin


class Weekday(EnumMixin, Enum):
    """
    An enum representing the days of the week.
    """

    MONDAY = 'mon'
    TUESDAY = 'tue'
    WEDNESDAY = 'wed'
    THURSDAY = 'thu'
    FRIDAY = 'fri'
    SATURDAY = 'sat'
    SUNDAY = 'sun'


@pytest.mark.parametrize('value, expected', [
    ('mon', Weekday.MONDAY),
    ('tue', Weekday.TUESDAY),
    ('wed', Weekday.WEDNESDAY),
    ('thu', Weekday.THURSDAY),
    ('fri', Weekday.FRIDAY),
    ('sat', Weekday.SATURDAY),
    ('sun', Weekday.SUNDAY),
    ('monday', None),
])
def test_value_of(value, expected):
    actual = Weekday.value_of(value)

    assert actual == expected


@pytest.mark.parametrize('value, expected', [
    (Weekday.MONDAY, 0),
    (Weekday.TUESDAY, 1),
    (Weekday.WEDNESDAY, 2),
    (Weekday.THURSDAY, 3),
    (Weekday.FRIDAY, 4),
    (Weekday.SATURDAY, 5),
    (Weekday.SUNDAY, 6)
])
def test_ordinal(value, expected):
    actual = value.ordinal

    assert actual == expected


def test_equal():
    assert Weekday.MONDAY == Weekday.MONDAY


def test_not_equal():
    assert Weekday.MONDAY != Weekday.TUESDAY


def test_greater_than():
    assert Weekday.TUESDAY > Weekday.MONDAY


def test_greater_than_or_equal():
    assert Weekday.TUESDAY >= Weekday.MONDAY


def test_less_than():
    assert Weekday.MONDAY < Weekday.TUESDAY


def test_less_than_or_equal():
    assert Weekday.MONDAY <= Weekday.TUESDAY
