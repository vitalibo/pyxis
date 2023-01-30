from __future__ import annotations

import dataclasses
from typing import Optional, Type, TypeVar, Union, Callable, Any, overload

import pydantic

_T = TypeVar('_T')
_V = TypeVar('_V')

__all__ = (
    'dataclass',
)


@overload
def dataclass(  # pylint: disable=redefined-builtin
        *,
        init: bool = True, repr: bool = True, eq: bool = True, order: bool = False,
        unsafe_hash: bool = False, frozen: bool = False
) -> Callable[[Type[_T]], _V]:
    ...


@overload
def dataclass(  # pylint: disable=redefined-builtin
        cls: Type[_T], *,
        init: bool = True, repr: bool = True, eq: bool = True, order: bool = False,
        unsafe_hash: bool = False, frozen: bool = False
) -> _V:
    ...


def dataclass(  # pylint: disable=redefined-builtin
        cls: Optional[Type[_T]] = None, *,
        init: bool = True, repr: bool = True, eq: bool = True, order: bool = False,
        unsafe_hash: bool = False, frozen: bool = False
) -> Union[Callable[[Type[_T]], _V], _V]:
    """ Like the python standard lib dataclasses but with type validation and method reference """

    def wrap(_cls: Type[Any]) -> _V:
        _cls = dataclasses.dataclass(  # type: ignore
            _cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen
        )

        pydantic.dataclasses.dataclass(_cls, config={'extra': pydantic.Extra.forbid})
        _inject_field_reference(_cls)
        return _cls

    if cls is None:
        return wrap

    return wrap(cls)


def _inject_field_reference(cls):
    for field in cls.__dataclass_fields__.values():
        setattr(cls, field.name, _FieldReference(field.name))
    return cls


class _FieldReference:
    """ Allows to create a reference on a field in the dataclass """

    def __init__(
            self,
            field: str,
            parent: _FieldReference = None
    ) -> None:
        self._field = field
        self._parent = parent

    def __call__(self, *args, **kwargs):
        obj, *_ = args
        if self._parent is not None:
            obj = self._parent(obj)

        if isinstance(self._field, str):
            return getattr(obj, self._field)
        return obj[self._field]

    def __getattr__(self, field):
        return _FieldReference(field, parent=self)

    def __getitem__(self, field):
        return _FieldReference(field, parent=self)
