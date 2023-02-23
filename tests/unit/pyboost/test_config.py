import os
import sys
from unittest import mock

import pytest

from pyboost.config import Config, ConfigException, ConfigFactory, LocalFileConfigReader, JsonConfigParser, \
    IniConfigParser, ConfigParser, ConfigReader


def test_config_get():
    config = Config({'foo': {'bar': {'baz': 123}}})

    actual = config.get('foo.bar.baz')

    assert actual == 123


def test_config_get_missing_key():
    config = Config({'foo': {'bar': {'baz': 123}}})

    with pytest.raises(ConfigException) as e:
        config.get('foo.bar.tar')

    assert str(e.value) == 'no config found for key "foo.bar.tar"'


def test_config_get_none():
    config = Config({'foo': {'bar': {'baz': None}}})

    actual = config.get('foo.bar.baz')

    assert actual is None


def test_config_get_default():
    config = Config({'foo': {'bar': {'baz': None}}})

    actual = config.get('foo.bar.baz', 321)

    assert actual == 321


def test_config_get_not_default():
    config = Config({'foo': {'bar': {'baz': 123}}})

    actual = config.get('foo.bar.baz', 321)

    assert actual == 123


def test_config_get_array_index():
    config = Config({'foo': {'bar': [{'baz': 123}, {'baz': 321}, {'baz': 231}]}})

    actual = config.get('foo.bar[1].baz')

    assert actual == 321


def test_config_get_array_index_none():
    config = Config({'foo': {'bar': [{'baz': 123}, {'baz': None}, {'baz': 231}]}})

    actual = config.get('foo.bar[1].baz')

    assert actual is None


def test_config_get_array_index_default():
    config = Config({'foo': {'bar': [{'baz': 123}, {'baz': None}, {'baz': 231}]}})

    actual = config.get('foo.bar[1].baz', 321)

    assert actual == 321


def test_config_get_array_index_negative():
    config = Config({'foo': {'bar': [{'baz': 123}, {'baz': 321}, {'baz': 231}]}})

    actual = config.get('foo.bar[-1].baz')

    assert actual == 231


def test_config_get_array_bad_index():
    config = Config({'foo': {'bar': [{'baz': 123}, {'baz': 321}, {'baz': 231}]}})

    with pytest.raises(ConfigException) as e:
        config.get('foo.bar[i].baz')

    assert str(e.value) == 'illegal slice [i]'


def test_config_get_array_index_out_of_range():
    config = Config({'foo': {'bar': [{'baz': 123}, {'baz': 321}, {'baz': 231}]}})

    with pytest.raises(ConfigException) as e:
        config.get('foo.bar[3].baz')

    assert str(e.value) == 'index out of range: 3'


def test_config_get_array_slice():
    config = Config({'foo': {'bar': [{'baz': i} for i in range(11)]}})

    actual = config.get('foo.bar[1:-1:2].baz')

    assert actual == [1, 3, 5, 7, 9]


def test_config_get_array_slice_none():
    config = Config({'foo': {'bar': [{'baz': None if i % 2 == 0 else i} for i in range(5)]}})

    actual = config.get('foo.bar[:].baz')

    assert actual == [None, 1, None, 3, None]


def test_config_get_array_slice_default():  # TODO: clarify behavior
    config = Config({'foo': {'bar': [{'baz': None if i % 2 == 0 else i} for i in range(5)]}})

    actual = config.get('foo.bar[:].baz', 321)

    assert actual == [None, 1, None, 3, None]


def test_config_get_array_bad_slice():
    config = Config({'foo': {'bar': [{'baz': 123}, {'baz': 321}, {'baz': 231}]}})

    with pytest.raises(ConfigException) as e:
        config.get('foo.bar[1:-s,1].baz')

    assert str(e.value) == 'illegal slice [1:-s,1]'


def test_config_get_array_bad_slice_pattern():
    config = Config({'foo': {'bar': [{'baz': 123}, {'baz': 321}, {'baz': 231}]}})

    with pytest.raises(ConfigException) as e:
        config.get('foo.bar[-1:0:-1:1].baz')

    assert str(e.value) == 'illegal slice [-1:0:-1:1]'


