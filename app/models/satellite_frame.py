import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.core.db import Base


class SatelliteFrame(Base):
    __tablename__ = "satellite_frames"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    area_id = Column(String(36), sa.ForeignKey("areas.id", ondelete="CASCADE"), nullable=False, index=True)
    ano = Column(Integer, nullable=False)
    camada = Column(String(20), nullable=False, default="LAND_COVER")  # LAND_COVER | TRUE_COLOR | NDVI
    caminho_arquivo = Column(Text, nullable=True)   # path local em storage/
    imagem_url = Column(Text, nullable=True)        # URL pública servida pelo backend
    thumbnail_url = Column(Text, nullable=True)
    percentual_vegetacao = Column(Float, nullable=True)  # 0–100, % vegetação nativa
    classes_json = Column(Text, nullable=True)      # JSON: {nome_classe: percentual}
    fonte = Column(String(20), nullable=False, default="MAPBIOMAS")
    gerado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        sa.UniqueConstraint("area_id", "ano", "camada", name="uq_satellite_area_ano_camada"),
    )
