from asyncio import Semaphore
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import cached_property
from functools import wraps
from typing import AsyncGenerator
from typing import Callable
from typing import ParamSpec
from typing import Type
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import Select as _Select
from sqlmodel import SQLModel

from configuration import DB_LOG
from configuration import DB_URL
from logger import logger
from multiprocessing import cpu_count

T = TypeVar("T")
P = ParamSpec("P")

engine = create_async_engine(
    url=f"postgresql+asyncpg://{DB_URL}",
    pool_size=cpu_count() * 2,
    max_overflow=cpu_count(),
    pool_timeout=30,
    pool_recycle=60 * 15,
)

# Increase semaphore capacity based on DB service resources.
# Semaphore capacity is related to concurrent requests arriving at the database.
# Raising it too high may overwhelm the DB causing timeouts. Typically, a value between 50-100 is sufficient for high efficiency.
# Larger values are generally unnecessary unless if you know how to configure a proper setup.
acquire_connection_semaphore = Semaphore(50)


class SessionManager:
    @cached_property
    def session(self) -> AsyncSession:
        return AsyncSession(engine)

    async def close(self) -> None:
        await self.session.close()

    @staticmethod
    def new_session() -> AsyncSession:
        db = SessionManager()
        return db.session


db_context: ContextVar[SessionManager | None] = ContextVar(
    "db_context", default=None
)


def get_context_session() -> AsyncSession:
    db = db_context.get()
    if db is None:
        raise Exception(
            "DB context not set, run: "
            "from repositories.base import SessionManager, db_context; "
            "db = SessionManager(); "
            "db_context.set(db)"
        )

    return db.session


@asynccontextmanager
async def new_db_instance() -> AsyncGenerator[SessionManager, None]:
    async with acquire_connection_semaphore:
        try:
            db = SessionManager()
            yield db
        finally:
            await db.close()


@asynccontextmanager
async def managed_session() -> AsyncGenerator[AsyncSession, None]:
    session = get_context_session()

    try:
        yield session
    except Exception as exp:
        await session.rollback()
        raise exp
    finally:
        await session.close()


class Select(_Select):
    """
    Enhanced Select class with session management.
    """

    inherit_cache = True

    def __init__(
        self,
        orm_model: SQLModel,
        *entities: SQLModel,
        session: AsyncSession,
    ) -> None:
        """
        orm_model: SQLModel, The primary model for the select operation.
        *entities: SQLModel, Additional entities to include in the select.
        session: Session | None, The session to use. If None, a new session is generated.
        """
        super().__init__(orm_model, *entities)

        self.orm_model = orm_model
        self.session = session

    @staticmethod
    def _query_logger(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to log queries if DB_LOG is enabled."""

        @wraps(func)
        def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> T:
            if DB_LOG:
                logger.info(self)
            return func(self, *args, **kwargs)

        return wrapper

    @asynccontextmanager
    async def _managed_session(self):
        try:
            yield self.session
        except Exception as exp:
            await self.session.rollback()
            raise exp

    @_query_logger
    async def one_or_none(self) -> SQLModel | None:
        async with self._managed_session() as session:
            row = (
                (await session.execute(statement=self)).scalars().one_or_none()
            )

            if row is None:
                return None

            return row

    @_query_logger
    async def one(self) -> SQLModel:
        async with self._managed_session() as session:
            return (await session.execute(statement=self)).scalars().one()

    @_query_logger
    async def all(self) -> list[SQLModel]:
        async with self._managed_session() as session:
            return (await session.execute(statement=self)).scalars().all()

    @_query_logger
    async def first(self) -> SQLModel:
        async with self._managed_session() as session:
            return (await session.execute(statement=self)).scalars().first()


class BaseRepository:
    orm_model: Type[SQLModel]
    session_getter: Callable[[], AsyncSession] = get_context_session

    @classmethod
    def select(
        cls,
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
            session=cls.session_getter(),
        )
