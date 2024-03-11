from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from tusdatos.core.database import get_db
from tusdatos.core.models.user import User
from tusdatos.core.settings import settings

ALGORITHM = "HS256"

security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def encode_token(user_id: int) -> str:
    payload = {
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
        "sub": str(user_id),
    }

    return jwt.encode(claims=payload, key=settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token=token, key=settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        detail = "Signature has expired"
        raise HTTPException(status_code=401, detail=detail)
    except jwt.JWTError:
        detail = "Invalid token"
        raise HTTPException(status_code=401, detail=detail)

    return int(payload["sub"])


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    user_id = decode_token(token=token)

    if user_id is None:
        detail = "Invalid token"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        detail = "Invalid token"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    return user
