from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_usuario_or_401
from app.core.db import get_db
from app.repositories import alerta as repo_alerta
from app.schemas.alerta import AlertaOut

router = APIRouter(prefix="/alertas", tags=["alertas"])


def _to_out(a) -> AlertaOut:
    return AlertaOut(
        id=a.id,
        fonte=a.fonte,
        tipo=a.tipo,
        severidade=a.severidade,
        latitude=a.latitude,
        longitude=a.longitude,
        distanciaMetros=a.distancia_metros,
        areaId=a.area_id,
        detectadoEm=a.detectado_em.isoformat(),
        lido=a.lido,
    )


@router.get("", response_model=list[AlertaOut])
def list_alertas(
    since: str | None = None,
    areaId: str | None = None,
    u=Depends(get_usuario_or_401),
    db: Session = Depends(get_db),
):
    dt: datetime | None = None
    if since:
        try:
            dt = datetime.fromisoformat(since)
        except ValueError:
            raise HTTPException(400, "Parâmetro 'since' inválido. Use ISO8601.")

    alertas = repo_alerta.get_all(db, since=dt, area_id=areaId)
    return [_to_out(a) for a in alertas]


@router.patch("/{alerta_id}/lido")
def marcar_lido(
    alerta_id: str,
    u=Depends(get_usuario_or_401),
    db: Session = Depends(get_db),
):
    alerta = repo_alerta.get_by_id(db, alerta_id)
    if alerta is None:
        raise HTTPException(404, "Alerta não encontrado.")
    alerta.lido = True
    db.commit()
    return {"ok": True}
