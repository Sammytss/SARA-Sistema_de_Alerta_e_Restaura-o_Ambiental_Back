from typing import Optional

from pydantic import BaseModel


class AlertaOut(BaseModel):
    id: str
    fonte: str          # INPE | CIGMA | MAPBIOMAS
    tipo: str           # FOGO | DESMATAMENTO | SECA
    severidade: str     # BAIXA | MEDIA | ALTA | CRITICA
    latitude: float
    longitude: float
    distanciaMetros: Optional[float] = None
    areaId: Optional[str] = None
    detectadoEm: str    # ISO8601
    lido: bool
