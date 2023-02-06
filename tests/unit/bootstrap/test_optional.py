from unittest import mock

import pytest

from bootstrap.optional import Optional, _Empty


def test_empty():
    actual = Optional.empty()

    assert hash(actual) == hash(_Empty())
    assert hash(actual) == hash(None)


def test_of():
    actual = Optional.of('foo')

    assert hash(actual) == hash('foo')


def test_of_raise():
    with pytest.raises(ValueError):
        Optional.of(None)


def test_of_nullable():
    actual = Optional.of_nullable('foo')

    assert hash(actual) == hash('foo')


def test_of_nullable_none():
    actual = Optional.of_nullable(None)

    assert actual == Optional.empty()


def test_get():
    obj = Optional.of('foo')

    actual = obj.get()

    assert actual == 'foo'


def test_get_raise():
    obj = Optional.empty()

    with pytest.raises(ValueError) as e:
        obj.get()

    assert str(e.value) == 'No value present'


def test_is_empty():
    obj = Optional.empty()

    assert obj.is_empty()


def test_is_not_empty():
    obj = Optional.of('foo')

    assert not obj.is_empty()


def test_is_present():
    obj = Optional.of('foo')

    assert obj.is_present()


def test_is_not_present():
    obj = Optional.empty()

    assert not obj.is_present()


def test_filter():
    obj = Optional.of('foo')
    mock_predicate = mock.Mock()
    mock_predicate.return_value = True

    actual = obj.filter(mock_predicate)

    assert actual == obj
    assert actual != Optional.empty()
    mock_predicate.assert_called_once_with('foo')


def test_filter_not_pass():
    obj = Optional.of('foo')
    mock_predicate = mock.Mock()
    mock_predicate.return_value = False

    actual = obj.filter(mock_predicate)

    assert actual != obj
    assert actual == Optional.empty()
    mock_predicate.assert_called_once_with('foo')


def test_filter_empty():
    obj = Optional.empty()
    mock_predicate = mock.Mock()
    mock_predicate.return_value = True

    actual = obj.filter(mock_predicate)

    assert actual == obj
    assert actual == Optional.empty()
    mock_predicate.assert_not_called()


def test_filter_predicate_is_none():
    obj = Optional.of('foo')

    with pytest.raises(ValueError):
        obj.filter(None)


def test_flat_map():
    obj = Optional.of('foo')
    mock_mapper = mock.Mock()
    mock_mapper.return_value = Optional.of('bar')

    actual = obj.flat_map(mock_mapper)

    assert actual == Optional.of('bar')
    mock_mapper.assert_called_once_with('foo')


def test_flat_map_return_empty():
    obj = Optional.of('foo')
    mock_mapper = mock.Mock()
    mock_mapper.return_value = Optional.empty()

    actual = obj.flat_map(mock_mapper)

    assert actual == Optional.empty()
    mock_mapper.assert_called_once_with('foo')


def test_flat_map_empty():
    obj = Optional.empty()
    mock_mapper = mock.Mock()
    mock_mapper.return_value = Optional.empty()

    actual = obj.flat_map(mock_mapper)

    assert actual == Optional.empty()
    mock_mapper.assert_not_called()


def test_flat_map_mapper_is_none():
    obj = Optional.of('foo')

    with pytest.raises(ValueError):
        obj.flat_map(None)


def test_if_present():
    obj = Optional.of('foo')
    mock_action = mock.Mock()

    obj.if_present(mock_action)

    mock_action.assert_called_with('foo')


def test_if_present_not_called():
    obj = Optional.empty()
    mock_action = mock.Mock()

    obj.if_present(mock_action)

    mock_action.assert_not_called()


def test_if_present_action_is_none():
    obj = Optional.of('foo')

    with pytest.raises(ValueError):
        obj.if_present(None)


def test_if_present_or_else():
    obj = Optional.of('foo')
    mock_action = mock.Mock()
    mock_empty_action = mock.Mock()

    obj.if_present_or_else(mock_action, mock_empty_action)

    mock_action.assert_called_with('foo')
    mock_empty_action.assert_not_called()


def test_if_present_or_else_empty():
    obj = Optional.empty()
    mock_action = mock.Mock()
    mock_empty_action = mock.Mock()

    obj.if_present_or_else(mock_action, mock_empty_action)

    mock_action.assert_not_called()
    mock_empty_action.assert_called_once()


