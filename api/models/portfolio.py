from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel

from enums.portfolio_type import PortfolioType
from models.fields import StrEnumField
from schemas.portfolio import PortfolioUpdateModel

if TYPE_CHECKING:
    from models.user import UserModel


class PortfolioModel(SQLModel, table=True):
    __tablename__ = "portfolios"

    id: UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "unique": True,
            "nullable": False,
        },
    )
    type: PortfolioType = StrEnumField(PortfolioType, max_length=16)
    user_id: UUID = Field(default=None, foreign_key="users.id")

    user: "UserModel" = Relationship(
        back_populates="portfolios",
        sa_relationship_kwargs={
            "primaryjoin": "PortfolioModel.user_id == UserModel.id"
        },
    )

    def update(self, update_data: PortfolioUpdateModel) -> None:
        for key, value in update_data.model_dump().items():
            if value is None:
                continue

            setattr(self, key, value)
