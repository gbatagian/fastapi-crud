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
from sqlmodel import Session as _Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

from configuration import DB_LOG
from configuration import DB_URL
from logger import logger

T = TypeVar("T")


class Session(_Session):
    def __init__(
        self, *args: Any, managed: bool = False, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.managed = managed


class SessionConstructor:
    engine = create_engine(
        url=f"postgresql+psycopg2://{DB_URL}",
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )

    def __init__(self, managed: bool = False) -> None:
        self.managed = managed

    @cached_property
    def session(self) -> Session:
        return Session(self.engine, managed=self.managed)

    def close(self) -> None:
        self.session.close()


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
        if session is None:
            self.session = SessionConstructor(managed=False).session
        else:
            self.session = session

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
        finally:
            if self.session.managed is False:
                self.session.close()

    @query_logger
    def one(self) -> SQLModel:
        try:
            return self.session.exec(statement=self).scalars().one()
        except Exception as exp:
            self.session.rollback()
            raise exp
        finally:
            if self.session.managed is False:
                self.session.close()

    @query_logger
    def all(self) -> list[SQLModel]:
        try:
            return self.session.exec(statement=self).scalars().all()
        except Exception as exp:
            self.session.rollback()
            raise exp
        finally:
            if self.session.managed is False:
                self.session.close()

    @query_logger
    def first(self) -> SQLModel:
        try:
            return self.session.exec(statement=self).scalars().first()
        except Exception as exp:
            self.session.rollback()
            raise exp
        finally:
            if self.session.managed is False:
                self.session.close()


class BaseRepository:
    orm_model: Type[SQLModel]
    session: Session

    def select(
        self,
        orm_model: Type[SQLModel],
        *entities: Type[SQLModel],
    ) -> Select:
        return Select(
            orm_model,
            *entities,
            session=self.session,
        )


def session_manager() -> Generator[SessionConstructor]:
    db = SessionConstructor(managed=True)
    try:
        yield db
    finally:
        db.close()
