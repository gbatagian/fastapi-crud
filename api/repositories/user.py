from uuid import UUID

from sqlalchemy.orm import selectinload

from models.portfolio import PortfolioModel
from models.user import UserModel
from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    orm_model: UserModel = UserModel

    @classmethod
    async def get(cls, id: UUID) -> UserModel | None:
        return await (
            cls.select(cls.orm_model)
            .where(cls.orm_model.id == id)
            .one_or_none()
        )

    @classmethod
    async def all(cls) -> list[UserModel]:
        return await cls.select(cls.orm_model).all()

    @classmethod
    async def get_portfolios(cls, id: UUID) -> list[PortfolioModel]:
        result = await (
            cls.select(cls.orm_model)
            .where(cls.orm_model.id == id)
            .options(selectinload(UserModel.portfolios))
            .one_or_none()
        )
        if result is None:
            return []

        return result.portfolios
