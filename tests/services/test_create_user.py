import pytest
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select

from tusdatos.core.models.user import User
from tusdatos.core.schemas.auth import CreateUser
from tusdatos.services.users import create_user, user_login


@pytest.fixture
def user_data():
    return CreateUser(
        name="Test User",
        username="testuser",
        password="password123",
    )


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_create_user_new_username(self, async_db_session, user_data):
        user = await create_user(db=async_db_session, user_data=user_data)

        query = select(User).where(User.username == user_data.username)
        result = await async_db_session.execute(query)
        created_user = result.scalars().first()

        assert user.username == user_data.username
        assert user.name == user_data.name

        assert created_user is not None

    @pytest.mark.asyncio
    async def test_create_user_existing_username(self, async_db_session, user_data):
        await create_user(db=async_db_session, user_data=user_data)

        with pytest.raises(HTTPException) as exc_info:
            await create_user(db=async_db_session, user_data=user_data)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "User with the same username or document number already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_user_password_hashing(self, async_db_session, user_data):
        user = await create_user(db=async_db_session, user_data=user_data)

        assert user.password != user_data.password


class TestUserLogin:
    @pytest.mark.asyncio
    async def test_user_login_valid_credentials(self, async_db_session, user_data):
        await create_user(db=async_db_session, user_data=user_data)

        auth_data = OAuth2PasswordRequestForm(
            username=user_data.username,
            password=user_data.password,
        )

        token = await user_login(async_db_session, auth_data)

        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_user_login_invalid_credentials(self, async_db_session, user_data):
        await create_user(db=async_db_session, user_data=user_data)

        auth_data = OAuth2PasswordRequestForm(
            username=user_data.username,
            password="Wrong password",
        )

        with pytest.raises(HTTPException) as exc_info:
            await user_login(db=async_db_session, auth_data=auth_data)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid username or password"
