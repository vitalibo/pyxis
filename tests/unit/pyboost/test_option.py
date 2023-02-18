from unittest import mock

import pytest

from pyboost.option import Option, _Empty


def test_empty():
    actual = Option.empty()

    assert hash(actual) == hash(_Empty())
    assert hash(actual) == hash(None)


def test_of():
    actual = Option.of('foo')

    assert hash(actual) == hash('foo')


def test_of_raise():
    with pytest.raises(ValueError):
        Option.of(None)


def test_of_nullable():
    actual = Option.of_nullable('foo')

    assert hash(actual) == hash('foo')


def test_of_nullable_none():
    actual = Option.of_nullable(None)

    assert actual == Option.empty()


def test_get():
    obj = Option.of('foo')

    actual = obj.get()

    assert actual == 'foo'


def test_get_raise():
    obj = Option.empty()

    with pytest.raises(ValueError) as e:
        obj.get()

    assert str(e.value) == 'No value present'


def test_is_empty():
    obj = Option.empty()

    assert obj.is_empty()


def test_is_not_empty():
    obj = Option.of('foo')

    assert not obj.is_empty()


def test_is_present():
    obj = Option.of('foo')

    assert obj.is_present()


def test_is_not_present():
    obj = Option.empty()

    assert not obj.is_present()


def test_filter():
    obj = Option.of('foo')
    mock_predicate = mock.Mock()
    mock_predicate.return_value = True

    actual = obj.filter(mock_predicate)

    assert actual == obj
    assert actual != Option.empty()
    mock_predicate.assert_called_once_with('foo')


def test_filter_not_pass():
    obj = Option.of('foo')
    mock_predicate = mock.Mock()
    mock_predicate.return_value = False

    actual = obj.filter(mock_predicate)

    assert actual != obj
    assert actual == Option.empty()
    mock_predicate.assert_called_once_with('foo')


def test_filter_empty():
    obj = Option.empty()
    mock_predicate = mock.Mock()
    mock_predicate.return_value = True

    actual = obj.filter(mock_predicate)

    assert actual == obj
    assert actual == Option.empty()
    mock_predicate.assert_not_called()


def test_filter_predicate_is_none():
    obj = Option.of('foo')

    with pytest.raises(ValueError):
        obj.filter(None)


def test_flat_map():
    obj = Option.of('foo')
    mock_mapper = mock.Mock()
    mock_mapper.return_value = Option.of('bar')

    actual = obj.flat_map(mock_mapper)

    assert actual == Option.of('bar')
    mock_mapper.assert_called_once_with('foo')


def test_flat_map_return_empty():
    obj = Option.of('foo')
    mock_mapper = mock.Mock()
    mock_mapper.return_value = Option.empty()

    actual = obj.flat_map(mock_mapper)

    assert actual == Option.empty()
    mock_mapper.assert_called_once_with('foo')


def test_flat_map_empty():
    obj = Option.empty()
    mock_mapper = mock.Mock()
    mock_mapper.return_value = Option.empty()

    actual = obj.flat_map(mock_mapper)

    assert actual == Option.empty()
    mock_mapper.assert_not_called()


def test_flat_map_mapper_is_none():
    obj = Option.of('foo')

    with pytest.raises(ValueError):
        obj.flat_map(None)


def test_if_present():
    obj = Option.of('foo')
    mock_action = mock.Mock()

    obj.if_present(mock_action)

    mock_action.assert_called_with('foo')


def test_if_present_not_called():
    obj = Option.empty()
    mock_action = mock.Mock()

    obj.if_present(mock_action)

    mock_action.assert_not_called()


def test_if_present_action_is_none():
    obj = Option.of('foo')

    with pytest.raises(ValueError):
        obj.if_present(None)


def test_if_present_or_else():
    obj = Option.of('foo')
    mock_action = mock.Mock()
    mock_empty_action = mock.Mock()

    obj.if_present_or_else(mock_action, mock_empty_action)

    mock_action.assert_called_with('foo')
    mock_empty_action.assert_not_called()


