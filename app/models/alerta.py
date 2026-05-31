import uuid
from datetime import UTC, datetime

from geoalchemy2 import Geography
from sqlalchemy import Boolean, Column, DateTime, Float, String, Text

from app.core.db import Base


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fonte = Column(String(20), nullable=False)          # INPE | CIGMA | MAPBIOMAS
    tipo = Column(String(20), nullable=False)           # FOGO | DESMATAMENTO | SECA
    severidade = Column(String(20), nullable=False, default="MEDIA")  # BAIXA | MEDIA | ALTA | CRITICA
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    localizacao = Column(Geography("POINT", srid=4326), nullable=False)
    distancia_metros = Column(Float, nullable=True)
    area_id = Column(String(36), nullable=True, index=True)
    detectado_em = Column(DateTime(timezone=True), nullable=False)
    lido = Column(Boolean, nullable=False, default=False)
    hash_dedupe = Column(Text, nullable=True, unique=True)  # deduplicação por fonte+coord+data
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
