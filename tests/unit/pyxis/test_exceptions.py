import pytest

from pyxis.exceptions import IllegalArgumentException, IllegalStateException


def test_illegal_argument_exception():
    with pytest.raises(IllegalArgumentException):
        raise IllegalArgumentException('foo')


def test_illegal_state_exception():
    with pytest.raises(IllegalStateException):
        raise IllegalStateException('foo')
