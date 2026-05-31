from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac import has_permissao
from app.core.security import decodificar_token

_bearer = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
) -> str:
    user_id = decodificar_token(credentials.credentials, expected_type="access")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def get_usuario_or_401(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    from app.repositories import usuario as repo_usuario

    u = repo_usuario.get_by_id(db, user_id)
    if u is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )
    return u


def require_perfil(*perfis: str):
    """Dependency que exige um dos perfis informados."""
    def _dep(u=Depends(get_usuario_or_401)):
        if u.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Perfil '{u.perfil}' não autorizado. Requer: {', '.join(perfis)}.",
            )
        return u
    return _dep


def require_permissao(permissao: str):
    """Dependency que exige uma permissão específica (baseada no perfil)."""
    def _dep(u=Depends(get_usuario_or_401)):
        if not has_permissao(u.perfil, permissao):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão '{permissao}' necessária.",
            )
        return u
    return _dep
