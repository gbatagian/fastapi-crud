from __future__ import annotations

from enum import Enum
from functools import cached_property
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Type

from sqlalchemy.sql import Select as _Select
from sqlalchemy.sql.expression import select
from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

from configuration import BD_PWD
from configuration import DB_NAME
from configuration import DB_PORT
from configuration import DB_SERVICE_IP
from configuration import DB_USER
from models.base import BaseOutModel


class SessionManager:
    engine = create_engine(
        url=f"postgresql+psycopg2://{DB_USER}:{BD_PWD}@{DB_SERVICE_IP}:{DB_PORT}/{DB_NAME}",
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )

    @cached_property
    def session(self) -> Session:
        return Session(self.engine)


class FetchMethod(Enum):
    ONE = "one"
    ONE_OR_NONE = "one_or_none"
    ALL = "all"
    FIRST = "first"

    @classmethod
    @lru_cache
    def values(cls) -> list[str]:
        return [e.value for e in cls]


class Query(_Select):
    inherit_cache = True

    def __init__(
        self, orm_model: Type[SQLModel], out_model: Type[BaseOutModel], session: Session
    ) -> None:
        self.statement = select(orm_model)

        self.out_model = out_model
        self.session = session
        self._fetch_method: FetchMethod | None = None

    def __getattribute__(self, name: str) -> Callable[..., Query] | Any:
        # proxy statement operations, i.e. where, join etc. to self.statement i.e. sqlalchemy.sql.Select
        statement = object.__getattribute__(self, "statement")
        statement_operation = getattr(statement, name, None)

        if statement_operation is not None:

            def execute_operation(*args: Any, **kwargs: Any):
                self.statement = statement_operation(*args, **kwargs)
                return self

            return execute_operation

        return object.__getattribute__(self, name)

    def one_or_none(self) -> Type[BaseOutModel] | None:
        with self.session as session:
            result = session.exec(statement=self.statement).one_or_none()

            if result is None:
                return None

            row = next(element for element in result)  # type: ignore
            return self.out_model.model_validate(row)

    def one(self) -> Type[BaseOutModel]:
        with self.session as session:
            result = session.exec(statement=self.statement).one()
            row = next(element for element in result)  # type: ignore

            return self.out_model.model_validate(row)

    def all(self) -> list[Type[BaseOutModel]]:
        with self.session as session:
            result = session.exec(statement=self.statement).all()

            return [
                self.out_model.model_validate(next(element for element in row)) for row in result
            ]

    def first(self) -> Type[BaseOutModel]:
        with self.session as session:
            result = session.exec(statement=self.statement).first()
            row = next(element for element in result)  # type: ignore

            return self.out_model.model_validate(row)


class BaseRepository:
    orm_model: Type[SQLModel]
    out_model: Type[BaseOutModel]
    session: Type[Session]

    def query(self):
        return Query(
            orm_model=self.orm_model,
            out_model=self.out_model,
            session=self.session,
        )


def get_db():
    db = SessionManager()
    try:
        yield db
    finally:
        db.session.close()
