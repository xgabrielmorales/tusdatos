from typing import Annotated

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from tusdatos.core.auth_handler import encode_token, get_password_hash, verify_password
from tusdatos.core.models.user import User
from tusdatos.core.schemas.auth import CreatedUserData


async def create_user(db: Session, user_data: CreatedUserData) -> User:
    query = select(User).where(User.username == user_data.username)
    result = await db.execute(query)

    result = result.scalars().first()

    if result:
        detail = "User with the same username or document number already exists"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    db_user = User(
        name=user_data.name,
        username=user_data.username,
        password=get_password_hash(user_data.password),
    )

    db.add(db_user)

    await db.commit()
    await db.refresh(db_user)

    return db_user


async def user_login(db: Session, auth_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    query = select(User).where(User.username == auth_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    if user is None or not verify_password(auth_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = encode_token(user.id)

    return token
