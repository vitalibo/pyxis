__all__ = [
    'require_not_none',
    'is_none',
    'not_none',
    'identity'
]

from typing import TypeVar, overload, Optional

T = TypeVar('T')


@overload
def require_not_none(obj: T) -> T: ...


@overload
def require_not_none(obj: T, msg: str) -> T: ...


def require_not_none(obj: T, msg: Optional[str] = None) -> T:
    """ Checks that the specified object reference is not None """

    if obj is None:
        if msg is None:
            raise ValueError()
        raise ValueError(msg)
    return obj


def is_none(obj: T) -> bool:
    """ Returns True if the provided reference is None otherwise returns False """

    return obj is None


def not_none(obj: T) -> bool:
    """ Returns True if the provided reference is not None otherwise returns False """

    return obj is not None


def identity(obj: T) -> T:
    """ Function that always returns its input argument """

    return obj
