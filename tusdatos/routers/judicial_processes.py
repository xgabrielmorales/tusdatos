from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from tusdatos.core.auth_handler import get_current_user
from tusdatos.core.database import trials_as_actor_db, trials_as_defendant_db
from tusdatos.core.models import User
from tusdatos.core.schemas import (
    CauseCollection,
    LegalActionsCollection,
    TrialDetailCollecion,
)
from tusdatos.services.scraper import JudicialProcessScraper

router = APIRouter(
    prefix="/judicial-processes",
    tags=["Judicial Processes"],
)


COLLECTION = {
    "ACTOR": trials_as_actor_db,
    "DEMANDADO": trials_as_defendant_db,
}


@router.get(
    path="/search",
    description="Search and store a user's judicial process information.",
)
async def serach(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
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


@router.get(
    path="/causes",
    description="List the causes of judicial processes.",
)
async def causes(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> CauseCollection:

    judicial_proceedings = await COLLECTION[search_role].find_one(
        filter={"_id": user_document_num},
        projection={"_id": 0, "causes.details": 0},
    )

    if judicial_proceedings is None:
        detail = "No stored data was found for the given user."
        raise HTTPException(status_code=404, detail=detail)

    return judicial_proceedings


@router.get(
    path="/detials",
    description="List of details of a judicial process.",
)
async def detials(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    trial_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> TrialDetailCollecion:
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


@router.get(
    path="/actions",
    description="List of details of a judicial process.",
)
async def actions(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    judicature_id: str,
    judicature_incident_id: int,
    trial_id: str,
    trial_incident_movement_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> LegalActionsCollection:
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
