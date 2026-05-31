from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id, get_usuario_or_401
from app.core.db import get_db
from app.core.rbac import get_permissoes
from app.core.security import (
    criar_access_token,
    criar_refresh_token,
    decodificar_token,
    verificar_senha,
)
from app.repositories import usuario as repo_usuario
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
_limiter = Limiter(key_func=get_remote_address)


def _usuario_para_map(u, access_token: str | None = None) -> dict:
    return {
        "id": u.id,
        "nome": u.nome,
        "email": u.email,
        "perfil": u.perfil,
        "permissoes": get_permissoes(u.perfil),
        "token": access_token,
        "status": u.status,
        "ultimoLogin": datetime.now(UTC).isoformat(),
        "telefone": u.telefone,
        "documento": u.documento,
        "orgaoInstituicao": u.orgao_instituicao,
        "dataCadastro": u.criado_em.isoformat() if u.criado_em else None,
    }


@router.post("/login", response_model=TokenResponse)
@_limiter.limit("10/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    u = repo_usuario.get_by_email(db, body.email)
    if u is None:
        raise HTTPException(
            status_code=404,
            detail="E-mail não encontrado. Verifique e tente novamente.",
        )
    if not verificar_senha(body.senha, u.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta. Tente novamente.",
        )
    if u.status != "ATIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sua conta está {u.status.lower()}. Entre em contato com o administrador.",
        )

    access = criar_access_token(u.id)
    refresh = criar_refresh_token(u.id)
    return TokenResponse(
        accessToken=access,
        refreshToken=refresh,
        usuario=_usuario_para_map(u, access),
    )


@router.post("/refresh")
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    user_id = decodificar_token(body.refreshToken, expected_type="refresh")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado.",
        )
    u = repo_usuario.get_by_id(db, user_id)
    if u is None or u.status != "ATIVO":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo.",
        )
    return {"accessToken": criar_access_token(u.id)}


@router.get("/me")
def me(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    u = repo_usuario.get_by_id(db, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return _usuario_para_map(u)
