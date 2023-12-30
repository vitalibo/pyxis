import dataclasses
from typing import Callable, Optional, Type, TypeVar, Union, overload

__all__ = [
    'reference',
    'dataclass'
]

T = TypeVar('T')


def reference(cls):
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


@overload
def dataclass(
        *,
        init: bool = True,
        repr: bool = True,  # pylint: disable=redefined-builtin
        eq: bool = True,
        order: bool = False,
        unsafe_hash: bool = False,
        frozen: bool = False
) -> Callable[[Type[T]], Type[T]]:
    ...


@overload
def dataclass(
        _cls: Type[T],
        *,
        init: bool = True,
        repr: bool = True,  # pylint: disable=redefined-builtin
        eq: bool = True,
        order: bool = False,
        unsafe_hash: bool = False,
        frozen: bool = False
) -> Type[T]:
    ...


def dataclass(
        _cls: Optional[Type[T]] = None,
        *,
        init: bool = True,
        repr: bool = True,  # pylint: disable=redefined-builtin
        eq: bool = True,
        order: bool = False,
        unsafe_hash: bool = False,
        frozen: bool = False
) -> Union[Callable[[Type[T]], Type[T]], Type[T]]:
    """
    Like the python standard lib dataclasses but with enriched field reference
    """

    def wrap(cls: Type[T]) -> Type[T]:
        cls = dataclasses.dataclass(  # noqa
            cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen)
        try:
            import pydantic.dataclasses  # pylint: disable=import-outside-toplevel
            pydantic.dataclasses.dataclass(cls)
        except ImportError:
            pass
        return reference(cls)

    if _cls is None:
        return wrap
    return wrap(_cls)