def test_config_get_array_inner():
    config = Config({'foo': {'bar': [{'baz': [{'tar': 1}]}, {'baz': [{'tar': 2}, {'tar': 3}]}]}})

    actual = config.get('foo.bar[].baz[].tar')

    assert actual == [[1], [2, 3]]


def test_config_get_not_iterable_node():
    config = Config({'foo': {'bar': {'baz': 123}}})

    with pytest.raises(ConfigException) as e:
        config.get('foo.bar[0].baz')

    assert str(e.value) == 'no config found for key "foo.bar[0].baz"'


def test_config_get_node_is_leaf():
    config = Config({'foo': {'bar': 'baz'}})

    with pytest.raises(ConfigException) as e:
        config.get('foo.bar.b')

    assert str(e.value) == 'no config found for key "foo.bar.b"'


def test_config_getattr():
    config = Config({'foo': {'bar': {'baz': 123}}})

    actual = config.foo.bar.baz

    assert actual == 123


def test_config_getattr_node():
    config = Config({'foo': {'bar': {'baz': 123, 'tar': '123'}}})

    actual = config.foo.bar

    assert actual == Config({'baz': 123, 'tar': '123'})


def test_config_getattr_missing_key():
    config = Config({'foo': {'bar': {'baz': 123}}})

    with pytest.raises(ConfigException) as e:
        _ = config.foo.bar.tar

    assert str(e.value) == 'no config found for key "tar"'


def test_config_getitem():
    config = Config({'foo': {'bar': {'baz': 123}}})

    actual = config['foo.bar.baz']

    assert actual == 123


def test_config_getitem_node():
    config = Config({'foo': {'bar': {'baz': 123}}})

    actual = config['foo.bar']

    assert actual == {'baz': 123}


def test_config_getitem_missing_key():
    config = Config({'foo': {'bar': {'baz': 123}}})

    with pytest.raises(ConfigException) as e:
        _ = config['foo.bar.tar']

    assert str(e.value) == 'no config found for key "foo.bar.tar"'


def test_config_equals():
    one = Config({'foo': {'bar': {'baz': 123}}})
    two = Config({'foo': {'bar': {'baz': 123}}})

    assert one == two


def test_config_not_equals():
    one = Config({'foo': {'bar': {'baz': 123}}})
    two = Config({'foo': {'bar': {'baz': 321}}})

    assert one != two


def test_config_as_dict():
    config = Config({'foo': {'bar': {'baz': 123, 'tar': '123'}}})

    actual = dict(config)

    assert actual == {'foo': {'bar': {'baz': 123, 'tar': '123'}}}


def samples_config_with_fallback():
    return [
        ({}, {}, {}),
        ({}, {'foo': 123}, {'foo': 123}),
        ({'foo': 123}, {}, {'foo': 123}),
        ({'foo': 123}, {'foo': 321}, {'foo': 123}),
        ({'foo': 123}, {'bar': 321}, {'foo': 123, 'bar': 321}),
        ({'a': {'foo': 123}}, {'a': {'bar': 321}}, {'a': {'foo': 123, 'bar': 321}}),
        ({'a': {'foo': 123}}, {'b': {'foo': 321}}, {'a': {'foo': 123}, 'b': {'foo': 321}}),
        ({'a': {'foo': {'baz': 123}}}, {'a': {'foo': 123}}, {'a': {'foo': {'baz': 123}}}),
        ({'a': {'foo': 123}}, {'a': {'foo': {'baz': 123}}}, {'a': {'foo': 123}}),
        ({'a': ['aa']}, {'a': ['bb']}, {'a': ['aa']}),
        ({'a': 123}, {'a': ['aa']}, {'a': 123}),
        ({'a': ['aa']}, {'a': 123}, {'a': ['aa']}),
        ({'a': {'foo': 123}}, {'a': ['aa']}, {'a': {'foo': 123}}),
        ({'foo': None}, {'foo': 123}, {'foo': None})
    ]


@pytest.mark.parametrize('config1, config2, expected', samples_config_with_fallback())
def test_config_with_fallback(config1, config2, expected):
    config1, config2 = Config(config1), Config(config2)

    actual = config1.with_fallback(config2)

    assert actual == Config(expected)


