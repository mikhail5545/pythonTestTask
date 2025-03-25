import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from fastapi import status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from main import app


@pytest.mark.asyncio
async def test_create_user_success(client: TestClient, session: AsyncSession):
    """Tests successful user creation.

    Creates a user with valid data using POST /users/ and asserts:
        - 201 CREATED status code.
        - Correct user data in the response.
        - User exists in the database.

    Args:
        client: The test client.
        session: The database session.
    """
    user_data = {
        "first_name": "User",
        "last_name": "Test",
        "email": "usertest@test.com",
        "password": "Passaword123"
    }  

    response = await client.post("/users/", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    created_user = response.json()
    assert created_user["first_name"] == "User"
    assert created_user["email"] == "usertest@test.com"

    result = await session.execute(select(User).where(User.email == "usertest@test.com"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.first_name == "User"
    assert user.email == "usertest@test.com"


@pytest.mark.asyncio
async def test_create_user_invalid_data(client: TestClient, session: AsyncSession):
    """Tests user creation with invalid data.

    Attempts to create a user with invalid data using POST /users/ and asserts:
        - 422 UNPROCESSABLE ENTITY status code.

    Args:
        client: The test client.
        session: The database session.
    """
    user_data = {
        "first_name": "U",
        "last_name": "Test",
        "email": "usertest@test.com",
        "password": "pass"
    }  

    response = await client.post("/users/", json=user_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_user_not_found(client: TestClient, session: AsyncSession):
    """Tests getting a non-existent user.

    Attempts to get a user with ID 1 using GET /users/1 and asserts:
        - 404 NOT FOUND status code.
        - Correct error detail in the response.

    Args:
        client: The test client.
        session: The database session.
    """
    response = await client.get("/users/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found"
    

@pytest.mark.asyncio
async def test_get_user_success(client: TestClient, session: AsyncSession):
    """Tests getting an existing user.

    Creates a user, then retrieves it using GET /users/:id and asserts:
        - 200 OK status code.
        - Correct user data in the response.

    Args:
        client: The test client.
        session: The database session.
    """
    user_data = {
        "first_name": "User",
        "last_name": "Test",
        "email": "usertest@test.com",
        "password": "Passaword123"
    }  

    response = await client.post("/users/", json=user_data)
    user_id = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED

    response = await client.get(f"/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    user = response.json()
    assert user["first_name"] == "User"
    assert user["email"] == "usertest@test.com"


@pytest.mark.asyncio
async def test_get_users_success(client: TestClient, session: AsyncSession):
    """Tests getting all users.

    Creates two users, then retrieves all users using GET /users/ and asserts:
        - 200 OK status code.
        - Correct number of users in the response.
        - Correct user data in the response.

    Args:
        client: The test client.
        session: The database session.
    """
    user_data1 = {
        "first_name": "UserF",
        "last_name": "TestF",
        "email": "usertest1@test.com",
        "password": "Passaword123"
    }

    user_data2 = {
        "first_name": "UserS",
        "last_name": "TestS",
        "email": "usertest2@test.com",
        "password": "Passaword123"
    }

    response = await client.post("/users/", json=user_data1)
    assert response.status_code == status.HTTP_201_CREATED
    response = await client.post("/users/", json=user_data2)
    assert response.status_code == status.HTTP_201_CREATED

    result = await session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 2

    response = await client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) == 2
    assert users[0]["first_name"] == "UserF"
    assert users[1]["first_name"] == "UserS"
    

@pytest.mark.asyncio
async def test_get_users_not_found(client: TestClient, session: AsyncSession):
    """Tests getting users when no users exist.

    Attempts to get all users using GET /users/ and asserts:
        - 404 NOT FOUND status code.
        - Correct error detail in the response.

    Args:
        client: The test client.
        session: The database session.
    """
    response = await client.get("/users/")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Users not found"


@pytest.mark.asyncio
async def test_update_user_success(client: TestClient, session: AsyncSession):
    """Tests successful user update.

    Creates a user, then updates it with valid data using PUT /users/:id and asserts:
        - 200 OK status code.
        - Correct updated user data in the response.
        - User is updated in the database.

    Args:
        client: The test client.
        session: The database session.
    """
    user_data = {
        "first_name": "User",
        "last_name": "Test",
        "email": "usertest@test.com",
        "password": "Passaword123"
    }

    response = await client.post("/users/", json=user_data)
    user_id = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED

    user_data_updated = {
        "first_name": "UserU",
        "last_name": "TestU",
        "email": "usertest1@test.com",
        "password": "Passaword1234"
    }

    response = await client.put(f"/users/{user_id}", json=user_data_updated)
    assert response.status_code == status.HTTP_200_OK
    updated_user = response.json()
    assert updated_user["first_name"] == "UserU"
    assert updated_user["last_name"] == "TestU"
    assert updated_user["email"] == "usertest1@test.com"

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.first_name == "UserU"
    

@pytest.mark.asyncio
async def test_update_user_not_found(client: TestClient, session: AsyncSession):
    """Tests updating a non-existent user.

    Attempts to update a user with ID 1 using PUT /users/1 and asserts:
        - 404 NOT FOUND status code.
        - Correct error detail in the response.

    Args:
        client: The test client.
        session: The database session.
    """
    user_data_updated = {
        "first_name": "UserU",
        "last_name": "TestU",
        "email": "usertest1@test.com",
        "password": "Passaword1234"
    }

    response = await client.put("/users/1", json=user_data_updated)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_user_success(client: TestClient, session: AsyncSession):
    """Tests successful user deletion.

    Creates a user, then deletes it using DELETE /users/:id and asserts:
        - 204 NO CONTENT status code.

    Args:
        client: The test client.
        session: The database session.
    """
    user_data = {
        "first_name": "User",
        "last_name": "Test",
        "email": "usertest@test.com",
        "password": "Passaword123"
    }

    response = await client.post("/users/", json=user_data)
    user_id = response.json()["id"]

    assert response.status_code == status.HTTP_201_CREATED

    response = await client.delete(f"/users/{user_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
  

@pytest.mark.asyncio
async def test_delete_user_not_found(client: TestClient, session: AsyncSession):
    """Tests deleting a non-existent user.

    Attempts to delete a user with ID 1 using DELETE /users/1 and asserts:
        - 404 NOT FOUND status code.

    Args:
        client: The test client.
        session: The database session.
    """
    response = await client.delete("/users/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
