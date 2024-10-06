from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel

from enums.portfolio_type import PortfolioType
from models.base import BaseOutModel

if TYPE_CHECKING:
    from models.user import UserORM


class PortfolioORM(SQLModel, table=True):
    __tablename__ = "portfolios"

    id: UUID | None = Field(default=None, primary_key=True)
    type: str
    user_id: UUID = Field(default=None, foreign_key="users.id")

    # relationships
    user: "UserORM" = Relationship(
        back_populates="portfolios",
        sa_relationship_kwargs={"primaryjoin": "PortfolioORM.user_id == UserORM.id"},
    )


class PortfolioModel(BaseOutModel, orm_model=PortfolioORM):  # type: ignore
    type: PortfolioType
