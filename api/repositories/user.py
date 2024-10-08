from uuid import UUID

from models.portfolio import PortfolioModel
from models.user import UserModel
from repositories.base import BaseRepository
from repositories.base import SessionManager


class UserRepository(BaseRepository):
    orm_model = UserModel

    def __init__(self, db: SessionManager) -> None:
        self.session = db.session

    def get(self, id: UUID) -> UserModel | None:
        return self.query().where(self.orm_model.id == id).one_or_none()

    def all(self) -> list[UserModel]:
        return self.query().all()

    def get_portfolios(self, id: UUID) -> list[PortfolioModel]:
        result = self.get(id=id)
        if result is None:
            return []

        return result.portfolios
