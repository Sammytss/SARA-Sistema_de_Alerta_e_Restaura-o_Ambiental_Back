from datetime import UTC, datetime, timedelta

import bcrypt as _bcrypt
from jose import JWTError, jwt

from app.core.config import settings


# ── Senha ─────────────────────────────────────────────────────────

def hash_senha(senha: str) -> str:
    return _bcrypt.hashpw(senha.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    return _bcrypt.checkpw(senha_plain.encode("utf-8"), senha_hash.encode("utf-8"))


# ── JWT ───────────────────────────────────────────────────────────

def criar_access_token(user_id: str) -> str:
    exp = datetime.now(UTC) + timedelta(minutes=settings.access_ttl_min)
    return jwt.encode(
        {"sub": user_id, "type": "access", "exp": exp},
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )


def criar_refresh_token(user_id: str) -> str:
    exp = datetime.now(UTC) + timedelta(days=settings.refresh_ttl_days)
    return jwt.encode(
        {"sub": user_id, "type": "refresh", "exp": exp},
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )


def decodificar_token(token: str, expected_type: str = "access") -> str | None:
    """Valida o token e retorna o user_id, ou None se inválido/expirado."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_alg]
        )
        if payload.get("type") != expected_type:
            return None
        return payload.get("sub")
    except JWTError:
        return None
