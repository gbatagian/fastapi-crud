from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel

from enums.subscription_plan import SubscriptionPlan
from models.fields import EnumField
from schemas.user import UserUpdateModel

if TYPE_CHECKING:
    from models.portfolio import PortfolioModel


class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={
            "server_default": text("gen_random_uuid()"),
            "unique": True,
            "nullable": False,
        },
    )
    name: str
    surname: str
    email: str
    plan: SubscriptionPlan = EnumField(SubscriptionPlan)

    portfolios: list["PortfolioModel"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "primaryjoin": "UserModel.id == PortfolioModel.user_id"
        },
    )

    def update(self, update_data: UserUpdateModel) -> None:
        for key, value in update_data.model_dump().items():
            if value is None:
                continue

            setattr(self, key, value)
