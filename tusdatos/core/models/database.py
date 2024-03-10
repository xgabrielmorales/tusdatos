from motor.motor_asyncio import AsyncIOMotorClient

from tusdatos.core.settings import settings

client = AsyncIOMotorClient(settings.MONOG_URI)

judicial_processes_db = client.get_database("judicial_processes")

trials_as_actor_db = judicial_processes_db.get_collection("trials_as_actor")
trails_as_defendant_db = judicial_processes_db.get_collection("trails_as_defendant")
