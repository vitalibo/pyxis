import functools
from typing import Optional, TypeVar, overload, Callable

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


def function(f: Callable) -> Callable:
    """
    A decorator that simply returns the input function, useful for creating higher-order functions.
    """
    return f


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
