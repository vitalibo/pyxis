from __future__ import annotations

import functools
from typing import Callable, Optional, TypeVar, overload

__all__ = [
    'require_not_none',
    'is_none',
    'not_none',
    'identity',
    'function',
    'unpack',
    'return_values_as',
    'SingletonMeta'
]

T = TypeVar('T')
R = TypeVar('R')


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


def identity(obj: T) -> T:
    """
    Function that always returns its input argument
    """

    return obj


def unpack(f: Callable) -> Callable:
    """
    A decorator that unpacks the input argument and passes it to the decorated function.
    """

    @functools.wraps(f)
    def wrap(value):
        return f(*value)

    return wrap


def return_values_as(mapper):
    """
    Decorator that materializes the return value of a generation function.

    >>> @return_values_as(list)
    >>> def foo():
    >>>     yield 1
    >>>     yield 2
    >>>
    >>> assert foo() == [1, 2]
    """

    def inner(func):
        @functools.wraps(func)
        def wraps(*argv, **kwargs):
            return mapper(func(*argv, **kwargs))

        return wraps

    require_not_none(mapper)
    return inner


class SingletonMeta(type):
    """
    A metaclass that can be used to create classes with only one instance.

    >>> class MyClass(metaclass=SingletonMeta):
    >>>    pass
    """

    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


class function:  # pylint: disable=invalid-name
    """
    Represents a function that accepts one or more arguments and produces a result.
    """

    def __init__(self, this: Callable[[T], R]):
        self._this = require_not_none(this)

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)

    def __rshift__(self, other: Callable) -> function:
        return self.and_then(other)

    def __lshift__(self, other: Callable) -> function:
        return self.compose(other)

    def compose(self, other: Callable) -> function:
        """
        Returns a composed function that first applies the other function to its input,
        and then applies this function to the result.
        """

        return function(lambda *args, **kwargs: self._this(require_not_none(other)(*args, **kwargs)))

    def and_then(self, other: Callable) -> function:
        """
        Returns a composed function that first applies this function to its input,
        and then applies the other function to the result.
        """

        return function(lambda *args, **kwargs: require_not_none(other)(self._this(*args, **kwargs)))

    def apply(self, *args, **kwargs):
        """
        Applies this function to the given arguments.
        """

        return self._this(*args, **kwargs)
