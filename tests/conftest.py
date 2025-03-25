from typing import Generator, AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from async_asgi_testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from load_dotenv import load_dotenv
import os

from app.database.database import dbmanager, get_db
from app.models.user import Base
from main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_db() -> Generator:
    """Sets up and tears down the test database.

    This fixture is used to create and drop the test database before and after the test session.
    It uses environment variables to get the database URL.

    Yields:
        None
    """
    load_dotenv()
    engine = create_engine(os.getenv("TEST_DATABASE_URL"))

    with engine.begin():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        yield
        Base.metadata.drop_all(engine)


@pytest_asyncio.fixture(autouse=True)
async def session() -> AsyncGenerator:
    """Provides an asynchronous database session for each test.

    This fixture creates an asynchronous database session using the TEST_DATABASE_URL environment variable.
    The session is automatically rolled back after each test to ensure isolation.
    It also overrides the get_db dependency in the main app to use this session during tests.

    Yields:
        AsyncSession: An asynchronous database session.
    """
    load_dotenv()
    async_engine = create_async_engine(os.getenv("DATABASE_URL"))

    async with async_engine.begin() as conn:
        async_session = AsyncSession(bind=conn, expire_on_commit=False)
        
        dbmanager.set_test_session(async_session)

        async def test_get_session() -> AsyncGenerator[AsyncSession, None]:
            try:
                yield async_session
            except SQLAlchemyError:
                raise
            finally:
                dbmanager.reset_test_session()


        app.dependency_overrides[get_db] = test_get_session

        
        yield async_session
        await async_session.rollback()
        await async_session.close()
        await conn.rollback()
        await async_engine.dispose()


@pytest_asyncio.fixture
async def client():
    """Provides a test client for making HTTP requests.

    This fixture creates a TestClient instance for making HTTP requests to the FastAPI application.

    Yields:
        TestClient: A test client instance.
    """
    scope = {"test_client": "127.0.0.1:8000"}

    async with TestClient(app, scope=scope) as test_client:
        yield test_client