import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_usuario_or_401, require_perfil
from app.core.db import get_db
from app.core.rbac import has_permissao
from app.repositories import area as repo_area
from app.schemas.area import AreaCreate, AreaOut, AreaUpdate
from app.schemas.satellite import SatelliteFrameOut, SatelliteTimelineOut
from app.services.ingestao import satellite as satellite_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/areas", tags=["areas"])


def _to_out(a) -> AreaOut:
    return AreaOut(
        id=a.id,
        nome=a.nome,
        municipio=a.municipio,
        produtorId=a.produtor_id,
        tecnicoAtribuidoId=a.tecnico_atribuido_id,
        status=a.status,
        percentualRegeneracao=a.percentual_regeneracao,
        centroLat=a.centro_lat,
        centroLng=a.centro_lng,
        raioMetros=a.raio_metros,
        ultimaEvidencia=a.ultima_evidencia.isoformat() if a.ultima_evidencia else None,
        totalEvidencias=a.total_evidencias,
        updatedAt=a.updated_at.isoformat() if a.updated_at else datetime.utcnow().isoformat(),
    )


def _parse_since(since: str | None) -> datetime | None:
    if not since:
        return None
    try:
        return datetime.fromisoformat(since)
    except ValueError:
        raise HTTPException(400, "Parâmetro 'since' inválido. Use ISO8601.")


@router.get("", response_model=list[AreaOut])
def list_areas(
    since: str | None = None,
    u=Depends(get_usuario_or_401),
    db: Session = Depends(get_db),
):
    dt = _parse_since(since)
    if has_permissao(u.perfil, "AREA_VIEW_ALL"):
        areas = repo_area.get_all(db, since=dt)
    elif has_permissao(u.perfil, "AREA_VIEW_ASSIGNED"):
        areas = repo_area.get_by_tecnico(db, u.id, since=dt)
    elif has_permissao(u.perfil, "AREA_VIEW_OWN"):
        areas = repo_area.get_by_produtor(db, u.id, since=dt)
    else:
        raise HTTPException(403, "Sem permissão para listar áreas.")
    return [_to_out(a) for a in areas]


@router.get("/{area_id}", response_model=AreaOut)
def get_area(
    area_id: str,
    u=Depends(get_usuario_or_401),
    db: Session = Depends(get_db),
):
    area = repo_area.get_by_id(db, area_id)
    if area is None:
        raise HTTPException(404, "Área não encontrada.")

    if has_permissao(u.perfil, "AREA_VIEW_ALL"):
        pass
    elif has_permissao(u.perfil, "AREA_VIEW_ASSIGNED") and area.tecnico_atribuido_id != u.id:
        raise HTTPException(403, "Acesso negado a esta área.")
    elif has_permissao(u.perfil, "AREA_VIEW_OWN") and area.produtor_id != u.id:
        raise HTTPException(403, "Acesso negado a esta área.")

    return _to_out(area)


@router.post("", response_model=AreaOut, status_code=201)
def create_area(
    body: AreaCreate,
    u=Depends(require_perfil("GESTOR")),
    db: Session = Depends(get_db),
):
    data = {
        "nome": body.nome,
        "municipio": body.municipio,
        "produtor_id": body.produtorId,
        "tecnico_atribuido_id": body.tecnicoAtribuidoId,
        "status": body.status,
        "percentual_regeneracao": body.percentualRegeneracao,
        "centro_lat": body.centroLat,
        "centro_lng": body.centroLng,
        "raio_metros": body.raioMetros,
    }
    area = repo_area.create(db, data)
    return _to_out(area)


