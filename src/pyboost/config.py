from __future__ import annotations

import abc
import argparse
import ast
import inspect
import os
import re
import sys
from typing import Dict, List, TypeVar, overload, Optional, Any

from pyboost.functions import function, require_not_none
from pyboost.option import Option

__all__ = [
    'Config',
    'ConfigFactory',
    'ConfigException',
    'ConfigReader',
    'ConfigParser',
    'ConfigValueResolver'
]

T = TypeVar('T')


class Config:
    """
    The Config class is a configuration class that wraps a Python dictionary. It provides several methods for
    accessing and manipulating configuration values. The Config class is immutable and thread-safe.
    """

    def __init__(self, root):
        self.__root = root

    @overload
    def get(self, key: str) -> Optional[T]:
        ...

    @overload
    def get(self, key: str, default: T) -> T:
        ...

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """
        Get the value associated with a specific key in the configuration tree.

        :param key: the key to retrieve the value for
        :param default: the default value to return if the value is None
        :return: the value associated with the specified key, or the default value
        """

        def traverse(root, nodes):
            while nodes:  # pylint: disable=too-many-nested-blocks
                path = nodes.pop(0)
                if isinstance(root, Dict) and path in root:
                    root = root.get(path)
                elif isinstance(root, List) and path.startswith('[') and path.endswith(']'):
                    path = path[1:-1]
                    try:
                        if re.match(r'^[-0-9]*:[-0-9]*:?[-0-9]*$', path) or path == '':
                            # append the ':::' string to the path string before splitting to ensure that
                            # we get at least three parts
                            params = [int(x) if x else None for x in (path + ':::').split(':')[:3]]
                            return [traverse(x, list(nodes)) for x in root[slice(*params)]]

                        root = root[int(path)]
                    except IndexError as e:
                        raise ConfigException(f'index out of range: {path}') from e
                    except ValueError as e:
                        raise ConfigException(f'illegal slice [{path}]') from e
                else:
                    raise ConfigException(f'no config found for key "{key}"')
            return root

        return Option \
            .of_nullable(traverse(self.__root, key.replace('[', '.[').split('.'))) \
            .or_else(default)

    @overload
    def with_fallback(self, other: Config) -> Config:
        ...

    def with_fallback(self, other: Config, fill_missing: bool = True) -> Config:
        """
        Returns a new Config that contains the values of this Config, with missing values filled in by the fallback
        Config. If a key is present in both Configs, the value from this Config is used.

        :param other: a Config to use as the fallback for missing values in this Config
        :param fill_missing: should be filled in missing values
        :return: a new Config
        """

        def merge(dict1, dict2, use_dict2):
            for key in set(dict1.keys()).union(dict2.keys()):
                if key in dict1 and key in dict2:
                    if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                        yield key, dict(merge(dict1[key], dict2[key], True))
                    else:
                        yield key, dict1[key]
                elif key in dict1:
                    yield key, dict1[key]
                elif use_dict2:
                    yield key, dict2[key]

        return Config(dict(merge(self.__root, other.__root, fill_missing)))  # pylint: disable=protected-access

    def resolve(self) -> Config:
        """
        Returns a new `Config` object with all resolved values. Performs a depth-first traversal of the Config tree
        and resolves string values using the appropriate resolver.
        """

        def traversal(path, node):
            if isinstance(node, str):
                return ConfigValueResolver.find_subclass(node) \
                    .map(lambda x: traversal(path, x.resolve(self, path[1:], node))) \
                    .or_else(node)
            elif isinstance(node, dict):
                return {key: traversal(f'{path}{key}', value) for key, value in node.items()}
            elif isinstance(node, list):
                return [traversal(f'{path}[{i}]', value) for i, value in enumerate(node)]
            else:
                return node

        return Config(traversal('.', self.__root))

    def keys(self) -> List[str]:
        # workaround for creating a dict from a config object
        return self.__root.keys()

    def __getattr__(self, item):
        value = self.get(item)
        if isinstance(value, Dict):
            return Config(value)
        return value

    def __getitem__(self, item):
        return self.get(item)

    def __iter__(self):
        """
        Returns an iterator over all flatten keys in the Config.
        """

        def traversal(path, nodes):
            for key, value in nodes:
                yield path + key
                if isinstance(value, Dict):
                    yield from traversal(path + key + '.', value.items())
                if isinstance(value, List):
                    yield from traversal(path + key, ((f'[{i}]', item) for i, item in enumerate(value)))

        return iter(traversal('', self.__root.items()))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Config):
            return False

        return self.__root == other.__root  # pylint: disable=protected-access

    def __repr__(self):
        return repr(self.__root)


