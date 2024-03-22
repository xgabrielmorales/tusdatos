from typing import Literal

from fastapi.exceptions import HTTPException

from tusdatos.core.database import trials_as_actor_db, trials_as_defendant_db
from tusdatos.services.judicial_processes_scraper import JudicialProcessScraper

COLLECTION = {
    "ACTOR": trials_as_actor_db,
    "DEMANDADO": trials_as_defendant_db,
}


async def serach_judicial_processes(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
):
    scraper = JudicialProcessScraper(
        user_document_num=user_document_num,
        search_role=search_role,
    )
    causes = await scraper.extract_data()

    document = {
        "_id": user_document_num,
        **causes.model_dump(),
    }

    kwargs = {
        "filter": {"_id": user_document_num},
        "replacement": document,
        "upsert": True,
    }

    await COLLECTION[search_role].replace_one(**kwargs)

    return None


async def get_causes(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
):
    db = COLLECTION[search_role]

    breakpoint()

    judicial_proceedings = await db.find_one(
        filter={"_id": user_document_num},
        projection={"_id": 0, "causes.details": 0},
    )

    if judicial_proceedings is None:
        detail = "No stored data was found for the given user."
        raise HTTPException(status_code=404, detail=detail)

    return judicial_proceedings


async def get_details(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    trial_id: str,
) -> dict:
    pipeline = [
        {"$match": {"_id": user_document_num}},
        {"$unwind": "$causes"},
        {"$match": {"causes.idJuicio": trial_id}},
        {"$unwind": "$causes.details"},
        {"$replaceRoot": {"newRoot": "$causes.details"}},
    ]

    cursor = COLLECTION[search_role].aggregate(pipeline=pipeline)

    details = [document async for document in cursor]

    if not details:
        detail = "No stored data was found for the given user."
        raise HTTPException(status_code=404, detail=detail)

    return {"details": details}


async def get_actions(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    trial_id: str,
    judicature_id: str,
    judicature_incident_id: int,
    trial_incident_movement_id: int,
):
    pipeline = [
        {"$match": {"_id": user_document_num}},
        {"$unwind": "$causes"},
        {"$match": {"causes.idJuicio": trial_id}},
        {"$unwind": "$causes.details"},
        {"$match": {"causes.details.idJudicatura": judicature_id}},
        {"$unwind": "$causes.details.lstIncidenteJudicatura"},
        {
            "$match": {
                "causes.details.lstIncidenteJudicatura.idMovimientoJuicioIncidente": trial_incident_movement_id,
                "causes.details.lstIncidenteJudicatura.idIncidenteJudicatura": judicature_incident_id,
            },
        },
        {"$unwind": "$causes.details.lstIncidenteJudicatura.legal_actions"},
        {"$replaceRoot": {"newRoot": "$causes.details.lstIncidenteJudicatura.legal_actions"}},
    ]

    cursor = COLLECTION[search_role].aggregate(pipeline=pipeline)

    actions = [document async for document in cursor]

    if not actions:
        detail = "No stored data was found for the given user."
        raise HTTPException(status_code=404, detail=detail)

    return {"actions": actions}
