from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tusdatos.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=32))
    username: Mapped[str] = mapped_column(String(length=128), unique=True)
    password: Mapped[str]
