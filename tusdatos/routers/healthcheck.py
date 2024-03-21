from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from tusdatos.core.database import client as mongo_client
from tusdatos.core.database import get_db

router = APIRouter(tags=["Health Checks"])


@router.get("/healthcheck")
async def healthcheck(postgres_db: Session = Depends(get_db)) -> dict:
    try:
        await postgres_db.execute(text("SELECT 1"))
        postgres_status = "ok"
    except OperationalError:
        postgres_status = "error"

    try:
        await mongo_client.get_database("admin").command("ping")
        mongo_status = "ok"
    except Exception:
        mongo_status = "error"

    return {
        "MongoDB": mongo_status,
        "PostgreSQL": postgres_status,
    }
