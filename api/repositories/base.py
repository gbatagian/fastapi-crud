from __future__ import annotations

from functools import cached_property
from functools import wraps
from typing import Any
from typing import Callable
from typing import Generator
from typing import Type
from typing import TypeVar
from typing import cast

from sqlalchemy.sql import Select as _Select
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

from configuration import DB_LOG
from configuration import DB_URL
from logger import logger

T = TypeVar("T")


class SessionManager:
    engine = create_engine(
        url=f"postgresql+psycopg2://{DB_URL}",
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )

    @cached_property
    def session(self) -> Session:
        return Session(self.engine)


class Select(_Select):
    inherit_cache = True

    def __init__(
        self,
        orm_model: Type[SQLModel],
        *entities: Type[SQLModel],
        session: Session | None = None,
    ) -> None:
        super().__init__(orm_model, *entities)

        self.orm_model = orm_model
        self.session = session
        if self.session is None:
            self.session = SessionManager().session

    @staticmethod
    def query_logger(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> T:
            if DB_LOG:
                logger.info(self)
            return func(self, *args, **kwargs)

        return cast(Callable[..., T], wrapper)

    @query_logger
    def one_or_none(self) -> SQLModel | None:
        try:
            row = self.session.exec(statement=self).scalars().one_or_none()

            if row is None:
                return None

            return row
        except Exception as exp:
            self.session.rollback()
            raise exp

    @query_logger
    def one(self) -> SQLModel:
        try:
            return self.session.exec(statement=self).scalars().one()
        except Exception as exp:
            self.session.rollback()
            raise exp

    @query_logger
    def all(self) -> list[SQLModel]:
        try:
            return self.session.exec(statement=self).scalars().all()
        except Exception as exp:
            self.session.rollback()
            raise exp

    @query_logger
    def first(self) -> SQLModel:
        try:
            return self.session.exec(statement=self).scalars().first()
        except Exception as exp:
            self.session.rollback()
            raise exp


class BaseRepository:
    orm_model: Type[SQLModel]
    session: Session

    def select(
        self,
        orm_model: Type[SQLModel],
        *entities: Type[SQLModel],
    ) -> Select:
        return Select(
            orm_model=orm_model,
            *entities,
            session=self.session,
        )


def get_db() -> Generator[SessionManager]:
    db = SessionManager()
    try:
        yield db
    finally:
        db.session.close()
