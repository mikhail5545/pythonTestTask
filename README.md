# Basic Asynchronous REST API for User Management with FastAPI, SQLAlchemy, and PostgreSQL

## Dependency managment
This API uses Poetry for dependency managment instead of pip. Learn more about Poetry - https://python-poetry.org/
All dependencies and project attributes located in `pyproject.toml`.
You can view all dependencies using:
poetry show
```bash
    poetry show --tree
```

## Installation

1.  **Clone repository:**
    ```bash
    git clone https://github.com/mikhail5545/pythonTestTask.git
    cd <path_to_cloned_repo>
    ```

2.  **Install poetry (if you don't have it):**
    -Linux/MacOS/WSL:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
    -Windows:
    ```PowerShell
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
    ```
2.  **You need to create a virtual environment:**
    ```bash
    poetry add pyproject.toml
    ```

3.  **Install dependencies:**
    ```bash
    poetry install --no-root
    ```

## Launch application

1.  Using .bashrc alias:
    ```bash
    source .bashrc
    run
    ```

2.  Manually using Uvicorn:
    ```bash
    poetry run uvicorn main:app --reload
    ```
    App will be available at `http://127.0.0.1:8000`.

## Run tests

1.  Using .bashrc alias:
    ```bash
    source .bashrc
    test
    ```

2.  Manually using pytest:
    ```bash
    poetry run pytest tests/
    ```

## API description

### User model

####Fields:
1.  id - int, Primary key
2.  first_name - str, Required
3.  last_name - str, Required
4.  email - str, Required
5.  password - str, Required. Password stores in hashed form. Hashing implemented using bcrypt.
6.  salt - str. - Increases safety. Utility-field for password. Auto-generated for each user.
7.  created_at - DateTime - auto-generated
8.  updated_at - DateTime - auto-generated


### Endpoints

* **User creation (POST /users/)**:
    * Request body: `{ "first_name": "User first name", "last_name": "User last name", "email": "user@example.com", "password": "securepassword" }`
    * Response (201 Created): `{ "id": 1, "first_name": "User first name", "last_name": "User last name", "email": "user@example.com", "created_at": "2023-10-27T10:00:00", "updated_at": "2023-10-27T10:00:00" }`
    * Response (400 Bad Request): `{ "detail": "Email already registered" }` or `{ "detail": "Invalid data" }`
* **Retrieve user by ID (GET /users/{user_id})**:
    * Response (200 OK): `{ "id": 1, "first_name": "User first name", "last_name": "User last name", "email": "user@example.com", "created_at": "2023-10-27T10:00:00", "updated_at": "2023-10-27T10:00:00" }`
    * Response (404 Not Found): `{ "detail": "User not found" }`
* **Update user by ID (PUT /users/{user_id})**:
    * Request body: `{ "first_name": "New first name", "last_name": "New last name", "email": "new_email@example.com", "password": "newsecurepassword" }` (all fields are optional)
    * Response (200 OK): `{ "id": 1, "first_name": "New first name", "last_name": "New last name", "email": "new_email@example.com", "created_at": "2023-10-27T10:00:00", "updated_at": "2023-10-27T10:30:00" }`
    * Response (404 Not Found): `{ "detail": "User not found" }`
    * Response (400 Bad Request): `{ "detail": "Invalid data" }` or `{ "detail": "Email already registered" }`
* **Delete user by ID (DELETE /users/{user_id})**:
    * Response (204 No Content): (Empty response body)
    * Response (404 Not Found): `{ "detail": "User not found" }`
* **Get all users (GET /users/)**:
    * Response (200 OK): `[{"id": 1, "first_name": "User first name", "last_name": "User last name", "email": "user@example.com", "created_at": "2023-10-27T10:00:00", "updated_at": "2023-10-27T10:00:00"}, {"id": 2, "first_name": "User2 first name", "last_name": "User2 last name", "email": "user2@example.com", "created_at": "2023-10-27T11:00:00", "updated_at": "2023-10-27T11:00:00"}]`
    * Response (404 Not Found): `{ "detail": "No users found" }` (if no users)

## Database

*   The application uses PostgreSQL as the database and asyncpg as database driver.
*   Database connection details are configured in the `database.py` file using `DatabaseManager` class.
*   SQLAlchemy is used as the ORM to interact with the database.

## Security

*   User passwords are not stored in plain text. They are hashed using bcrypt.
*   Each user has a unique salt generated for added security.

## Error Handling

*   The API returns appropriate HTTP status codes for different scenarios (e.g., 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 204 No Content).
*   Error responses include a `detail` field with a description of the error.