class ConfigFactory:
    """ Contains static methods to create `Config` objects. """

    @staticmethod
    def default_load() -> Config:
        """
        Loads default application configuration
        """

        for extension in ['json', 'yaml', 'ini', 'properties']:
            try:
                return ConfigFactory.load(f'application.{extension}')
            except (ConfigException, FileNotFoundError):
                pass

        config = ConfigFactory.arguments()
        return ConfigFactory.load(config.args.config_file)

    @staticmethod
    def load(path: str) -> Config:
        """
        Loads an application configuration from the given file path
        """

        return ConfigFactory.default_application() \
            .with_fallback(ConfigFactory.from_file(path)) \
            .resolve()

    @staticmethod
    def from_file(path: str, node: Optional[str] = None) -> Config:
        """
        Loads a configuration from the given file path.

        :param path: to the configuration file
        :param node: path to the node of the `Config` that should be returned
        :return: a `Config` object
        """

        reader = ConfigReader.find_subclass(path) \
            .or_else_raise(ConfigException, f'no reader found for file {path}')
        parser = ConfigParser.find_subclass(path) \
            .or_else_raise(ConfigException, f'no format parser found for file {path}')
        config = parser.parse(reader.read(require_not_none(path)))

        if node is not None:
            for name in node.split('.')[::-1]:
                config = {name: config}
        return Config(config)

    @staticmethod
    def default_application() -> Config:
        """
        Returns a `Config` object with the default application configuration.
        """

        return ConfigFactory.arguments() \
            .with_fallback(ConfigFactory.system_environments()) \
            .resolve()

    @staticmethod
    def system_environments() -> Config:
        """
        Parses the environment variables and returns them as a `Config` object.
        """

        envs = {}
        for key, value in os.environ.items():
            envs[key] = value

        return Config({'envs': envs})

    @staticmethod
    def arguments() -> Config:
        """
        Parse command line arguments and return a `Config` object.
        """

        parser = argparse.ArgumentParser()
        for var in sys.argv:
            if var.startswith('--'):
                parser.add_argument(var)
        parsed, _ = parser.parse_known_args(sys.argv)

        args = {}
        for name, value in vars(parsed).items():
            keys = name.split('.')
            cell = args
            for key in keys[:-1]:
                cell = cell.setdefault(key, {})
            key = keys[-1]
            try:
                cell[key] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                cell[key] = value

        return Config({'args': args})

    @staticmethod
    def empty() -> Config:
        """
        Create an empty `Config` object.
        """

        return Config({})


class ConfigException(Exception):
    """ Base exception for all configuration related exceptions. """


class _SubclassRegistryMeta(abc.ABCMeta):
    """
    A metaclass that maintains a registry of subclasses and provides a way to look up an instance of a subclass based
    on some criteria. Requires that any subclass that is not abstract must implement a method called `test` and
    may define a `priority` attribute to control the order in which they are tested by the `find_subclass` method.
    """

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__instances = {}
        if not inspect.isabstract(cls) and 'test' not in cls.__dict__:
            raise TypeError(f'Class {cls.__name__} must implement test method')

    def find_subclass(cls, *args, **kwargs):
        for subclass in sorted(cls.__subclasses__(), key=lambda x: getattr(x, 'priority', 100)):
            if subclass.test(*args, **kwargs):
                return Option.of(cls.__instances.setdefault(subclass, subclass()))
        return Option.empty()


