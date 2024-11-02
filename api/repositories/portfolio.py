from uuid import UUID

from models.portfolio import PortfolioModel
from repositories.base import BaseRepository


class PortfolioRepository(BaseRepository):
    orm_model: PortfolioModel = PortfolioModel

    @classmethod
    async def get(cls, id: UUID) -> PortfolioModel | None:
        return await (
            cls.select(cls.orm_model)
            .where(cls.orm_model.id == id)
            .one_or_none()
        )

    @classmethod
    async def all(cls) -> list[PortfolioModel]:
        return await cls.select(cls.orm_model).all()
