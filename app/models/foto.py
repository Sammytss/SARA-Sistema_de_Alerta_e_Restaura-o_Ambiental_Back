from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Float, String, Text

from app.core.db import Base


class Foto(Base):
    __tablename__ = "fotos"

    id = Column(String(36), primary_key=True)
    evidencia_id = Column(String(36), nullable=False, index=True)
    path_local = Column(Text, nullable=True)
    remote_url = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capturada_em = Column(DateTime(timezone=True), nullable=False)
    uploaded = Column(Boolean, nullable=False, default=True)
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
