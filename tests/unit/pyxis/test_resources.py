from unittest import mock

from pyxis import resources


def test_absolute():
    actual = resources.absolute(__file__, 'data/scratch.txt')

    assert actual.endswith('tests/unit/pyxis/data/scratch.txt')


def test_load_text():
    with mock.patch('builtins.open', mock.mock_open(read_data='foo')) as mock_open:
        actual = resources.load_text(__file__, 'data/scratch.txt')

        assert actual == 'foo'
        call_args = mock_open.call_args
        assert call_args[0][0].endswith('tests/unit/pyxis/data/scratch.txt')
        assert call_args[1] == {'encoding': 'utf-8'}


def test_load_text_encoding():
    with mock.patch('builtins.open', mock.mock_open(read_data='foo')) as mock_open:
        actual = resources.load_text(__file__, 'data/scratch.txt', encoding='utf-16')

        assert actual == 'foo'
        call_args = mock_open.call_args
        assert call_args[1] == {'encoding': 'utf-16'}


def test_load_json():
    with mock.patch('builtins.open', mock.mock_open(read_data='{"foo": "bar"}')):
        actual = resources.load_json(__file__, 'data/scratch.json')

        assert actual == {'foo': 'bar'}


def test_load_json_as_text():
    with mock.patch('builtins.open', mock.mock_open(read_data='{\n  "foo": "bar"\n}\n')):
        actual = resources.load_json_as_text(__file__, 'data/scratch.json')

        assert actual == '{"foo": "bar"}'


def test_load_yaml():
    with mock.patch('builtins.open', mock.mock_open(read_data='foo: bar\nbaz: qux\n')):
        actual = resources.load_yaml(__file__, 'data/scratch.yaml')

        assert actual == {'foo': 'bar', 'baz': 'qux'}


def test_load_yaml_all():
    with mock.patch('builtins.open', mock.mock_open(read_data='foo: bar\n---\nbaz: qux\n')):
        actual = list(resources.load_yaml_all(__file__, 'data/scratch.yaml'))

        assert actual == [{'foo': 'bar'}, {'baz': 'qux'}]