def test_if_present_or_else_empty():
    obj = Option.empty()
    mock_action = mock.Mock()
    mock_empty_action = mock.Mock()

    obj.if_present_or_else(mock_action, mock_empty_action)

    mock_action.assert_not_called()
    mock_empty_action.assert_called_once()


def test_if_present_or_else_action_is_none():
    obj = Option.of('foo')
    mock_empty_action = mock.Mock()

    with pytest.raises(ValueError):
        obj.if_present_or_else(None, mock_empty_action)


def test_if_present_or_else_empty_action_is_none():
    obj = Option.of('foo')
    mock_action = mock.Mock()

    with pytest.raises(ValueError):
        obj.if_present_or_else(mock_action, None)


def test_map():
    obj = Option.of('foo')
    mock_mapper = mock.Mock()
    mock_mapper.return_value = 'bar'

    actual = obj.map(mock_mapper)

    assert actual == Option.of('bar')
    mock_mapper.assert_called_once_with('foo')


def test_map_return_none():
    obj = Option.of('foo')
    mock_mapper = mock.Mock()
    mock_mapper.return_value = None

    actual = obj.map(mock_mapper)

    assert actual == Option.empty()
    mock_mapper.assert_called_once_with('foo')


def test_map_empty():
    obj = Option.empty()
    mock_mapper = mock.Mock()
    mock_mapper.return_value = 'bar'

    actual = obj.map(mock_mapper)

    assert actual == Option.empty()
    mock_mapper.assert_not_called()


def test_map_mapper_is_none():
    obj = Option.of('foo')

    with pytest.raises(ValueError):
        obj.map(None)


def test_or():
    obj1 = Option.of('foo')
    obj2 = Option.of('bar')

    actual = obj1 or obj2

    assert actual == obj1


def test_or_empty():
    obj1 = Option.empty()
    obj2 = Option.of('bar')

    actual = obj1 or obj2

    assert actual == obj2


def test_or_both_empty():
    obj1 = Option.empty()
    obj2 = Option.empty()

    actual = obj1 or obj2

    assert actual == obj2


def test_or_empty_not_option():
    obj1 = Option.empty()
    obj2 = 'bar'

    actual = obj1 or obj2

    assert actual == obj2


def test_or_else():
    obj = Option.of('foo')

    actual = obj.or_else('bar')

    assert actual == 'foo'


def test_or_else_empty():
    obj = Option.empty()

    actual = obj.or_else('bar')

    assert actual == 'bar'


def test_or_else_get():
    obj = Option.of('foo')
    mock_supplier = mock.Mock()
    mock_supplier.return_value = 'bar'

    actual = obj.or_else_get(mock_supplier)

    assert actual == 'foo'
    mock_supplier.assert_not_called()


def test_or_else_get_empty():
    obj = Option.empty()
    mock_supplier = mock.Mock()
    mock_supplier.return_value = 'bar'

    actual = obj.or_else_get(mock_supplier)

    assert actual == 'bar'
    mock_supplier.assert_called_once()


def test_or_else_get_supplier_is_none():
    obj = Option.of('foo')

    with pytest.raises(ValueError):
        obj.or_else_get(None)


def test_or_else_raise_not_raised():
    obj = Option.of('foo')

    actual = obj.or_else_raise()

    assert actual == 'foo'


def test_or_else_raise():
    obj = Option.empty()

    with pytest.raises(ValueError) as e:
        obj.or_else_raise()

    assert str(e.value) == 'No value present'


def test_or_else_raise_custom_error():
    obj = Option.empty()

    with pytest.raises(KeyError):
        obj.or_else_raise(KeyError)


def test_bool():
    assert Option.of('foo')
    assert not Option.empty()


def test_equals():
    assert Option.of('foo') == Option.of('foo')
    assert Option.of('foo') != Option.of('bar')
    assert Option.of('foo') != Option.empty()
    assert Option.empty() == Option.empty()
    assert Option.of('foo') != 'foo'


def test_hash():
    assert hash(Option.of('foo')) == hash(Option.of('foo'))
    assert hash(Option.of('foo')) == hash('foo')
    assert hash(Option.empty()) == hash(None)


def test_repl():
    assert repr(Option.of('foo')) == "Option('foo')"
    assert repr(Option.empty()) == 'Option(None)'
