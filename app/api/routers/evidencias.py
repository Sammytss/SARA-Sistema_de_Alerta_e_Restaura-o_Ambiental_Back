import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import require_permissao
from app.core.config import settings
from app.core.db import get_db
from app.repositories import evidencia as repo_ev
from app.schemas.evidencia import EvidenciaIn, EvidenciaOut

router = APIRouter(tags=["evidencias"])


def _to_out(ev) -> EvidenciaOut:
    return EvidenciaOut(
        id=ev.id,
        areaId=ev.area_id,
        autorId=ev.autor_id,
        autorNome=ev.autor_nome,
        tipo=ev.tipo,
        latitude=ev.latitude,
        longitude=ev.longitude,
        precisaoGps=ev.precisao_gps,
        observacoes=ev.observacoes,
        dataRegistro=ev.data_registro.isoformat(),
        updatedAt=ev.updated_at.isoformat() if ev.updated_at else datetime.utcnow().isoformat(),
    )


@router.post("/fotos/upload")
async def upload_foto(
    file: UploadFile = File(...),
    u=Depends(require_permissao("EVIDENCE_CREATE")),
):
    ext = os.path.splitext(file.filename or "foto.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    dest = os.path.join(settings.upload_dir_path, filename)

    content = await file.read()
    max_bytes = settings.max_foto_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(400, f"Foto excede o limite de {settings.max_foto_mb} MB.")

    with open(dest, "wb") as f:
        f.write(content)

    return {"remoteUrl": f"/storage/{filename}"}


@router.post("/evidencias", response_model=EvidenciaOut, status_code=201)
def create_evidencia(
    body: EvidenciaIn,
    u=Depends(require_permissao("EVIDENCE_CREATE")),
    db: Session = Depends(get_db),
):
    # Idempotência: retorna existente se já sincronizado
    existing = repo_ev.get_by_id(db, body.id)
    if existing:
        return _to_out(existing)

    ev_data = {
        "id": body.id,
        "area_id": body.areaId,
        "autor_id": body.autorId,
        "autor_nome": body.autorNome,
        "tipo": body.tipo,
        "latitude": body.latitude,
        "longitude": body.longitude,
        "precisao_gps": body.precisaoGps,
        "observacoes": body.observacoes,
        "data_registro": datetime.fromisoformat(body.dataRegistro),
    }

    fotos_data = [
        {
            "id": f"{body.id}_{i}",
            "evidencia_id": body.id,
            "path_local": f.pathLocal,
            "remote_url": f.remoteUrl,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "capturada_em": datetime.fromisoformat(f.capturadaEm),
            "uploaded": True,
        }
        for i, f in enumerate(body.fotos)
    ]

    ev = repo_ev.create(db, ev_data, fotos_data)
    return _to_out(ev)


@router.get("/evidencias", response_model=list[EvidenciaOut])
def list_evidencias(
    areaId: str | None = None,
    since: str | None = None,
    u=Depends(require_permissao("EVIDENCE_CREATE")),
    db: Session = Depends(get_db),
):
    if not areaId:
        raise HTTPException(400, "Parâmetro 'areaId' obrigatório.")
    dt = datetime.fromisoformat(since) if since else None
    evs = repo_ev.get_by_area(db, areaId, since=dt)
    return [_to_out(e) for e in evs]
