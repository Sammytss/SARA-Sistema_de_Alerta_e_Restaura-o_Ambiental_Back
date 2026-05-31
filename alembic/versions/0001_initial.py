"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-31

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "usuarios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("senha_hash", sa.Text, nullable=False),
        sa.Column("perfil", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="ATIVO"),
        sa.Column("telefone", sa.String(20), nullable=True),
        sa.Column("documento", sa.String(50), nullable=True),
        sa.Column("orgao_instituicao", sa.String(255), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    op.create_table(
        "areas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("municipio", sa.String(255), nullable=False),
        sa.Column("produtor_id", sa.String(36), nullable=True),
        sa.Column("tecnico_atribuido_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="REGULAR"),
        sa.Column(
            "percentual_regeneracao", sa.Float, nullable=False, server_default="0.0"
        ),
        sa.Column("centro_lat", sa.Float, nullable=False),
        sa.Column("centro_lng", sa.Float, nullable=False),
        sa.Column(
            "localizacao",
            geoalchemy2.types.Geography(geometry_type="POINT", srid=4326),
            nullable=True,
        ),
        sa.Column("raio_metros", sa.Float, nullable=True),
        sa.Column("ultima_evidencia", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_evidencias", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_areas_municipio", "areas", ["municipio"])
    op.create_index("ix_areas_produtor", "areas", ["produtor_id"])
    op.create_index("ix_areas_tecnico", "areas", ["tecnico_atribuido_id"])

    op.create_table(
        "evidencias",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("area_id", sa.String(36), nullable=False),
        sa.Column("autor_id", sa.String(36), nullable=False),
        sa.Column("autor_nome", sa.String(255), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column(
            "localizacao",
            geoalchemy2.types.Geography(geometry_type="POINT", srid=4326),
            nullable=True,
        ),
        sa.Column("precisao_gps", sa.Float, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=False, server_default=""),
        sa.Column("data_registro", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_evidencias_area", "evidencias", ["area_id"])

    op.create_table(
        "fotos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("evidencia_id", sa.String(36), nullable=False),
        sa.Column("path_local", sa.Text, nullable=True),
        sa.Column("remote_url", sa.Text, nullable=True),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column("capturada_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "uploaded", sa.Boolean, nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_fotos_evidencia", "fotos", ["evidencia_id"])

    op.create_table(
        "alertas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("fonte", sa.String(20), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("severidade", sa.String(20), nullable=False, server_default="MEDIA"),
        sa.Column("latitude", sa.Float, nullable=False),
        sa.Column("longitude", sa.Float, nullable=False),
        sa.Column(
            "localizacao",
            geoalchemy2.types.Geography(geometry_type="POINT", srid=4326),
            nullable=False,
        ),
        sa.Column("distancia_metros", sa.Float, nullable=True),
        sa.Column("area_id", sa.String(36), nullable=True),
        sa.Column("detectado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "lido", sa.Boolean, nullable=False, server_default=sa.false()
        ),
        sa.Column("hash_dedupe", sa.Text, nullable=True, unique=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_alertas_area", "alertas", ["area_id"])
    op.create_index("ix_alertas_detectado", "alertas", ["detectado_em"])


def downgrade() -> None:
    op.drop_table("alertas")
    op.drop_table("fotos")
    op.drop_table("evidencias")
    op.drop_table("areas")
    op.drop_table("usuarios")
    op.execute("DROP EXTENSION IF EXISTS postgis CASCADE")
