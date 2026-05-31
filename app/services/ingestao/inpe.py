"""
Ingestão de focos de queimada do INPE BDQueimadas.
Documentação: https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas
API pública — sem chave de acesso necessária.
"""
import hashlib
import logging
import uuid
from datetime import UTC, datetime, date

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories import alerta as repo_alerta

logger = logging.getLogger(__name__)

# Bounding box do Tocantins (graus decimais)
_TO_LAT_MIN = -13.5
_TO_LAT_MAX = -5.0
_TO_LNG_MIN = -50.5
_TO_LNG_MAX = -45.5


def _hash_foco(lat: float, lng: float, data_str: str) -> str:
    key = f"INPE|{lat:.4f}|{lng:.4f}|{data_str[:10]}"
    return hashlib.sha256(key.encode()).hexdigest()[:64]


def _parse_datetime(value: str) -> datetime:
    """Tenta vários formatos de data retornados pela API do INPE."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo=UTC)
        except ValueError:
            continue
    return datetime.now(UTC)


async def ingerir_focos_inpe(db: Session) -> int:
    """Busca focos do dia atual e persiste novos alertas. Retorna quantos foram inseridos."""
    hoje = date.today().isoformat()
    url = f"{settings.inpe_base_url}/api-focos/api/focos"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                url,
                params={
                    "data_utilizado": hoje,
                    "de_lat": str(_TO_LAT_MIN),
                    "de_lon": str(_TO_LNG_MIN),
                    "ate_lat": str(_TO_LAT_MAX),
                    "ate_lon": str(_TO_LNG_MAX),
                    "formato": "json",
                    "quantidade": "1000",
                },
            )
    except httpx.RequestError as exc:
        logger.warning("INPE indisponível: %s", exc)
        return 0

    if resp.status_code != 200:
        logger.warning("INPE retornou HTTP %d", resp.status_code)
        return 0

    try:
        payload = resp.json()
    except Exception:
        logger.warning("INPE retornou JSON inválido")
        return 0

    focos = payload if isinstance(payload, list) else payload.get("focos", [])
    count = 0

    for foco in focos:
        try:
            lat = float(foco.get("latitude", 0))
            lng = float(foco.get("longitude", 0))
            dt_raw = foco.get("data_hora_gmt") or foco.get("data_utc") or hoje
            detectado = _parse_datetime(str(dt_raw))
            hash_key = _hash_foco(lat, lng, str(dt_raw))

            area_id = repo_alerta.crossref_with_areas(db, lat, lng, raio_metros=5000)
            severidade = "CRITICA" if area_id else "ALTA"

            alerta_data = {
                "id": str(uuid.uuid4()),
                "fonte": "INPE",
                "tipo": "FOGO",
                "severidade": severidade,
                "latitude": lat,
                "longitude": lng,
                "area_id": area_id,
                "detectado_em": detectado,
                "hash_dedupe": hash_key,
            }

            if repo_alerta.upsert_by_hash(db, alerta_data):
                count += 1
        except Exception as exc:
            logger.debug("Foco inválido ignorado: %s — %s", foco, exc)
            continue

    logger.info("INPE: %d novos focos ingeridos em %s", count, hoje)
    return count
