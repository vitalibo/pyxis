import json
import os

from pyxis.functions import require_not_none


def absolute(root: str, path: str) -> str:
    """
    Returns an absolute path to a resource.

    >>> absolute_path = absolute(__file__, 'foo/bar.txt')
    """

    return os.path.join(os.path.dirname(require_not_none(root, 'root')), require_not_none(path, 'path'))


def load_text(root: str, path: str, encoding: str = 'utf-8', **kwargs) -> str:
    """
    Returns a resource as a string.

    >>> content = load_text(__file__, 'foo/bar.txt')
    """

    with open(absolute(root, path), encoding=encoding) as f:
        return f.read()


def load_json(root: str, path: str, **kwargs):
    """
    Returns a json resource as an object.

    >>> content = load_json(__file__, 'foo/bar.json')
    """

    return json.loads(load_text(root, path, **kwargs), **kwargs)


def load_json_as_text(root: str, path: str, **kwargs) -> str:
    """
    Returns a json resource as a json string.

    >>> content: str = load_json_as_text(__file__, 'foo/bar.json')
    """

    return json.dumps(load_json(root, path, **kwargs), **kwargs)


def load_yaml(root: str, path: str, **kwargs):
    """
    Returns a yaml resource as an object.

    >>> content = load_yaml(__file__, 'foo/bar.yaml')
    """

    import yaml  # noqa: PLC0415

    return yaml.safe_load(load_text(root, path, **kwargs))


def load_yaml_all(root: str, path: str, **kwargs):
    """
    Returns a yaml resource as an array of objects.

    >>> content = load_yaml_all(__file__, 'foo/bar.yaml')
    """

    import yaml  # noqa: PLC0415

    return list(yaml.safe_load_all(load_text(root, path, **kwargs)))
