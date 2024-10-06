from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from models.user import UserModel
from repositories.base import SessionManager
from repositories.base import get_db
from repositories.user import UserRepository

user_api = APIRouter()


@user_api.get("/users")
def get_user(db: SessionManager = Depends(get_db)) -> list[UserModel]:
    return UserRepository(db=db).all()


@user_api.get("/users/{user_id}")
def get_user(user_id: UUID, db: SessionManager = Depends(get_db)) -> UserModel | None:
    return UserRepository(db=db).get(user_id)
