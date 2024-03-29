import asyncio
from asyncio import Semaphore
from typing import Literal

import httpx
from httpx import AsyncClient, codes
from pydantic import ValidationError

from tusdatos.core.schemas import Cause, CauseCollection, LegalActions, TrialDetail


class JudicialProcessScraper:
    BASE_URL: str = "https://api.funcionjudicial.gob.ec"
    HEADERS: dict[str, str] = {"Content-Type": "application/json"}

    def __init__(
        self,
        search_role: Literal["ACTOR", "DEMANDADO"],
        user_document_num: str,
        timeout: int = 20,
        max_concurrent_requests: int = 15,
    ):
        self.search_role: str = search_role
        self.timeout: int = timeout

        self.user_document_num: str = user_document_num
        self.semaphore = Semaphore(max_concurrent_requests)

    def _search_arguments(self) -> dict:
        search_role = self.search_role.upper()

        return {
            "actor": {
                "cedulaActor": self.user_document_num if search_role == "ACTOR" else "",
            },
            "demandado": {
                "cedulaDemandado": self.user_document_num if search_role == "DEMANDADO" else "",
            },
        }

    async def _search_legal_actions(
        self,
        client: AsyncClient,
        incidente_judicatura_id: str,
        judicatura_id: int,
        juicio_id: int,
        movimiento_juicio_incidente_id: str,
    ) -> list[LegalActions]:
        async with self.semaphore:
            legal_actions_response = await client.post(
                headers=self.HEADERS,
                url=f"{self.BASE_URL}/EXPEL-CONSULTA-CAUSAS-SERVICE/api/consulta-causas/informacion/actuacionesJudiciales",
                timeout=self.timeout,
                json={
                    "idIncidenteJudicatura": incidente_judicatura_id,
                    "idJudicatura": judicatura_id,
                    "idJuicio": juicio_id,
                    "idMovimientoJuicioIncidente": movimiento_juicio_incidente_id,
                },
            )

        if legal_actions_response.status_code != codes.OK:
            detail = "Unexpected status code when consulting the legal actions of a trial."
            raise Exception(detail)

        try:
            legal_actions: list[LegalActions] = []
            for raw_data in legal_actions_response.json():
                legal_actions.append(LegalActions(**raw_data))
        except ValidationError:
            detail = "The response was not obtained with the pre-established format when consulting the legal actions of a trial."
            raise ValueError(detail)

        return legal_actions

    async def _search_trial_details(self, client: AsyncClient, cause: Cause) -> list[TrialDetail]:
        async with self.semaphore:
            trial_detail_response = await client.get(
                headers=self.HEADERS,
                timeout=self.timeout,
                url=f"{self.BASE_URL}/EXPEL-CONSULTA-CAUSAS-CLEX-SERVICE/api/consulta-causas-clex/informacion/getIncidenteJudicatura/{cause.idJuicio}",
            )

        if trial_detail_response.status_code != codes.OK:
            detail = "Unexpected status code when consulting the details of the trials."
            raise Exception(detail)

        try:
            trial_details: list[TrialDetail] = []
            for raw_data in trial_detail_response.json():
                trial_details.append(TrialDetail(**raw_data))
        except ValidationError:
            detail = "The response was not obtained with the pre-established format when consulting the details of trials."
            raise ValueError(detail)

        for trial_detail in trial_details:
            for trial_incident in trial_detail.lstIncidenteJudicatura:
                trial_incident.legal_actions = await self._search_legal_actions(
                    client=client,
                    incidente_judicatura_id=trial_incident.idIncidenteJudicatura,
                    judicatura_id=trial_detail.idJudicatura,
                    juicio_id=cause.idJuicio,
                    movimiento_juicio_incidente_id=trial_incident.idMovimientoJuicioIncidente,
                )

        cause.details = trial_details

    async def _count_causes(self, client: AsyncClient) -> int:
        async with self.semaphore:
            response = await client.post(
                headers=self.HEADERS,
                json=self._search_arguments(),
                timeout=self.timeout,
                url=f"{self.BASE_URL}/EXPEL-CONSULTA-CAUSAS-SERVICE/api/consulta-causas/informacion/contarCausas",
            )

        if response.status_code != codes.OK:
            detail = "Unexpected status code when consulting the the number of records."
            raise Exception(detail)

        if not response.text.isnumeric():
            detail = "The response was not obtained with the pre-established format when consulting the number of records."
            raise ValueError(detail)

        return int(response.text)

    async def _search_all_causes(self, client: AsyncClient) -> list[Cause]:
        total_causes = await self._count_causes(client=client)

        async with self.semaphore:
            response = await client.post(
                headers=self.HEADERS,
                json=self._search_arguments(),
                timeout=self.timeout,
                url=f"{self.BASE_URL}/EXPEL-CONSULTA-CAUSAS-SERVICE/api/consulta-causas/informacion/buscarCausas?page=1&size={total_causes}",
            )

        if response.status_code != codes.OK:
            detail = "The expected response was not obtained when consulting the court cases."
            raise Exception(detail)

        try:
            causes: list[Cause] = []
            for raw_data in response.json():
                causes.append(Cause(**raw_data))
        except ValidationError:
            detail = "The cause data does not comply with the pre-established structure."
            raise ValueError(detail)

        return causes

    async def extract_data(self) -> CauseCollection:
        async with httpx.AsyncClient() as client:
            self._extracted_data = await self._search_all_causes(client=client)

            corroutines = []
            for cause in self._extracted_data:
                corroutines.append(self._search_trial_details(client=client, cause=cause))

            await asyncio.gather(*corroutines)

        return CauseCollection(causes=self._extracted_data)
