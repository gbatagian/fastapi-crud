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
async def get_users() -> list[UserModel]:
    return await UserRepository.all()


@user_api.post("/users")
async def create_user(
    user_create: UserCreateModel,
) -> UserModel:
    async with managed_session() as session:
        user = UserModel(
            name=user_create.name,
            surname=user_create.surname,
            email=user_create.email,
            plan=user_create.plan,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


@user_api.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
) -> UserModel | None:
    return await UserRepository.get(user_id)


@user_api.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    user_update: UserUpdateModel,
) -> UserModel | None:
    user = await UserRepository.get(user_id)
    if user is None:
        return None

    user.update(user_update)

    async with managed_session() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


@user_api.delete("/users/{user_id}")
async def delete_user(user_id: UUID) -> UserModel | None:
    user = await UserRepository.get(user_id)
    if user is None:
        return None

    async with managed_session() as session:
        await session.delete(user)
        await session.commit()

    return user


@user_api.get("/users/{user_id}/portfolios")
async def get_user_portfolios(user_id: UUID) -> list[PortfolioModel] | None:
    return await UserRepository.get_portfolios(user_id)
