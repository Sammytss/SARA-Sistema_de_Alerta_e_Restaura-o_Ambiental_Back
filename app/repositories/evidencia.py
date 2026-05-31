from datetime import datetime

from sqlalchemy.orm import Session

from app.models.area import Area
from app.models.evidencia import Evidencia
from app.models.foto import Foto


def get_by_id(db: Session, ev_id: str) -> Evidencia | None:
    return db.get(Evidencia, ev_id)


def get_by_area(
    db: Session, area_id: str, since: datetime | None = None
) -> list[Evidencia]:
    q = db.query(Evidencia).filter(Evidencia.area_id == area_id)
    if since:
        q = q.filter(Evidencia.updated_at > since)
    return q.order_by(Evidencia.data_registro.desc()).all()


def create(db: Session, ev_data: dict, fotos_data: list[dict]) -> Evidencia:
    ev = Evidencia(**ev_data)
    ev.localizacao = f"SRID=4326;POINT({ev_data['longitude']} {ev_data['latitude']})"
    db.add(ev)

    for f in fotos_data:
        db.add(Foto(**f))

    area = db.get(Area, ev_data["area_id"])
    if area:
        area.total_evidencias = (area.total_evidencias or 0) + 1
        area.ultima_evidencia = ev_data.get("data_registro")

    db.commit()
    db.refresh(ev)
    return ev
