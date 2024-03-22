from typing import Annotated, Literal

from fastapi import APIRouter, Depends

from tusdatos.core.auth_handler import get_current_user
from tusdatos.core.models import User
from tusdatos.core.schemas import (
    CauseCollection,
    LegalActionsCollection,
    TrialDetailCollecion,
)
from tusdatos.services.judicial_processes import get_actions, get_causes, get_details, serach_judicial_processes

router = APIRouter(
    prefix="/judicial-processes",
    tags=["Judicial Processes"],
)


@router.get(
    path="/search",
    description="Search and store a user's judicial process information.",
)
async def search(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    return serach_judicial_processes()


@router.get(
    path="/causes",
    description="List the causes of judicial processes.",
)
async def causes(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> CauseCollection:
    return get_causes(
        search_role=search_role,
        user_document_num=user_document_num,
    )


@router.get(
    path="/details",
    description="List of details of a judicial process.",
)
async def details(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    trial_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> TrialDetailCollecion:
    return get_details(
        search_role=search_role,
        user_document_num=user_document_num,
        trial_id=trial_id,
    )


@router.get(
    path="/actions",
    description="List of details of a judicial process.",
)
async def actions(
    search_role: Literal["ACTOR", "DEMANDADO"],
    user_document_num: str,
    trial_id: str,
    judicature_id: str,
    judicature_incident_id: int,
    trial_incident_movement_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> LegalActionsCollection:
    return get_actions(
        search_role=search_role,
        user_document_num=user_document_num,
        trial_id=trial_id,
        judicature_id=judicature_id,
        judicature_incident_id=judicature_incident_id,
        trial_incident_movement_id=trial_incident_movement_id,
    )
