from pydantic import BaseModel, field_validator

from tusdatos.utils import sanitize_text


class LegalActions(BaseModel):
    actividad: str
    alias: str
    codigo: int
    escapeOut: str
    fecha: str
    idJudicatura: str
    idJuicio: str
    idMovimientoJuicioIncidente: int
    ieDocumentoAdjunto: str
    ieTablaReferencia: str
    nombreArchivo: str
    origen: str
    tipo: str
    tipoIngreso: str
    uuid: str
    visible: str

    @field_validator("actividad", mode="after")
    @classmethod
    def sanitize_actividad(cls, actividad: str) -> str:
        return sanitize_text(actividad)


class Litigant(BaseModel):
    tipoLitigante: str
    nombresLitigante: str
    representadoPor: str | None
    idLitigante: int


class Defendant(BaseModel):
    tipoLitigante: str
    nombresLitigante: str
    representadoPor: str | None
    idLitigante: int


class TrialIncident(BaseModel):
    fechaCrea: str
    idIncidenteJudicatura: int
    idJudicaturaDestino: str
    idMovimientoJuicioIncidente: int
    incidente: int
    litiganteActor: str | None
    litiganteDemandado: str | None
    lstLitiganteActor: list[Litigant] | None
    lstLitiganteDemandado: list[Defendant] | None

    # Additional Fields
    legal_actions: list[LegalActions] | None = None


class TrialDetail(BaseModel):
    ciudad: str
    idJudicatura: str
    nombreJudicatura: str
    lstIncidenteJudicatura: list[TrialIncident]


class Cause(BaseModel):
    estadoActual: str | None
    fechaIngreso: str | None
    id: int
    idJuicio: str | None
    idMateria: int | None
    iedocumentoAdjunto: str | None
    nombreDelito: str | None

    # Additional Fields
    details: list[TrialDetail] | None = None


class CauseCollection(BaseModel):
    causes: list[Cause]


class TrialDetailCollecion(BaseModel):
    details: list[TrialDetail]


class LegalActionsCollection(BaseModel):
    actions: list[LegalActions]
