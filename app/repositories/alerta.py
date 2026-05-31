from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.alerta import Alerta


def get_all(
    db: Session,
    since: datetime | None = None,
    area_id: str | None = None,
) -> list[Alerta]:
    q = db.query(Alerta)
    if since:
        q = q.filter(Alerta.detectado_em > since)
    if area_id:
        q = q.filter(Alerta.area_id == area_id)
    return q.order_by(Alerta.detectado_em.desc()).all()


def get_by_id(db: Session, alerta_id: str) -> Alerta | None:
    return db.get(Alerta, alerta_id)


def create(db: Session, data: dict) -> Alerta:
    alerta = Alerta(**data)
    alerta.localizacao = f"SRID=4326;POINT({data['longitude']} {data['latitude']})"
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


def upsert_by_hash(db: Session, data: dict) -> Alerta | None:
    """Idempotente: retorna None se hash_dedupe já existe."""
    if data.get("hash_dedupe"):
        existing = (
            db.query(Alerta)
            .filter(Alerta.hash_dedupe == data["hash_dedupe"])
            .first()
        )
        if existing:
            return None
    return create(db, data)


def crossref_with_areas(db: Session, lat: float, lng: float, raio_metros: float = 5000) -> str | None:
    """Usa ST_DWithin para encontrar a área mais próxima dentro do raio (metros)."""
    result = db.execute(
        text("""
            SELECT id, ST_Distance(localizacao::geography, ST_GeomFromText(:ponto, 4326)) AS dist
            FROM areas
            WHERE localizacao IS NOT NULL
              AND ST_DWithin(localizacao::geography, ST_GeomFromText(:ponto, 4326), :raio)
            ORDER BY dist
            LIMIT 1
        """),
        {"ponto": f"POINT({lng} {lat})", "raio": raio_metros},
    ).first()
    return result.id if result else None
