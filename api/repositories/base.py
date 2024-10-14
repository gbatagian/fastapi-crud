from __future__ import annotations

from contextlib import contextmanager
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


class KeepAliveSession(Session):
    """
    Session type to indicate sessions that remain open after query execution.

    This session type is useful in HTTP contexts where a single session is created 
    at the start of a request, remains open throughout the request's lifecycle, 
    and closes upon request completion.
    """


class SessionManager:
    engine = create_engine(
        url=f"postgresql+psycopg2://{DB_URL}",
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )

    def __init__(self, session_type: Type[Session] | None = None) -> None:
        if session_type is None:
            self.session_type = Session
        else:
            self.session_type = session_type

    @cached_property
    def session(self) -> Session:
        return self.session_type(self.engine)

    def close(self) -> None:
        self.session.close()

    @staticmethod
    def new_session() -> Session:
        db = SessionManager()
        return db.session

    @staticmethod
    def mew_keep_alive_session() -> Session:
        db = SessionManager(session_type=KeepAliveSession)
        return db.session


def get_keep_alive_session_manager() -> Generator[SessionManager]:
    db = SessionManager(session_type=KeepAliveSession)
    try:
        yield db
    finally:
        db.close()


class Select(_Select):
    """
    Enhanced Select class with session management.
    """

    inherit_cache = True

    def __init__(
        self,
        orm_model: Type[SQLModel],
        *entities: Type[SQLModel],
        session: KeepAliveSession | None = None,
    ) -> None:
        """
        orm_model: Type[SQLModel], The primary model for the select operation.
        *entities: Type[SQLModel], Additional entities to include in the select.
        session: Session | None, The session to use. If None, a new session is generated.
        """
        super().__init__(orm_model, *entities)

        self.orm_model = orm_model
        if session is None:
            self.session = SessionManager.new_session()
        else:
            self.session = session

    @staticmethod
    def query_logger(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to log queries if DB_LOG is enabled."""

        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> T:
            if DB_LOG:
                logger.info(self)
            return func(self, *args, **kwargs)

        return cast(Callable[..., T], wrapper)

    @contextmanager
    def _managed_session(self):
        """
        Context manager for handling session lifecycle.

        - For KeepAliveSession: Keeps the session open after query execution.
        - For standard Session: Closes the session after query completion.
        """
        if isinstance(self.session, KeepAliveSession):
            # yield the session without opening its context manager to keep it open after
            # query execution. This allows the session to persist across multiple
            # operations, e.g. within an HTTP request.
            try:
                yield self.session
            except Exception as exp:
                self.session.rollback()
                raise exp
        else:
            # yield the session inside its context manager to close it after query execution.
            with self.session as session:
                yield session

    @query_logger
    def one_or_none(self) -> SQLModel | None:
        with self._managed_session() as session:
            row = session.exec(statement=self).scalars().one_or_none()

            if row is None:
                return None

            return row

    @query_logger
    def one(self) -> SQLModel:
        with self._managed_session() as session:
            return session.exec(statement=self).scalars().one()

    @query_logger
    def all(self) -> list[SQLModel]:
        with self._managed_session() as session:
            return session.exec(statement=self).scalars().all()

    @query_logger
    def first(self) -> SQLModel:
        with self._managed_session() as session:
            return session.exec(statement=self).scalars().first()


class BaseRepository:
    orm_model: Type[SQLModel]
    session: KeepAliveSession

    def select(
        self,
        orm_model: Type[SQLModel],
        *entities: Type[SQLModel],
    ) -> Select:
        """
        Create a Select instance for the given ORM model and entities.

        orm_model: Type[SQLModel], The primary model for the select operation.
        *entities: Type[SQLModel], Additional entities to include in the select.
        """
        return Select(
            orm_model,
            *entities,
            session=self.session,
        )
