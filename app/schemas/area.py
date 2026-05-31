from typing import Optional

from pydantic import BaseModel


class AreaOut(BaseModel):
    id: str
    nome: str
    municipio: str
    produtorId: Optional[str] = None
    tecnicoAtribuidoId: Optional[str] = None
    status: str
    percentualRegeneracao: float
    centroLat: float
    centroLng: float
    raioMetros: Optional[float] = None
    ultimaEvidencia: Optional[str] = None
    totalEvidencias: int
    updatedAt: str


class AreaCreate(BaseModel):
    nome: str
    municipio: str
    produtorId: Optional[str] = None
    tecnicoAtribuidoId: Optional[str] = None
    status: str = "REGULAR"
    percentualRegeneracao: float = 0.0
    centroLat: float
    centroLng: float
    raioMetros: Optional[float] = None


class AreaUpdate(BaseModel):
    nome: Optional[str] = None
    status: Optional[str] = None
    percentualRegeneracao: Optional[float] = None
    tecnicoAtribuidoId: Optional[str] = None
    centroLat: Optional[float] = None
    centroLng: Optional[float] = None
    raioMetros: Optional[float] = None
