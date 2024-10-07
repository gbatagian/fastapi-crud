from uuid import UUID

from models.portfolio import PortfolioModel
from models.user import UserModel
from models.user import UserORM
from repositories.base import BaseRepository
from repositories.base import SessionManager


class UserRepository(BaseRepository):
    orm_model = UserORM
    out_model = UserModel

    def __init__(self, db: SessionManager) -> None:
        self.session = db.session

    def get(self, id: UUID) -> UserModel | None:
        return self.query().where(self.orm_model.id == id).one_or_none()

    def all(self) -> list[UserModel]:
        return self.query().all()

    def get_portfolios(self, id: UUID) -> list[PortfolioModel]:
        result = self.query().where(self.orm_model.id == id).one_or_none()
        if result is None:
            return []

        return result.orm_model.portfolios
