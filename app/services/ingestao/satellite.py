"""
Ingestão de imagens de satélite Sentinel-2 via Microsoft Planetary Computer.
API pública — sem chave de acesso necessária.
Documentação: https://planetarycomputer.microsoft.com/api/stac/v1
"""
import json
import logging
import uuid
from datetime import UTC, datetime

import httpx
from sqlalchemy.orm import Session

from app.models.area import Area
from app.models.satellite_frame import SatelliteFrame

logger = logging.getLogger(__name__)

_PC_STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
_PC_TILES = "https://planetarycomputer.microsoft.com/api/data/v1/item/tiles/WebMercatorQuad"

# Período seco no Cerrado/Tocantins — menor cobertura de nuvens
# Tuplas (mm-dd início, mm-dd fim) — ano inserido em gerar_timeline_area
_PERIODOS = [
    ("06-01", "09-30"),  # Seco: junho-setembro
    ("04-01", "10-31"),  # Transição
    ("01-01", "12-31"),  # Ano todo
]


def _bbox_da_area(area: Area, buffer_deg: float = 0.15) -> list[float]:
    return [
        area.centro_lng - buffer_deg,
        area.centro_lat - buffer_deg,
        area.centro_lng + buffer_deg,
        area.centro_lat + buffer_deg,
    ]


def _tile_url(item_id: str) -> str:
    return (
        f"{_PC_TILES}/{{z}}/{{x}}/{{y}}@1x"
        f"?collection=sentinel-2-l2a"
        f"&item={item_id}"
        f"&assets=visual"
        f"&rescale=0%2C2500"
    )


async def _buscar_melhor_cena(
    client: httpx.AsyncClient, bbox: list[float], year: int
) -> dict | None:
    """Retorna a cena Sentinel-2 com menor cobertura de nuvens para o ano/bbox."""
    for inicio, fim in _PERIODOS:
        datetime_range = f"{year}-{inicio}/{year}-{fim}"
        try:
            resp = await client.post(
                _PC_STAC,
                json={
                    "collections": ["sentinel-2-l2a"],
                    "bbox": bbox,
                    "datetime": datetime_range,
                    "limit": 10,
                },
                timeout=15,
            )
            if resp.status_code != 200:
                logger.debug("STAC %s: HTTP %d", datetime_range, resp.status_code)
                continue
            items = json.loads(resp.text).get("features", [])
            if not items:
                continue
            items.sort(key=lambda x: x["properties"].get("eo:cloud_cover", 999))
            best = items[0]
            if best["properties"].get("eo:cloud_cover", 100) < 60:
                return best
        except Exception as exc:
            logger.debug("STAC %s falhou: %s", datetime_range, exc)

    return None


async def gerar_timeline_area(
    db: Session, area: Area, anos: int = 5
) -> list[SatelliteFrame]:
    """Gera ou recupera do cache os frames Sentinel-2 dos últimos N anos."""
    ano_atual = datetime.now(UTC).year
    bbox = _bbox_da_area(area)
    frames: list[SatelliteFrame] = []

    async with httpx.AsyncClient() as client:
        for year in range(ano_atual - anos + 1, ano_atual + 1):
            # Tenta usar cache existente
            cached = (
                db.query(SatelliteFrame)
                .filter(
                    SatelliteFrame.area_id == area.id,
                    SatelliteFrame.ano == year,
                    SatelliteFrame.camada == "TRUE_COLOR",
                )
                .first()
            )
            if cached:
                frames.append(cached)
                continue

            cena = await _buscar_melhor_cena(client, bbox, year)
            if not cena:
                logger.warning(
                    "Nenhuma cena Sentinel-2 para área %s ano %d", area.id, year
                )
                continue

            item_id = cena["id"]
            cloud = round(cena["properties"].get("eo:cloud_cover", 0), 2)

            frame = SatelliteFrame(
                id=str(uuid.uuid4()),
                area_id=area.id,
                ano=year,
                camada="TRUE_COLOR",
                imagem_url=_tile_url(item_id),
                thumbnail_url=None,
                percentual_vegetacao=None,
                classes_json=None,
                fonte="SENTINEL2",
            )
            db.add(frame)
            frames.append(frame)
            logger.info(
                "Frame Sentinel-2 criado: área=%s ano=%d cena=%s nuvens=%.1f%%",
                area.id, year, item_id, cloud,
            )

    try:
        db.commit()
    except Exception as exc:
        logger.error("Erro ao salvar frames: %s", exc)
        db.rollback()

    return frames
