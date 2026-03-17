from __future__ import annotations

from typing import Any, Callable, Generic, Optional, TypeVar, overload

from pyxis.functions import require_not_none

__all__ = ['Option']

T_co = TypeVar('T_co', covariant=True)
U = TypeVar('U')


class Option(Generic[T_co]):
    """
    A container object which may or may not contain a non-none value. If a value is present, is_present() returns True.
    If no value is present, the object is considered empty and is_present() returns False.
    """

    def __init__(self, value: T_co) -> None:
        self.__value = value

    @staticmethod
    def empty() -> Option[Any]:
        """
        Returns an empty Option instance. No value is present for this Option.

        :return: an empty Option
        """

        return _Empty()

    def filter(self, predicate: Callable[[T_co], bool]) -> Option[T_co]:
        """
        If a value is present, and the value matches the given predicate, returns an Option describing the value,
        otherwise returns an empty Option.

        :param predicate: the predicate to apply to a value, if present
        :return: an Option describing the value of this Option, if a value is present and the value matches
        the given predicate, otherwise an empty Option
        """

        require_not_none(predicate)

        if self.is_empty():
            return self.empty()

        if predicate(self.__value):
            return self

        return self.empty()

    def flat_map(self, mapper: Callable[[T_co], Option[U]]) -> Option[U]:
        """
        If a value is present, returns the result of applying the given Option-bearing mapping function to the value,
        otherwise returns an empty Option.

        :param mapper: the mapping function to apply to a value, if present
        :return: the result of applying an Option-bearing mapping function
        """

        require_not_none(mapper)

        if self.is_empty():
            return self.empty()

        return mapper(self.__value)

    def get(self) -> T_co:
        """
        If a value is present, returns the value, otherwise raise ValueError

        :return: the non-none value described by this Option
        :raise ValueError: if no value is present
        """

        if self.is_empty():
            raise ValueError('No value present')

        return self.__value

    def if_present(self, action: Callable[[T_co], None]) -> None:
        """
        If a value is present, performs the given action with the value, otherwise does nothing.

        :param action: the action to be performed, if a value is present
        """

        require_not_none(action)

        if self.is_present():
            action(self.__value)

    def if_present_or_else(self, action: Callable[[T_co], None], empty_action: Callable[[], None]) -> None:
        """
        If a value is present, performs the given action with the value, otherwise performs the given empty-based action

        :param action: the action to be performed, if a value is present
        :param empty_action: the empty-based action to be performed, if no value is present
        """

        require_not_none(action)
        require_not_none(empty_action)

        if self.is_present():
            action(self.__value)
        else:
            empty_action()

    def is_empty(self) -> bool:
        """
        If a value is not present, returns True, otherwise False.

        :return: True if a value is not present, otherwise False
        """

        return self.__value is None

    def is_present(self) -> bool:
        """
        If a value is present, returns True, otherwise False.

        :return: True if a value is present, otherwise False
        """

        return self.__value is not None

    def map(self, mapper: Callable[[T_co], U]) -> Option[U]:
        """
        If a value is present, returns an Option describing the result of applying the given mapping function
        to the value, otherwise returns an empty Option. If the mapping function returns a None result then
        this method returns an empty Option.

        :param mapper: the mapping function to apply to a value, if present
        :return: an Option describing the result of applying a mapping function to the value of this Option,
        if a value is present, otherwise an empty Option
        """

        require_not_none(mapper)

        if self.is_empty():
            return self.empty()

        return Option.of_nullable(mapper(self.__value))

    @overload
    def try_map(self, mapper: Callable[[T_co], U]) -> Option[U]:
        ...

    @overload
    def try_map(self, mapper: Callable[[T_co], U], error_handler: Callable[[Exception], U]) -> Option[U]:
        ...

    def try_map(
        self, mapper: Callable[[T_co], U], error_handler: Optional[Callable[[Exception], U]] = None
    ) -> Option[U]:
        """
        If a value is present, returns an Option describing the result of applying the given mapping function
        to the value, catching any exceptions that occur. If no value is present, returns an empty Option.

        :param mapper: the function to apply to the value, if present
        :param error_handler: an optional function to handle exceptions raised by the mapper
        :return: an Option containing the result of applying the function to the value, or an empty Option if no value
        is present or if an exception occurred
        """

        require_not_none(mapper)

        if self.is_empty():
            return self.empty()

        try:
            return Option.of_nullable(mapper(self.__value))
        except Exception as e:  # noqa: BLE001
            if error_handler is not None:
                return Option.of_nullable(error_handler(e))
            return Option.empty()

    @staticmethod
    def of(value: T_co) -> Option[T_co]:
        """
        Returns an Option describing the given non-none value.

        :param value: the value to describe, which must be non-none
        :return: an Option with the value present
        """

        return Option(require_not_none(value))

    @staticmethod
    def of_nullable(value: T_co) -> Option[T_co]:
        """
        Returns an Option describing the given value, if non-none, otherwise returns an empty Option.

        :param value: the possibly-none value to describe
        :return: an Option with a present value if the specified value is non-none, otherwise an empty Option
        """

        if value is None:
            return Option.empty()

        return Option(value)

    @staticmethod
    def try_of(supplier: Callable[[], T_co]) -> Option[T_co]:
        """
        Returns an Option describing the result of invoking a specified supplier, if non-none, otherwise
        returns an empty Option.

        :param supplier: the function to invoke
        :return: an Option with a present value if the specified function returns non-none, otherwise an empty Option
        """

        require_not_none(supplier)

        try:
            return Option.of_nullable(supplier())
        except Exception:  # noqa: BLE001
            return Option.empty()

    def __or__(self, other: Option[T_co]) -> Option[T_co]:
        """
        If a value is present, returns an Option describing the value, otherwise returns other an Option.

        :param other: the supplying function that produces an Option to be returned
        :return: an Option describing the value of this Option, if a value is present,
        otherwise an Option produced by the supplying function.
        """

        if self.is_present():
            return self

        return other

    def or_else(self, other: T_co) -> T_co:
        """
        If a value is present, returns the value, otherwise returns other.

        :param other: the value to be returned, if no value is present. May be None.
        :return: the value, if present, otherwise other
        """

        if self.is_present():
            return self.__value

        return other

    def or_else_get(self, supplier: Callable[[], T_co]) -> T_co:
        """
        If a value is present, returns the value, otherwise returns the result produced by the supplying function.

        :param supplier: the supplying function that produces a value to be returned
        :return: the value, if present, otherwise the result produced by the supplying function
        """

        require_not_none(supplier)

        if self.is_present():
            return self.__value

        return supplier()

    @overload
    def or_else_raise(self) -> T_co:
        ...

    @overload
    def or_else_raise(self, supplier: Callable[[Any], Exception], *args, **kwargs) -> T_co:
        ...

    def or_else_raise(self, supplier: Optional[Callable[[Any], Exception]] = None, *args, **kwargs) -> T_co:
        """
        If a value is present, returns the value, otherwise raises an exception produced by the exception
        supplying function.

        :param supplier: the supplying function that produces an exception to be raised
        :return: the value, if present
        """

        if self.is_present():
            return self.__value

        if supplier is None:
            raise ValueError('No value present')
        raise supplier(*args, **kwargs)

    def __bool__(self):
        return self.is_present()

    def __eq__(self, other) -> bool:
        if isinstance(other, Option):
            return self.__value == other.__value
        return False

    def __hash__(self):
        return hash(self.__value)

    def __repr__(self):
        return f'Option({self.__value!r})'


class _Empty(Option[None]):
    """Common instance of Option for empty value"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        super().__init__(None)

    def is_empty(self) -> bool:
        return True

    def is_present(self) -> bool:
        return False
