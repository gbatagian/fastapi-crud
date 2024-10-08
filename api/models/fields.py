from enum import Enum
from typing import Any
from typing import Type

from sqlalchemy import types as sa_types
from sqlmodel import Field


def enum_field_factory(
    enum_type: Type[Enum], values: list[Any] | None = None
) -> Field:  # type: ignore
    if values is None:
        values = [member.value for member in enum_type]

    return Field(
        sa_type=sa_types.Enum(
            enum_type,
            values_callable=lambda _: values,
        )
    )


EnumField = enum_field_factory
