from typing import Optional

from pydantic import BaseModel


class SatelliteFrameOut(BaseModel):
    id: str
    areaId: str
    ano: int
    camada: str                              # LAND_COVER | TRUE_COLOR | NDVI
    imagemUrl: str
    tileUrl: Optional[str] = None           # XYZ tile template para flutter_map (real imagery)
    thumbnailUrl: Optional[str] = None
    percentualVegetacao: Optional[float] = None
    classes: Optional[dict[str, float]] = None
    fonte: str


class SatelliteTimelineOut(BaseModel):
    frames: list[SatelliteFrameOut]
    geometria: str                           # polygon | circle | point