@router.get("/{area_id}/satellite-timeline", response_model=SatelliteTimelineOut)
async def get_satellite_timeline(
    area_id: str,
    anos: int = Query(default=5, ge=1, le=20),
    u=Depends(get_usuario_or_401),
    db: Session = Depends(get_db),
):
    """Retorna a linha do tempo de imagens de satélite Sentinel-2 (últimos N anos).

    Dados reais via Microsoft Planetary Computer (sem chave).
    Fallback automático para dados mock se o serviço estiver indisponível.
    """
    area = repo_area.get_by_id(db, area_id)
    if area is None:
        raise HTTPException(404, "Área não encontrada.")

    if not (
        has_permissao(u.perfil, "AREA_VIEW_ALL")
        or (has_permissao(u.perfil, "AREA_VIEW_ASSIGNED") and area.tecnico_atribuido_id == u.id)
        or (has_permissao(u.perfil, "AREA_VIEW_OWN") and area.produtor_id == u.id)
    ):
        raise HTTPException(403, "Acesso negado a esta área.")

    geometria_tipo = "polygon" if area.geometria else ("circle" if area.raio_metros else "point")

    # ── Dados reais: Sentinel-2 via Planetary Computer ────────────
    try:
        real_frames = await satellite_service.gerar_timeline_area(db, area, anos)
        if real_frames:
            return SatelliteTimelineOut(
                frames=[
                    SatelliteFrameOut(
                        id=f.id,
                        areaId=f.area_id,
                        ano=f.ano,
                        camada=f.camada,
                        imagemUrl=f.imagem_url or "",
                        tileUrl=f.imagem_url if f.imagem_url and "{z}" in f.imagem_url else None,
                        thumbnailUrl=f.thumbnail_url,
                        percentualVegetacao=f.percentual_vegetacao,
                        classes=None,
                        fonte=f.fonte,
                    )
                    for f in sorted(real_frames, key=lambda x: x.ano)
                ],
                geometria=geometria_tipo,
            )
    except Exception as exc:
        logger.warning("Satellite service indisponível (%s), usando mock.", exc)

    # ── Fallback: mock com progressão MapBiomas simulada ──────────
    ano_atual = datetime.utcnow().year
    anos_lista = list(range(ano_atual - anos + 1, ano_atual + 1))
    _classes = [
        {"Pastagem": 70.0, "Floresta": 15.0, "Agricultura": 10.0, "Outros": 5.0},
        {"Pastagem": 62.0, "Floresta": 22.0, "Agricultura": 10.0, "Outros": 6.0},
        {"Pastagem": 53.0, "Floresta": 30.0, "Agricultura": 10.0, "Outros": 7.0},
        {"Pastagem": 44.0, "Floresta": 40.0, "Agricultura": 9.0, "Outros": 7.0},
        {"Pastagem": 34.0, "Floresta": 52.0, "Agricultura": 8.0, "Outros": 6.0},
    ]
    frames_mock = [
        SatelliteFrameOut(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{area_id}-{ano}-LAND_COVER")),
            areaId=area_id,
            ano=ano,
            camada="LAND_COVER",
            imagemUrl="",
            tileUrl=None,
            thumbnailUrl=None,
            percentualVegetacao=round(cls.get("Floresta", 0.0), 1),
            classes=cls,
            fonte="MAPBIOMAS_MOCK",
        )
        for ano, cls in zip(anos_lista, _classes[-len(anos_lista):])
    ]
    return SatelliteTimelineOut(frames=frames_mock, geometria=geometria_tipo)


@router.patch("/{area_id}", response_model=AreaOut)
def update_area(
    area_id: str,
    body: AreaUpdate,
    u=Depends(require_perfil("GESTOR")),
    db: Session = Depends(get_db),
):
    area = repo_area.get_by_id(db, area_id)
    if area is None:
        raise HTTPException(404, "Área não encontrada.")

    updates: dict = {}
    if body.nome is not None:
        updates["nome"] = body.nome
    if body.status is not None:
        updates["status"] = body.status
    if body.percentualRegeneracao is not None:
        updates["percentual_regeneracao"] = body.percentualRegeneracao
    if body.tecnicoAtribuidoId is not None:
        updates["tecnico_atribuido_id"] = body.tecnicoAtribuidoId
    if body.centroLat is not None:
        updates["centro_lat"] = body.centroLat
    if body.centroLng is not None:
        updates["centro_lng"] = body.centroLng
    if body.raioMetros is not None:
        updates["raio_metros"] = body.raioMetros

    area = repo_area.update(db, area, updates)
    return _to_out(area)
