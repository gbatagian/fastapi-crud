from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field
from sqlmodel import Relationship
from sqlmodel import SQLModel

from enums.subscription_plan import SubscriptionPlan
from models.base import BaseOutModel

if TYPE_CHECKING:
    from models.portfolio import PortfolioORM


class UserORM(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID | None = Field(default=None, primary_key=True)
    name: str
    surname: str
    email: str
    plan: str

    portfolios: list["PortfolioORM"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "primaryjoin": "UserORM.id == PortfolioORM.user_id"
        },
    )


class UserModel(BaseOutModel, orm_model=UserORM):  # type: ignore
    plan: SubscriptionPlan

    @property
    def is_paid_subscriber(self) -> bool:
        return self.plan is not SubscriptionPlan.FREEMIUM
