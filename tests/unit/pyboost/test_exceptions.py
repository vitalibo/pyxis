import pytest

from pyboost.exceptions import IllegalArgumentException, IllegalStateException, \
    NotImplementedException, UnsupportedOperationException


def test_illegal_argument_exception():
    with pytest.raises(IllegalArgumentException):
        raise IllegalArgumentException('foo')


def test_illegal_state_exception():
    with pytest.raises(IllegalStateException):
        raise IllegalStateException('foo')


def test_not_implemented_exception():
    with pytest.raises(NotImplementedException):
        raise NotImplementedException('foo')


def test_unsupported_operation_exception():
    with pytest.raises(UnsupportedOperationException):
        raise UnsupportedOperationException('foo')
