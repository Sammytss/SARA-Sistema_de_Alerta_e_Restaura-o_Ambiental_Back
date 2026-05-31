import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, String, Text

from app.core.db import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    senha_hash = Column(Text, nullable=False)
    perfil = Column(String(50), nullable=False)          # GESTOR | TECNICO | PRODUTOR | PUBLICO
    status = Column(String(20), nullable=False, default="ATIVO")  # ATIVO | INATIVO | BLOQUEADO
    telefone = Column(String(20), nullable=True)
    documento = Column(String(50), nullable=True)
    orgao_instituicao = Column(String(255), nullable=True)
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
