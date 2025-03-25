from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_create: UserCreate, 
        session: AsyncSession = Depends(get_db)
    ) -> UserRead:
    """Creates a new user.

    This route handles POST requests to /users/. It creates a new user in the database.

    Args:
        user_create: User creation data (Pydantic model).
        session: The database session (dependency injection).

    Returns:
        UserRead: The created user data (Pydantic model).

    Raises:
        HTTPException: 400 Bad Request if a user with the same email already exists.
        HTTPException: 500 Internal Server Error if there's a database error.
    """
    user = User(
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name
    )

    user.set_password(user_create.password)

    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    except SQLAlchemyError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(f"Unable to create user: {err}"))

    return user


@router.get("/", response_model=list[UserRead])
async def get_users(session: AsyncSession = Depends(get_db)) -> list[UserRead]:
    """Retrieves all users.

    This route handles GET requests to /users/. It retrieves all users from the database.

    Args:
        session: The database session (dependency injection).

    Returns:
        list[UserRead]: A list of user data (Pydantic models).

    Raises:
        HTTPException: 404 Not Found if no users are found.
    """
    result = await session.execute(select(User))
    users = result.scalars().all()
    
    if len(users) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")

    return users


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_db)):
    """Retrieves a user by ID.

    This route handles GET requests to /users/:id. It retrieves a specific user from the database.

    Args:
        user_id: The ID of the user to retrieve.
        session: The database session (dependency injection).

    Returns:
        UserRead: The user data (Pydantic model).

    Raises:
        HTTPException: 404 Not Found if the user is not found.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
        user_id: int, 
        user_update: UserUpdate, 
        session: AsyncSession = Depends(get_db)
    ) -> UserRead:
    """Updates a user by ID.

    This route handles PUT requests to /users/:id. It updates a specific user in the database.

    Args:
        user_id: The ID of the user to update.
        user_update: User update data (Pydantic model).
        session: The database session (dependency injection).

    Returns:
        UserRead: The updated user data (Pydantic model).

    Raises:
        HTTPException: 404 Not Found if the user is not found.
        HTTPException: 400 Bad Request if there's a database error (e.g., unique constraint violation).
        HTTPException: 422 Unprocessable Entity if the update data is invalid.
        HTTPException: 500 Internal Server Error if there's a database error.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    try:
        if user_update.email:
            user.email = user_update.email
        if user_update.first_name:
            user.first_name = user_update.first_name
        if user_update.last_name:
            user.last_name = user_update.last_name
        if user_update.password:
            user.set_password(user_update.password)

        await session.commit()
        await session.refresh(user)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    except SQLAlchemyError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(f"Unable to update user: {err}"))
    

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_db)) -> None:
    """Deletes a user by ID.

    This route handles DELETE requests to /users/:id. It deletes a specific user from the database.

    Args:
        user_id: The ID of the user to delete.
        session: The database session (dependency injection).

    Returns:
        None

    Raises:
        HTTPException: 404 Not Found if the user is not found.
        HTTPException: 500 Internal Server Error if there's a database error.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    try:
        await session.delete(user)
        await session.commit()
    except SQLAlchemyError as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(f"Unable to delete user: {err}"))
    
    return None
