from uuid import UUID

from models.portfolio import PortfolioModel
from repositories.base import BaseRepository
from repositories.base import SessionConstructor


class PortfolioRepository(BaseRepository):
    orm_model: PortfolioModel = PortfolioModel

    def __init__(self, db: SessionConstructor) -> None:
        self.session = db.session

    def get(self, id: UUID) -> PortfolioModel | None:
        return (
            self.select(self.orm_model)
            .where(self.orm_model.id == id)
            .one_or_none()
        )

    def all(self) -> list[PortfolioModel]:
        return self.select(self.orm_model).all()