def test_if_present_or_else_action_is_none():
    obj = Optional.of('foo')
    mock_empty_action = mock.Mock()

    with pytest.raises(ValueError):
        obj.if_present_or_else(None, mock_empty_action)


def test_if_present_or_else_empty_action_is_none():
    obj = Optional.of('foo')
    mock_action = mock.Mock()

    with pytest.raises(ValueError):
        obj.if_present_or_else(mock_action, None)


def test_map():
    obj = Optional.of('foo')
    mock_mapper = mock.Mock()
    mock_mapper.return_value = 'bar'

    actual = obj.map(mock_mapper)

    assert actual == Optional.of('bar')
    mock_mapper.assert_called_once_with('foo')


def test_map_return_none():
    obj = Optional.of('foo')
    mock_mapper = mock.Mock()
    mock_mapper.return_value = None

    actual = obj.map(mock_mapper)

    assert actual == Optional.empty()
    mock_mapper.assert_called_once_with('foo')


def test_map_empty():
    obj = Optional.empty()
    mock_mapper = mock.Mock()
    mock_mapper.return_value = 'bar'

    actual = obj.map(mock_mapper)

    assert actual == Optional.empty()
    mock_mapper.assert_not_called()


def test_map_mapper_is_none():
    obj = Optional.of('foo')

    with pytest.raises(ValueError):
        obj.map(None)


def test_or():
    obj1 = Optional.of('foo')
    obj2 = Optional.of('bar')

    actual = obj1 or obj2

    assert actual == obj1


def test_or_empty():
    obj1 = Optional.empty()
    obj2 = Optional.of('bar')

    actual = obj1 or obj2

    assert actual == obj2


def test_or_both_empty():
    obj1 = Optional.empty()
    obj2 = Optional.empty()

    actual = obj1 or obj2

    assert actual == obj2


def test_or_empty_not_optional():
    obj1 = Optional.empty()
    obj2 = 'bar'

    actual = obj1 or obj2

    assert actual == obj2


def test_or_else():
    obj = Optional.of('foo')

    actual = obj.or_else('bar')

    assert actual == 'foo'


def test_or_else_empty():
    obj = Optional.empty()

    actual = obj.or_else('bar')

    assert actual == 'bar'


def test_or_else_get():
    obj = Optional.of('foo')
    mock_supplier = mock.Mock()
    mock_supplier.return_value = 'bar'

    actual = obj.or_else_get(mock_supplier)

    assert actual == 'foo'
    mock_supplier.assert_not_called()


def test_or_else_get_empty():
    obj = Optional.empty()
    mock_supplier = mock.Mock()
    mock_supplier.return_value = 'bar'

    actual = obj.or_else_get(mock_supplier)

    assert actual == 'bar'
    mock_supplier.assert_called_once()


def test_or_else_get_supplier_is_none():
    obj = Optional.of('foo')

    with pytest.raises(ValueError):
        obj.or_else_get(None)


def test_or_else_raise_not_raised():
    obj = Optional.of('foo')

    actual = obj.or_else_raise()

    assert actual == 'foo'


def test_or_else_raise():
    obj = Optional.empty()

    with pytest.raises(ValueError) as e:
        obj.or_else_raise()

    assert str(e.value) == 'No value present'


def test_or_else_raise_custom_error():
    obj = Optional.empty()

    with pytest.raises(KeyError):
        obj.or_else_raise(KeyError)


def test_bool():
    assert Optional.of('foo')
    assert not Optional.empty()


def test_equals():
    assert Optional.of('foo') == Optional.of('foo')
    assert Optional.of('foo') != Optional.of('bar')
    assert Optional.of('foo') != Optional.empty()
    assert Optional.empty() == Optional.empty()
    assert Optional.of('foo') != 'foo'


def test_hash():
    assert hash(Optional.of('foo')) == hash(Optional.of('foo'))
    assert hash(Optional.of('foo')) == hash('foo')
    assert hash(Optional.empty()) == hash(None)


def test_repl():
    assert repr(Optional.of('foo')) == "Optional('foo')"
    assert repr(Optional.empty()) == 'Optional(None)'
