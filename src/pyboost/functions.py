__all__ = [
    'require_not_none',
    'is_none',
    'not_none',
    'field_ref',
    'identity'
]

from typing import Optional, TypeVar, overload

T = TypeVar('T')


@overload
def require_not_none(obj: T) -> T: ...


@overload
def require_not_none(obj: T, msg: str) -> T: ...


def require_not_none(obj: T, msg: Optional[str] = None) -> T:
    """
    Checks that the specified object reference is not None
    """

    if obj is None:
        if msg is None:
            raise ValueError()
        raise ValueError(msg)
    return obj


def is_none(obj: T) -> bool:
    """
    Returns True if the provided reference is None otherwise returns False
    """

    return obj is None


def not_none(obj: T) -> bool:
    """
    Returns True if the provided reference is not None otherwise returns False
    """

    return obj is not None


def field_ref(cls):
    """
    Decorator to enrich field reference to dataclasses
    """

    def wraps(name):
        def func(self):
            return getattr(self, name)

        return func

    for field in cls.__dataclass_fields__.values():
        setattr(cls, field.name, wraps(field.name))
    return cls


def identity(obj: T) -> T:
    """
    Function that always returns its input argument
    """

    return obj
