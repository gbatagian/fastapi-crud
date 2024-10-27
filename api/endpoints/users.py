from uuid import UUID

from fastapi import APIRouter

from models.portfolio import PortfolioModel
from models.user import UserModel
from repositories.base import managed_session
from repositories.user import UserRepository
from schemas.user import UserCreateModel
from schemas.user import UserUpdateModel

user_api = APIRouter()


@user_api.get("/users")
def get_users() -> list[UserModel]:
    return UserRepository.all()


@user_api.post("/users")
def create_portfolio(
    user_create: UserCreateModel,
) -> UserModel:
    with managed_session() as session:
        user = UserModel(
            name=user_create.name,
            surname=user_create.surname,
            email=user_create.email,
            plan=user_create.plan,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    return user


@user_api.get("/users/{user_id}")
def get_user(
    user_id: UUID,
) -> UserModel | None:
    return UserRepository.get(user_id)


@user_api.put("/users/{user_id}")
def update_user(
    user_id: UUID,
    user_update: UserUpdateModel,
) -> UserModel | None:
    user = UserRepository.get(user_id)
    if user is None:
        return None

    user.update(user_update)

    with managed_session() as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    return user


@user_api.delete("/users/{user_id}")
def delete_portfolio(user_id: UUID) -> UserModel | None:
    user = UserRepository.get(user_id)
    if user is None:
        return None

    with managed_session() as session:
        session.delete(user)
        session.commit()

    return user


@user_api.get("/users/{user_id}/portfolios")
def get_user_portfolios(user_id: UUID) -> list[PortfolioModel] | None:
    return UserRepository.get_portfolios(user_id)
