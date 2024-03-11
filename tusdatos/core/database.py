from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from tusdatos.core.settings import settings

# Mongo DB (Motor)
# =======================

client = AsyncIOMotorClient(settings.MONOG_URI)

judicial_processes_db = client.get_database("judicial_processes")

trials_as_actor_db = judicial_processes_db.get_collection("trials_as_actor")
trails_as_defendant_db = judicial_processes_db.get_collection("trails_as_defendant")

# PosgreSQL (SQLAlchemy)
# =======================

engine = create_async_engine(settings.POSTGRES_URL)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        await db.close()
