from uuid import UUID

from sqlalchemy.orm import selectinload

from models.portfolio import PortfolioModel
from models.user import UserModel
from repositories.base import BaseRepository
from repositories.base import SessionMaker


class UserRepository(BaseRepository):
    orm_model: UserModel = UserModel

    def __init__(self, db: SessionMaker) -> None:
        self.session = db.session

    def get(self, id: UUID) -> UserModel | None:
        return (
            self.select(self.orm_model)
            .where(self.orm_model.id == id)
            .one_or_none()
        )

    def all(self) -> list[UserModel]:
        return self.select(self.orm_model).all()

    def get_portfolios(self, id: UUID) -> list[PortfolioModel]:
        result = (
            self.select(self.orm_model)
            .where(self.orm_model.id == id)
            .options(selectinload(UserModel.portfolios))
            .one_or_none()
        )
        if result is None:
            return []

        return result.portfolios
