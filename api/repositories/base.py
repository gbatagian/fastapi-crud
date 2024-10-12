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
from sqlmodel import Session as _Session
from sqlmodel import SQLModel
from sqlmodel import create_engine

from configuration import DB_LOG
from configuration import DB_URL
from logger import logger

T = TypeVar("T")


class Session(_Session):
    def __init__(
        self, *args: Any, _is_managed: bool = False, **kwargs: Any
    ) -> None:
        """
        _is_managed: bool, default = False.  If True, the session is managed by a SessionMaker context.
            In managed sessions, closing is handled by SessionMaker.close(). Examples:

            Managed session:

                def session_manager() -> Generator[SessionMaker]:
                    db = SessionMaker(managed=True)
                    try:
                        yield db
                    finally:
                        db.close()

                db = next(session_manager())
                db.session._is_managed # is True

            Unmanaged session:

                db = SessionMaker()
                db.session._is_managed # is False
        """
        super().__init__(*args, **kwargs)
        self._is_managed = _is_managed


class SessionMaker:
    engine = create_engine(
        url=f"postgresql+psycopg2://{DB_URL}",
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
    )

    def __init__(self, _is_managed: bool = False) -> None:
        """
        _is_managed: bool, default = False. Set to True if the SessionMaker instance
            is managed by a context manager.

            Example:

                def session_manager() -> Generator[SessionMaker]:
                    db = SessionMaker(_is_managed=True)
                    try:
                        yield db
                    finally:
                        db.close()
        """
        self._is_managed = _is_managed

    @cached_property
    def session(self) -> Session:
        return Session(self.engine, _is_managed=self._is_managed)

    def close(self) -> None:
        self.session.close()

    @staticmethod
    def generate_session() -> Session:
        """Generate a new, unmanaged Session instance."""
        db = SessionMaker()
        return db.session


class Select(_Select):
    inherit_cache = True

    def __init__(
        self,
        orm_model: Type[SQLModel],
        *entities: Type[SQLModel],
        session: Session | None = None,
    ) -> None:
        """
        orm_model: Type[SQLModel], The primary model for the select operation.
        *entities: Type[SQLModel], Additional entities to include in the select.
        session: Session | None, The session to use. If None, a new session is generated.
        """
        super().__init__(orm_model, *entities)

        self.orm_model = orm_model
        if session is None:
            self.session = SessionMaker.generate_session()
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

        For managed sessions, maintains the session open throughout the context.
        For unmanaged sessions, the session closes upon query completion.
        """
        if self.session._is_managed:
            # Session is managed by a SessionMaker context - it closes when SessionMaker.close()
            # is called.

            # In HTTP contexts, this allows the same session to persist for the
            # entire request, closing upon request completion.
            try:
                yield self.session
            except Exception as exp:
                self.session.rollback()
                raise exp
        else:
            # Session is not managed by SessionMaker context. It acts as its own context manager,
            # opening for the query and closing upon completion.
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
    session: Session

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


def session_manager() -> Generator[SessionMaker]:
    db = SessionMaker(_is_managed=True)
    try:
        yield db
    finally:
        db.close()
