from functools import lru_cache, total_ordering

__all__ = [
    'EnumMixin'
]


@total_ordering
class EnumMixin:
    """
    EnumMixin is a mixin class designed to extend the functionality of Enum classes.
    It provides additional methods and properties to handle comparison, value retrieval,
    and ordinal positions.

    >>> from enum import Enum
    >>> class Weekday(EnumMixin, Enum):
    ...     MONDAY = 'mon'
    ...     TUESDAY = 'tue'
    ...     WEDNESDAY = 'wed'
    ...     THURSDAY = 'thu'
    ...     FRIDAY = 'fri'
    ...     SATURDAY = 'sat'
    ...     SUNDAY = 'sun'
    """

    @classmethod
    def value_of(cls, value):  # pylint: disable=inconsistent-return-statements
        """
        Returns the enum constant of the specified enum type with the specified value.

        :param value: the value of the enum constant to be returned
        :return: the enum constant with the specified value
        """

        for member in cls.__members__.values():
            if member.value == value:
                return member

    @property
    def ordinal(self):
        """
        Returns the ordinal of this enum constant, which is its position in its enum declaration,
        where the initial constant is assigned an ordinal of zero.

        :return: the ordinal of this enum constant
        """

        return self.__ordinals__()[self.name]

    def __gt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.ordinal > other.ordinal

    @classmethod
    @lru_cache()
    def __ordinals__(cls):
        return {name: index for index, name in enumerate(cls.__members__)}
