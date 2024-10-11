from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from models.portfolio import PortfolioModel
from models.user import UserModel
from repositories.base import SessionConstructor
from repositories.base import session_manager
from repositories.user import UserRepository
from schemas.user import UserCreateModel
from schemas.user import UserUpdateModel

user_api = APIRouter()


@user_api.get("/users")
def get_users(
    db: SessionConstructor = Depends(session_manager),
) -> list[UserModel]:
    return UserRepository(db=db).all()


@user_api.post("/users")
def create_portfolio(
    user_create: UserCreateModel,
    db: SessionConstructor = Depends(session_manager),
) -> UserModel:
    with db.session as session:
        user = UserModel(
            name=user_create.name,
            surname=user_create.surname,
            email=user_create.email,
            plan=user_create.plan,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    return user


@user_api.get("/users/{user_id}")
def get_user(
    user_id: UUID, db: SessionConstructor = Depends(session_manager)
) -> UserModel | None:
    return UserRepository(db=db).get(user_id)


@user_api.put("/users/{user_id}")
def update_user(
    user_id: UUID,
    user_update: UserUpdateModel,
    db: SessionConstructor = Depends(session_manager),
) -> UserModel | None:
    user = UserRepository(db=db).get(user_id)
    if user is None:
        return None

    user.update(user_update)

    with db.session as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    return user


@user_api.delete("/users/{user_id}")
def delete_portfolio(
    user_id: UUID, db: SessionConstructor = Depends(session_manager)
) -> UserModel | None:
    user = UserRepository(db=db).get(user_id)
    if user is None:
        return None

    with db.session as session:
        session.delete(user)
        session.commit()

    return user


@user_api.get("/users/{user_id}/portfolios")
def get_user_portfolios(
    user_id: UUID, db: SessionConstructor = Depends(session_manager)
) -> list[PortfolioModel] | None:
    return UserRepository(db=db).get_portfolios(user_id)
