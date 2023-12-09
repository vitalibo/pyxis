import json
import os

from pyboost.functions import require_not_none


def resource(root: str, path: str) -> str:
    """
    Returns an absolute path to a resource.

    >>> absolute_path = resource(__file__, 'foo/bar.txt')
    """

    return os.path.join(os.path.dirname(
        require_not_none(root, 'root')), require_not_none(path, 'path'))


def resource_as_str(root: str, path: str, encoding: str = 'utf-8', **kwargs) -> str:
    """
    Returns a resource as a string.

    >>> content = resource_as_str(__file__, 'foo/bar.txt')
    """

    with open(resource(root, path), 'r', encoding=encoding) as f:
        return f.read()


def resource_as_json(root: str, path: str, **kwargs):
    """
    Returns a resource as a json object.

    >>> content = resource_as_json(__file__, 'foo/bar.json')
    """

    return json.loads(resource_as_str(root, path, **kwargs), **kwargs)


def resource_as_json_str(root: str, path: str, **kwargs) -> str:
    """
    Returns a resource as a json string.

    >>> content:str = resource_as_json_str(__file__, 'foo/bar.json')
    """

    return json.dumps(resource_as_json(root, path, **kwargs), **kwargs)
