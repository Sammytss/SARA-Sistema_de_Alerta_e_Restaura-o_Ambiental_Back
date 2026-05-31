from typing import Optional

from pydantic import BaseModel


class FotoIn(BaseModel):
    pathLocal: Optional[str] = None
    remoteUrl: Optional[str] = None
    latitude: float
    longitude: float
    capturadaEm: str


class EvidenciaIn(BaseModel):
    id: str                     # UUID gerado pelo cliente para idempotência
    areaId: str
    autorId: str
    autorNome: str
    tipo: str                   # VISTORIA | PLANTIO | REGENERACAO | OCORRENCIA
    fotos: list[FotoIn]
    latitude: float
    longitude: float
    precisaoGps: Optional[float] = None
    observacoes: str = ""
    dataRegistro: str           # ISO8601


class EvidenciaOut(BaseModel):
    id: str
    areaId: str
    autorId: str
    autorNome: str
    tipo: str
    latitude: float
    longitude: float
    precisaoGps: Optional[float] = None
    observacoes: str
    dataRegistro: str
    updatedAt: str
