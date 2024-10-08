from __future__ import annotations

from functools import cached_property
from typing import Any
from typing import Callable
from typing import Generator
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


class Query(_Select):
    def __init__(
        self,
        orm_model: Type[SQLModel],
        session: Session,
    ) -> None:
        self.statement = select(orm_model)

        self.orm_model = orm_model
        self.session = session

    def __getattribute__(
        self, name: str
    ) -> Callable[..., Type[SQLModel] | list[Type[SQLModel]] | None] | Any:
        # proxy statement operations, i.e. where, join etc. to self.statement i.e. sqlalchemy.sql.Select
        statement = object.__getattribute__(self, "statement")
        statement_operation = getattr(statement, name, None)

        if statement_operation is not None:

            def execute_operation(*args: Any, **kwargs: Any):
                self.statement = statement_operation(*args, **kwargs)
                return self

            return execute_operation

        return object.__getattribute__(self, name)

    def one_or_none(self) -> SQLModel | None:
        try:
            row = (
                self.session.exec(statement=self.statement)
                .scalars()
                .one_or_none()
            )

            if row is None:
                return None

            return row
        except Exception as exp:
            self.session.rollback()
            raise exp

    def one(self) -> SQLModel:
        try:
            return self.session.exec(statement=self.statement).scalars().one()
        except Exception as exp:
            self.session.rollback()
            raise exp

    def all(self) -> list[SQLModel]:
        try:
            return self.session.exec(statement=self.statement).scalars().all()
        except Exception as exp:
            self.session.rollback()
            raise exp

    def first(self) -> SQLModel:
        try:
            return self.session.exec(statement=self.statement).scalars().first()
        except Exception as exp:
            self.session.rollback()
            raise exp


class BaseRepository:
    orm_model: Type[SQLModel]
    session: Session

    def query(self) -> Query:
        return Query(
            orm_model=self.orm_model,
            session=self.session,
        )


def get_db() -> Generator[SessionManager]:
    db = SessionManager()
    try:
        yield db
    finally:
        db.session.close()
