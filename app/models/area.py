import uuid
from datetime import UTC, datetime

from geoalchemy2 import Geography
from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.core.db import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    municipio = Column(String(255), nullable=False, index=True)
    produtor_id = Column(String(36), nullable=True, index=True)
    tecnico_atribuido_id = Column(String(36), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="REGULAR")  # REGULAR | ATENCAO | CRITICA
    percentual_regeneracao = Column(Float, nullable=False, default=0.0)
    centro_lat = Column(Float, nullable=False)
    centro_lng = Column(Float, nullable=False)
    localizacao = Column(Geography("POINT", srid=4326), nullable=True)
    geometria = Column(Geography("POLYGON", srid=4326), nullable=True)
    poligono_json = Column(Text, nullable=True)  # cache GeoJSON do polígono (redundante ao Geography)
    raio_metros = Column(Float, nullable=True)
    ultima_evidencia = Column(DateTime(timezone=True), nullable=True)
    total_evidencias = Column(Integer, nullable=False, default=0)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