class ConfigReader(metaclass=_SubclassRegistryMeta):
    """
    An abstract base class for reading configuration files.
    """

    @abc.abstractmethod
    def read(self, path: str) -> str:
        """
        Reads the configuration from the given path and returns the content as a string.
        """


class ConfigParser(metaclass=_SubclassRegistryMeta):
    """
    An abstract base class for parsing configuration.
    """

    @abc.abstractmethod
    def parse(self, content: str) -> Dict:
        """
        Parses the given content and returns a dictionary of configuration values.
        """


class ConfigValueResolver(metaclass=_SubclassRegistryMeta):
    """
    An abstract base class for resolving `Config` values.
    """

    @abc.abstractmethod
    def resolve(self, config: Config, key: str, value: str) -> Any:
        """
        Returns resolved value for given string.
        """


class LocalFileConfigReader(ConfigReader):
    """
    Reads configuration from local file system.
    """

    priority = 200
    test = function(lambda x: True)

    def read(self, path: str) -> str:
        with open(path, encoding='utf-8') as f:
            return f.read()


class JsonConfigParser(ConfigParser):
    """
    A configuration parser that uses JSON.
    """

    test = function(lambda x: x.endswith('.json'))

    def parse(self, content: str) -> dict:
        import json  # pylint: disable=import-outside-toplevel
        return json.loads(content)


class IniConfigParser(ConfigParser):
    """
    A configuration parser that uses INI.
    """

    test = function(lambda x: x.endswith('.ini'))

    def parse(self, content: str) -> dict:
        import configparser  # pylint: disable=import-outside-toplevel
        parser = configparser.ConfigParser()
        parser.read_string(content)

        config = {}
        for section in parser.sections():
            keys = section.split('.')
            cell = config
            for key in keys[:-1]:
                cell = cell.setdefault(key, {})
            key = keys[-1]
            cell[key] = dict(parser[section])

        return config


class YamlConfigParser(ConfigParser):
    """
    A configuration parser that uses YAML.
    """

    test = function(lambda x: x.endswith('.yaml') or x.endswith('.yml'))

    def parse(self, content: str) -> dict:
        import yaml  # pylint: disable=import-outside-toplevel
        return yaml.safe_load(content)


class ConfigValueReferenceResolver(ConfigValueResolver):
    """
    Resolves references to other values within the Config using the syntax `${key.subkey}`
    """

    priority = 10
    test = function(lambda x: '${' in x and '}' in x and x.index('${') < x.index('}'))

    def resolve(self, config: Config, key: str, value: str) -> Any:
        def parse(string):
            while string:
                pos = string.find('$')
                if pos < 0:
                    yield string
                    return
                if pos > 0:
                    yield string[:pos]
                    string = string[pos:]

                chr = string[1:2]  # noqa pylint: disable=redefined-builtin
                if chr == '$':
                    yield '$'
                    string = string[2:]
                elif chr == '{':
                    ref_key = re.compile(r'\$\{([^}]+)}')
                    match = ref_key.match(string)
                    if match is None:
                        raise ConfigException(f'bad substitution variable reference {string}')
                    path = match.group(1)
                    string = string[match.end():]
                    yield get(path)

        def get(expr):
            *paths, expr = expr.split('|')
            for path in paths:
                try:
                    return config.get(path)
                except ConfigException:
                    pass

            path, *default = expr.split('?', 1)
            try:
                return config.get(path)
            except ConfigException as e:
                if not default:
                    raise e
                try:
                    return ast.literal_eval(default[0])
                except (ValueError, SyntaxError):
                    return default[0]

        itr = iter(parse(value))
        result = next(itr)
        for item in itr:
            if isinstance(item, (Dict, List)):
                raise ConfigException('can not substitute composite type')
            result = str(result) + str(item)
        return result
