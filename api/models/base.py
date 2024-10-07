from __future__ import annotations

from typing import Any
from typing import Type

from pydantic import ConfigDict
from pydantic_core import PydanticUndefined
from sqlmodel import SQLModel
from sqlmodel.main import SQLModelMetaclass


class OutModelMetaclass(SQLModelMetaclass):
    def __new__(
        cls,
        name: str,
        bases: tuple[Type, ...],
        class_dict: dict[str, Any],
        orm_model: Type[SQLModel] | None = None,
        **kwargs: Any,
    ) -> Type[SQLModel]:
        if orm_model is not None:
            # Add annotations from ORM Model to Out Model
            for field_name, field_info in orm_model.__fields__.items():  # type: ignore
                if field_name in class_dict["__annotations__"]:
                    # field is re-defined as attribute in out model - no need to get definition form ORM model
                    continue
                else:
                    # field is not defined in out model - get definition from ORM model
                    class_dict["__annotations__"][
                        field_name
                    ] = field_info.annotation
                    if field_info.default is not PydanticUndefined:
                        # add default value is exists
                        class_dict[field_name] = field_info.default

        return super().__new__(cls, name, bases, class_dict, **kwargs)


class BaseOutModel(SQLModel, table=False, metaclass=OutModelMetaclass):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # type: ignore
    _orm_model: Type[SQLModel]

    @classmethod
    def model_validate(
        cls, orm: Type[SQLModel], *args, **kwargs
    ) -> BaseOutModel | None:
        out_model_instance = super().model_validate(orm, *args, **kwargs)
        out_model_instance._orm_model = orm
        return out_model_instance

    @property
    def orm_model(self) -> Type[SQLModel]:
        return self._orm_model
