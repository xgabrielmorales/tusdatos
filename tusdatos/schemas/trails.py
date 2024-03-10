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


class TrailIncident(BaseModel):
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
    legal_actions: dict | None = None


class TrailDetail(BaseModel):
    ciudad: str
    idJudicatura: str
    nombreJudicatura: str
    lstIncidenteJudicatura: list[TrailIncident]


class Cause(BaseModel):
    cedula: str | None
    estadoActual: str | None
    fechaIngreso: str | None
    fechaProvidencia: str | None
    id: int
    idCanton: str | None
    idEstadoJuicio: str | None
    idJudicatura: str | None
    idJuicio: str | None
    idMateria: int | None
    idProvincia: str | None
    iedocumentoAdjunto: str | None
    nombre: str | None
    nombreDelito: str | None
    nombreEstadoJuicio: str | None
    nombreJudicatura: str | None
    nombreMateria: str | None
    nombreProvidencia: str | None
    nombreProvincia: str | None
    nombreTipoAccion: str | None
    nombreTipoResolucion: str | None

    # Additional Fields
    details: list[TrailDetail] | None = None