def test_config_with_fallback_not_fill_missing():
    config1 = Config({'foo': {'bar': 123}, 'bar': {'baz': 234}, 'baz': 345})
    config2 = Config({'foo': {'baz': 321}, 'bar': {'baz': 432}, 'taz': {'foo': 654}, 'zaz': 765})

    actual = config1.with_fallback(config2, fill_missing=False)

    assert actual == Config({'foo': {'bar': 123, 'baz': 321}, 'bar': {'baz': 234}, 'baz': 345})


def test_config_iter():
    config = Config({'foo': {'bar': {'baz': 123}, 'tar': [1, 2, {'taz': 3}, [{'taz': 4}, {'taz': 5}]]}})

    actual = list(config)

    assert actual == [
        'foo',
        'foo.bar',
        'foo.bar.baz',
        'foo.tar',
        'foo.tar[0]',
        'foo.tar[1]',
        'foo.tar[2]',
        'foo.tar[2].taz',
        'foo.tar[3]',
        'foo.tar[3][0]',
        'foo.tar[3][0].taz',
        'foo.tar[3][1]',
        'foo.tar[3][1].taz'
    ]


def test_config_has_key():
    config = Config({'foo': {'bar': {'baz': 123}, 'tar': [1, 2, {'taz': 3}, [4, 5]]}})

    assert 'foo.tar[3][0]' in config


def test_config_has_key_not():
    config = Config({'foo': {'bar': {'baz': 123}, 'tar': [1, 2, {'taz': 3}, [4, 5]]}})

    assert 'foo.tar[2].baz' not in config


