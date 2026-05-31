from datetime import UTC, datetime

from geoalchemy2 import Geography
from sqlalchemy import Column, DateTime, Float, String, Text

from app.core.db import Base


class Evidencia(Base):
    __tablename__ = "evidencias"

    id = Column(String(36), primary_key=True)   # UUID gerado pelo cliente (idempotência)
    area_id = Column(String(36), nullable=False, index=True)
    autor_id = Column(String(36), nullable=False)
    autor_nome = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=False)    # VISTORIA | PLANTIO | REGENERACAO | OCORRENCIA
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    localizacao = Column(Geography("POINT", srid=4326), nullable=True)
    precisao_gps = Column(Float, nullable=True)
    observacoes = Column(Text, nullable=False, default="")
    data_registro = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
