from uuid import UUID

from models.portfolio import PortfolioModel
from models.portfolio import PortfolioORM
from repositories.base import BaseRepository
from repositories.base import SessionManager


class PortfolioRepository(BaseRepository):
    orm_model = PortfolioORM
    out_model = PortfolioModel

    def __init__(self, db: SessionManager) -> None:
        self.session = db.session

    def get(self, id: UUID) -> PortfolioModel | None:
        query = self.query().where(self.orm_model.id == id)

        return query.one_or_none()

    def all(self) -> list[PortfolioModel]:
        return self.query().all()
