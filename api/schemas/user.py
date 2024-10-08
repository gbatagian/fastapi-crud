from pydantic import BaseModel

from enums.subscription_plan import SubscriptionPlan


class UserCreateModel(BaseModel):
    name: str
    surname: str
    email: str
    plan: SubscriptionPlan


class UserUpdateModel(BaseModel):
    name: str | None = None
    surname: str | None = None
    email: str | None = None
    plan: SubscriptionPlan | None = None