def samples_config_resolve():
    return [
        (
            {'exp': 'foo', 'foo': 123},
            {'exp': 'foo', 'foo': 123}
        ), (
            {'exp': '${foo}', 'foo': 123},
            {'exp': 123, 'foo': 123}
        ), (
            {'exp': '${foo.bar}', 'foo': {'bar': '123'}},
            {'exp': '123', 'foo': {'bar': '123'}}
        ), (
            {'exp': '${foo.bar}', 'foo': {'bar': 123.456}},
            {'exp': 123.456, 'foo': {'bar': 123.456}}
        ), (
            {'exp': '${foo}', 'foo': {'bar': 123.456}},
            {'exp': {'bar': 123.456}, 'foo': {'bar': 123.456}}
        ), (
            {'exp': '$${foo.bar}', 'foo': {'bar': '123'}},
            {'exp': '123', 'foo': {'bar': '123'}}  # TODO: should be '${foo.bar}' ???
        ), (
            {'exp': 'aa-${foo.bar}', 'foo': {'bar': 123}},
            {'exp': 'aa-123', 'foo': {'bar': 123}}
        ), (
            {'exp': '${foo.bar}-aa', 'foo': {'bar': '123'}},
            {'exp': '123-aa', 'foo': {'bar': '123'}}
        ), (
            {'exp': 'aa-${foo.bar}-aa', 'foo': {'bar': '123'}},
            {'exp': 'aa-123-aa', 'foo': {'bar': '123'}}
        ), (
            {'exp': 'aa-${foo.bar}-aa-${foo.bar}', 'foo': {'bar': '123'}},
            {'exp': 'aa-123-aa-123', 'foo': {'bar': '123'}}
        ), (
            {'exp': 'aa-${foo.bar}-aa-${foo.bar}-aa', 'foo': {'bar': '123'}},
            {'exp': 'aa-123-aa-123-aa', 'foo': {'bar': '123'}}
        ), (
            {'exp': 'aa-${foo.bar}-aa-${baz}-aa', 'foo': {'bar': '123'}, 'baz': 321},
            {'exp': 'aa-123-aa-321-aa', 'foo': {'bar': '123'}, 'baz': 321}
        ), (
            {'exp': '${foo}', 'foo': '${bar}', 'bar': 123},
            {'exp': 123, 'foo': 123, 'bar': 123}
        ), (
            {'exp': '${bar}', 'bar': {'baz': '${taz}'}, 'taz': 123},
            {'exp': {'baz': 123}, 'bar': {'baz': 123}, 'taz': 123}
        ), (
            {'exp': '${bar[2]}', 'bar': [11, 22, 33, 44]},
            {'exp': 33, 'bar': [11, 22, 33, 44]}
        ), (
            {'exp': '${foo[1:3]}', 'foo': [11, 22, 33, 44]},
            {'exp': [22, 33], 'foo': [11, 22, 33, 44]}
        ), (
            {'exp': '${foo[].bar}', 'foo': [{'bar': 11}, {'bar': 22}, {'bar': 33}]},
            {'exp': [11, 22, 33], 'foo': [{'bar': 11}, {'bar': 22}, {'bar': 33}]}
        ), (
            {'exp': '${foo[1][0]}', 'foo': [[10, 11, 12], [20, 21, 22]]},
            {'exp': 20, 'foo': [[10, 11, 12], [20, 21, 22]]}
        ), (
            {'exp': '${foo}', 'foo': [1, 2, 3]},
            {'exp': [1, 2, 3], 'foo': [1, 2, 3]}
        ), (
            {'exp': ['${foo[2]}', '${foo[0]}'], 'foo': [1, 2, 3]},
            {'exp': [3, 1], 'foo': [1, 2, 3]},
        ), (
            {'exp': {'foo': '${foo}'}, 'foo': 123},
            {'exp': {'foo': 123}, 'foo': 123}
        ), (
            {'exp': '${foo?123}'},
            {'exp': 123}
        ), (
            {'exp': '${foo?bar}'},
            {'exp': 'bar'}
        ), (
            {'exp': '${foo?}'},
            {'exp': ''}
        ), (
            {'exp': '${foo?bar}', 'bar': 123},
            {'exp': 'bar', 'bar': 123}
        ), (
            {'exp': '${foo|bar}', 'foo': 123, 'bar': 456},
            {'exp': 123, 'foo': 123, 'bar': 456}
        ), (
            {'exp': '${foo|bar}', 'bar': 123},
            {'exp': 123, 'bar': 123}
        ), (
            {'exp': '${foo|bar|baz?True}'},
            {'exp': True}
        ), (
            {'exp': '${foo|bar|baz?True}', 'bar': 123, 'baz': 456},
            {'exp': 123, 'bar': 123, 'baz': 456}
        ), (
            {'exp': '${foo|bar|baz?True}', 'foo': [1, 2, 3]},
            {'exp': [1, 2, 3], 'foo': [1, 2, 3]}
        ), (
            {'exp': '${foo.bar|baz.foo}', 'foo': {'bar': 123}, 'baz': {'foo': 456}},
            {'exp': 123, 'foo': {'bar': 123}, 'baz': {'foo': 456}}
        ), (
            {'exp': '${foo.bar|baz.foo}', 'foo': {'baz': 123}, 'baz': {'foo': 456}},
            {'exp': 456, 'foo': {'baz': 123}, 'baz': {'foo': 456}}
        ), (
            {'exp': '${foo[::-1]|baz.foo}', 'foo': [1, 2, 3]},
            {'exp': [3, 2, 1], 'foo': [1, 2, 3]}
        )
    ]


@pytest.mark.parametrize('config, expected', samples_config_resolve())
def test_config_resolve(config, expected):
    config = Config(config)

    actual = config.resolve()

    assert actual == Config(expected)


def samples_config_resolve_with_missing():
    return [
        {'exp': '${foo}'},
        {'exp': '${foo.bar}'},
        {'exp': '${foo[0]}'},
        {'exp': '${foo[0].bar}'},
        {'exp': '${foo|bar}'},
        {'exp': '${foo|bar|baz}'},
        {'exp': '${foo[0]|bar[0]}'}
    ]


@pytest.mark.parametrize('config', samples_config_resolve_with_missing())
def test_config_resolve_with_missing(config):
    config = Config(config)

    with pytest.raises(ConfigException):
        config.resolve()


def test_config_resolve_with_loop():
    config = Config({'exp': '${foo}', 'foo': '${bar}', 'bar': '${foo}'})

    with pytest.raises(RecursionError):
        config.resolve()


