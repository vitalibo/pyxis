from unittest import mock

from pyxis import resources


def test_resource():
    actual = resources.resource(__file__, 'data/scratch.txt')

    assert actual.endswith('tests/unit/pyxis/data/scratch.txt')


def test_resource_as_str():
    with mock.patch('builtins.open', mock.mock_open(read_data='foo')) as mock_open:
        actual = resources.resource_as_str(__file__, 'data/scratch.txt')

        assert actual == 'foo'
        call_args = mock_open.call_args
        assert call_args[0][0].endswith('tests/unit/pyxis/data/scratch.txt')
        assert call_args[0][1] == 'r'
        assert call_args[1] == {'encoding': 'utf-8'}


def test_resource_as_str_encoding():
    with mock.patch('builtins.open', mock.mock_open(read_data='foo')) as mock_open:
        actual = resources.resource_as_str(__file__, 'data/scratch.txt', encoding='utf-16')

        assert actual == 'foo'
        call_args = mock_open.call_args
        assert call_args[1] == {'encoding': 'utf-16'}


def test_resource_as_json():
    with mock.patch('builtins.open', mock.mock_open(read_data='{"foo": "bar"}')):
        actual = resources.resource_as_json(__file__, 'data/scratch.json')

        assert actual == {'foo': 'bar'}


def test_resource_as_json_str():
    with mock.patch('builtins.open', mock.mock_open(read_data='{\n  "foo": "bar"\n}\n')):
        actual = resources.resource_as_json_str(__file__, 'data/scratch.json')

        assert actual == '{"foo": "bar"}'
