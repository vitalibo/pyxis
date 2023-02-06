from __future__ import annotations

from typing import (
    Generic, TypeVar, Callable, overload
)

__all__ = [
    'Optional'
]

from .objects import require_not_none

T = TypeVar('T')
U = TypeVar('U')


class Optional(Generic[T]):
    """ A container object which may or may not contain a non-none value """

    def __init__(self, value: T) -> None:
        self.__value = value

    @staticmethod
    def empty() -> Optional[T]:
        return _Empty()

    def filter(self, predicate: Callable[[T], bool]) -> Optional[T]:
        require_not_none(predicate)

        if self.is_empty():
            return self.empty()

        if predicate(self.__value):
            return self
        else:
            return self.empty()

    def flat_map(self, mapper: Callable[[T], Optional[U]]) -> Optional[U]:
        require_not_none(mapper)

        if self.is_empty():
            return self.empty()

        return mapper(self.__value)

    def get(self) -> T:
        if self.is_empty():
            raise ValueError('No value present')

        return self.__value

    def if_present(self, action: Callable[[T], None]) -> None:
        require_not_none(action)

        if self.is_present():
            action(self.__value)

    def if_present_or_else(self, action: Callable[[T], None], empty_action: Callable[[], None]) -> None:
        require_not_none(action)
        require_not_none(empty_action)

        if self.is_present():
            action(self.__value)
        else:
            empty_action()

    def is_empty(self) -> bool:
        return self.__value is None

    def is_present(self) -> bool:
        return self.__value is not None

    def map(self, mapper: Callable[[T], U]) -> Optional[U]:
        require_not_none(mapper)

        if self.is_empty():
            return self.empty()

        return Optional.of_nullable(mapper(self.__value))

    @staticmethod
    def of(value: T) -> Optional[T]:
        return Optional(require_not_none(value))

    @staticmethod
    def of_nullable(value: T) -> Optional[T]:
        if value is None:
            return Optional.empty()
        else:
            return Optional(value)

    def __or__(self, other: Optional[T]) -> Optional[T]:
        if self.is_present():
            return self
        else:
            return other

    def or_else(self, other: T) -> T:
        if self.is_present():
            return self.__value
        else:
            return other

    def or_else_get(self, supplier: Callable[[], T]) -> T:
        require_not_none(supplier)

        if self.is_present():
            return self.__value
        else:
            return supplier()

    @overload
    def or_else_raise(self) -> T:
        ...

    @overload
    def or_else_raise(self, supplier: Callable[[], Exception]) -> T:
        ...

    def or_else_raise(self, supplier: Callable[[], Exception] = None) -> T:
        if self.is_present():
            return self.__value

        if supplier is None:
            raise ValueError('No value present')
        raise supplier()

    def __bool__(self):
        return self.is_present()

    def __eq__(self, other) -> bool:
        if isinstance(other, Optional):
            return self.__value == other.__value  # pylint: disable=protected-access
        return False

    def __hash__(self):
        return hash(self.__value)

    def __repr__(self):
        return f'Optional({repr(self.__value)})'


class _Empty(Optional):
    """ Common instance of Optional for empty value """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = Optional(None)
        return cls.__instance

    def is_empty(self) -> bool:
        return True

    def is_present(self) -> bool:
        return False