def test_config_factory_empty():
    actual = ConfigFactory.empty()

    assert actual == Config({})


def test_config_factory_system_environments():
    with mock.patch.dict(os.environ, {'FOO': 'BAR'}, clear=True):
        actual = ConfigFactory.system_environments()

        assert actual == Config({'envs': {'FOO': 'BAR'}})


def samples_config_factory_arguments():
    return [
        (
            ['--foo', '123'],
            {'args': {'foo': 123}}
        ), (
            ['--foo', '"123"'],
            {'args': {'foo': '123'}}
        ), (
            ['--foo.bar', '123'],
            {'args': {'foo': {'bar': 123}}}
        ), (
            ['--foo', 'text'],
            {'args': {'foo': 'text'}}
        ), (
            ['--foo', 'True'],
            {'args': {'foo': True}}
        ), (
            ['--foo', 'true'],
            {'args': {'foo': 'true'}}
        ), (
            ['--foo', '"True"'],
            {'args': {'foo': 'True'}}
        ), (
            ['--foo.bar.baz', '123'],
            {'args': {'foo': {'bar': {'baz': 123}}}}
        ), (
            ['--foo.bar', '123', '--foo.baz', '"321"'],
            {'args': {'foo': {'bar': 123, 'baz': '321'}}}
        ), (
            ['--foo', ''],
            {'args': {'foo': ''}}
        ), (
            ['--foo', 'None'],
            {'args': {'foo': None}}
        ), (
            ['--foo.bar', '[1,2,3]'],
            {'args': {'foo': {'bar': [1, 2, 3]}}}
        ), (
            ['--foo.bar', '["1"]'],
            {'args': {'foo': {'bar': ['1']}}}
        ), (
            ['--foo.bar', '{"baz": 123}'],
            {'args': {'foo': {'bar': {'baz': 123}}}}
        ), (
            ['--foo.bar', '{"baz": "123"}'],
            {'args': {'foo': {'bar': {'baz': '123'}}}}
        ), (
            ['--foo', '1.2'],
            {'args': {'foo': 1.2}}
        ), (
            ['--foo', '"1.2"'],
            {'args': {'foo': '1.2'}}
        ), (
            ['--foo', 'John Doe'],
            {'args': {'foo': 'John Doe'}}
        )
    ]


@pytest.mark.parametrize('argv, expected', samples_config_factory_arguments())
def test_config_factory_arguments(argv, expected):
    with mock.patch.object(sys, 'argv', ['test.py'] + argv):
        actual = ConfigFactory.arguments()

        assert actual == Config(expected)


def test_config_factory_default_application():
    with mock.patch.dict(os.environ, {'FOO': 'BAR', 'BAZ': '${args.bar}'}, clear=True), \
            mock.patch.object(sys, 'argv', ['test.py', '--foo', '${envs.FOO}', '--bar', '123']):
        actual = ConfigFactory.default_application()

        assert actual == Config({'envs': {'FOO': 'BAR', 'BAZ': 123}, 'args': {'foo': 'BAR', 'bar': 123}})


def test_config_factory_from_file():
    with mock.patch('builtins.open', mock.mock_open(read_data='{"foo": "bar"}')) as mock_file:
        actual = ConfigFactory.from_file('config.json')

        assert actual == Config({'foo': 'bar'})
        mock_file.assert_called_once_with('config.json', encoding='utf-8')


def test_config_factory_from_file_with_node():
    with mock.patch('builtins.open', mock.mock_open(read_data='{"foo": "bar"}')) as mock_file:
        actual = ConfigFactory.from_file('config.json', node='a.b.c')

        assert actual == Config({'a': {'b': {'c': {'foo': 'bar'}}}})
        mock_file.assert_called_once_with('config.json', encoding='utf-8')


