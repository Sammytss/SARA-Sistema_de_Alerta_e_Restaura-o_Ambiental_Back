"""add polygon to areas and satellite_frames table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-31

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Polígono na tabela areas (fonte: SIGCAR ou demarcação manual)
    op.add_column(
        "areas",
        sa.Column(
            "geometria",
            geoalchemy2.types.Geography(geometry_type="POLYGON", srid=4326),
            nullable=True,
        ),
    )
    op.add_column(
        "areas",
        sa.Column("poligono_json", sa.Text, nullable=True),
    )

    # Tabela de frames de satélite (cache MapBiomas/Sentinel-2)
    op.create_table(
        "satellite_frames",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "area_id",
            sa.String(36),
            sa.ForeignKey("areas.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("ano", sa.Integer, nullable=False),
        sa.Column("camada", sa.String(20), nullable=False, server_default="LAND_COVER"),
        sa.Column("caminho_arquivo", sa.Text, nullable=True),
        sa.Column("imagem_url", sa.Text, nullable=True),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("percentual_vegetacao", sa.Float, nullable=True),
        sa.Column("classes_json", sa.Text, nullable=True),
        sa.Column("fonte", sa.String(20), nullable=False, server_default="MAPBIOMAS"),
        sa.Column(
            "gerado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("area_id", "ano", "camada", name="uq_satellite_area_ano_camada"),
    )
    op.create_index("ix_satellite_area_id", "satellite_frames", ["area_id"])
    op.create_index("ix_satellite_ano", "satellite_frames", ["ano"])


def downgrade() -> None:
    op.drop_index("ix_satellite_ano", "satellite_frames")
    op.drop_index("ix_satellite_area_id", "satellite_frames")
    op.drop_table("satellite_frames")
    op.drop_column("areas", "poligono_json")
    op.drop_column("areas", "geometria")
