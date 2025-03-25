from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_scoped_session
from load_dotenv import load_dotenv
from contextvars import ContextVar
from sqlalchemy.orm import sessionmaker
import asyncio
import os

from app.models.user import Base


class DatabaseManager:
    """Manages the database connection and sessions.

    This class handles the creation of the database engine, session maker, and provides methods for 
    managing database sessions, including setting up test sessions.
    """
    def __init__(self):
        """Initializes the DatabaseManager with an AsyncEngine, session maker, and context for test sessions."""
        self.engine = AsyncEngine
        self.session_maker = None
        self.session = None
        self._test_session_context: ContextVar[AsyncSession | None] = ContextVar("test_session", default=None)


    async def init_db(self):
        """
        Initializes the database connection and creates all tables.

        Loads environment variables, creates an async engine using the DATABASE_URL, 
        creates a session maker, and creates all tables defined in Base.metadata.
        """
        load_dotenv()
        os.getenv("DATABASE_URL")

        self.engine = create_async_engine(
            os.getenv("DATABASE_URL"),
            echo=True
        )

        self.session_maker = sessionmaker(
            bind=self.engine, 
            class_=AsyncSession, 
            autoflush=False,
            expire_on_commit=False
        )

        self.session = async_scoped_session(self.session_maker, scopefunc=asyncio.current_task)

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        

    async def close(self):
        """
        Closes the database connection.

        Disposes of the database engine. Raises an exception if the engine is not initialized.
        """
        if self.engine is not None:
            await self.engine.dispose()
        else:
            raise Exception("Can't dispose engine. Engine not initialized")


    def set_test_session(self, session: AsyncSession):
        """Sets a test session in the context variable.

        Args:
            session: The AsyncSession to set as the test session.
        """
        self._test_session_context.set(session)


    def reset_test_session(self):
        """Resets the test session context variable to None."""
        self._test_session_context.set(None)


dbmanager = DatabaseManager()


async def get_db():
    """
    Provides a database session to the application.

    This function is used as a dependency injection in FastAPI routes. It yields a database session.
    If a test session is set, it yields the test session; otherwise, it yields a session from the session maker.
    """
    session = dbmanager.session()
    if session is None:
        raise Exception("DatabaseSessionManager is not initialized")
    try:
        if test_session := dbmanager._test_session_context.get():
            yield test_session
        else:
            yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()