def test_config_factory_file_not_found():
    with mock.patch('builtins.open', mock.mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError

        with pytest.raises(FileNotFoundError):
            ConfigFactory.from_file('config.json')


def test_config_factory_unsupported_file_type():
    with mock.patch('builtins.open', mock.mock_open(read_data='foo: bar')) as mock_file:
        with pytest.raises(ConfigException, match='no format parser found for file config.yaml'):
            ConfigFactory.from_file('config.yaml')

        mock_file.assert_not_called()


def test_config_factory_load():
    with mock.patch('pyboost.config.ConfigFactory.default_application', return_value=Config({'foo': 'bar'})), \
            mock.patch('builtins.open', mock.mock_open(read_data='{"bar": 123}')) as mock_file:
        actual = ConfigFactory.load('config.json')

        assert actual == Config({'foo': 'bar', 'bar': 123})
        mock_file.assert_called_once_with('config.json', encoding='utf-8')


def test_config_factory_default_load():
    with mock.patch('pyboost.config.ConfigFactory.default_application', return_value=Config({'foo': 'bar'})), \
            mock.patch('builtins.open', mock.mock_open(read_data='{"bar": 123}')) as mock_file:
        actual = ConfigFactory.default_load()

        assert actual == Config({'bar': 123, 'foo': 'bar'})
        mock_file.assert_called_once_with('application.json', encoding='utf-8')


def test_config_factory_default_load_not_found():
    with mock.patch('pyboost.config.ConfigFactory.load') as mock_load:
        mock_load.side_effect = FileNotFoundError, ConfigException, Config({'foo': 'bar'})

        actual = ConfigFactory.default_load()

        assert actual == Config({'foo': 'bar'})
        mock_load.assert_has_calls([
            mock.call('application.json'), mock.call('application.ini'), mock.call('application.properties')
        ])


def test_config_factory_default_load_use_arguments():
    with mock.patch('pyboost.config.ConfigFactory.load') as mock_load, \
            mock.patch('pyboost.config.ConfigFactory.arguments') as mock_arguments:
        mock_load.side_effect = [
            FileNotFoundError, ConfigException, FileNotFoundError, ConfigException, Config({'foo': 'bar'})
        ]
        mock_arguments.return_value = Config({'args': {'config_file': 's3://bucket/config.json'}})

        actual = ConfigFactory.default_load()

        assert actual == Config({'foo': 'bar'})
        mock_load.assert_has_calls([
            mock.call('application.json'), mock.call('application.ini'), mock.call('application.properties'),
            mock.call('application.yaml'), mock.call('s3://bucket/config.json')
        ])


def test_local_file_config_reader():
    with mock.patch('builtins.open', mock.mock_open(read_data='foo')) as mock_file:
        reader = LocalFileConfigReader()

        actual = reader.read('file_path')

        assert actual == 'foo'
        mock_file.assert_called_once_with('file_path', encoding='utf-8')


def test_local_file_config_reader_test():
    assert LocalFileConfigReader.test('file_path') is True


def test_config_reader_find_subclass_local_file():
    actual = ConfigReader.find_subclass('file_path')

    assert actual.is_present()
    assert isinstance(actual.get(), LocalFileConfigReader)


def test_json_config_parser():
    parser = JsonConfigParser()

    actual = parser.parse('{"foo": "bar"}')

    assert actual == {'foo': 'bar'}


def test_json_config_parser_test():
    assert JsonConfigParser.test('foo.json') is True
    assert JsonConfigParser.test('s3://bucket/foo.json') is True
    assert JsonConfigParser.test('foo.yaml') is False


def test_ini_config_parser():
    parser = IniConfigParser()

    actual = parser.parse('[foo]\nbar = 123')

    assert actual == {'foo': {'bar': '123'}}


def test_ini_config_parser_test():
    assert IniConfigParser.test('foo.ini') is True
    assert IniConfigParser.test('s3://bucket/foo.ini') is True
    assert IniConfigParser.test('foo.yaml') is False


def test_config_parser_find_subclass_json():
    actual = ConfigParser.find_subclass('foo.json')

    assert actual.is_present()
    assert isinstance(actual.get(), JsonConfigParser)


def test_config_parser_find_subclass_ini():
    actual = ConfigParser.find_subclass('foo.ini')

    assert actual.is_present()
    assert isinstance(actual.get(), IniConfigParser)


def test_config_parser_find_subclass_unknown():
    actual = ConfigParser.find_subclass('foo.yaml')

    assert actual.is_empty()
