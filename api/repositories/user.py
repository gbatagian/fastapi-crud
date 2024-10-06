from uuid import UUID

from sqlalchemy.orm import selectinload

from models.user import UserModel
from models.user import UserORM
from repositories.base import BaseRepository
from repositories.base import SessionManager


class UserRepository(BaseRepository):
    orm_model = UserORM
    out_model = UserModel

    def __init__(self, db: SessionManager) -> None:
        self.session = db.session

    def get(self, id: UUID, with_relationships: bool = False) -> UserModel | None:
        query = self.query().where(self.orm_model.id == id)
        if with_relationships is True:
            query = query.options(selectinload(self.orm_model.portfolios))

        return query.one_or_none()

    def all(self) -> list[UserModel]:
        return self.query().all()
