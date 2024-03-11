from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from tusdatos.core.auth_handler import encode_token, get_password_hash, verify_password
from tusdatos.core.database import get_db
from tusdatos.core.models.user import User
from tusdatos.core.schemas.auth import CreatedUser, CreateUser

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(path="/register", status_code=201)
async def register(user_data: CreateUser, db: Session = Depends(get_db)) -> CreatedUser:
    query = select(User).where(User.username == user_data.username)
    result = await db.execute(query)

    result = result.scalars().first()

    if result:
        detail = "User with the same username or document number already exists"
        raise HTTPException(status_code=400, detail=detail)

    db_user = User(
        name=user_data.name,
        username=user_data.username,
        password=get_password_hash(user_data.password),
    )

    db.add(db_user)

    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.post(path="/token")
async def login(
    auth_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    query = select(User).where(User.username == auth_data.username)
    result = await db.execute(query)

    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(auth_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = encode_token(user.id)

    return {"access_token": token, "token_type": "bearer"}
