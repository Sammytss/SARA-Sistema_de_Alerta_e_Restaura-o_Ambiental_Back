from datetime import UTC, datetime

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.area import Area


def _wkt_point(lat: float, lng: float) -> str:
    return f"SRID=4326;POINT({lng} {lat})"


def get_all(db: Session, since: datetime | None = None) -> list[Area]:
    q = db.query(Area)
    if since:
        q = q.filter(Area.updated_at > since)
    return q.order_by(Area.nome).all()


def get_by_tecnico(
    db: Session, tecnico_id: str, since: datetime | None = None
) -> list[Area]:
    q = db.query(Area).filter(Area.tecnico_atribuido_id == tecnico_id)
    if since:
        q = q.filter(Area.updated_at > since)
    return q.order_by(Area.nome).all()


def get_by_produtor(
    db: Session, produtor_id: str, since: datetime | None = None
) -> list[Area]:
    q = db.query(Area).filter(Area.produtor_id == produtor_id)
    if since:
        q = q.filter(Area.updated_at > since)
    return q.order_by(Area.nome).all()


def get_by_id(db: Session, area_id: str) -> Area | None:
    return db.get(Area, area_id)


def create(db: Session, data: dict) -> Area:
    area = Area(**data)
    area.localizacao = _wkt_point(data["centro_lat"], data["centro_lng"])
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


def update(db: Session, area: Area, data: dict) -> Area:
    for k, v in data.items():
        setattr(area, k, v)
    if "centro_lat" in data or "centro_lng" in data:
        lat = data.get("centro_lat", area.centro_lat)
        lng = data.get("centro_lng", area.centro_lng)
        area.localizacao = _wkt_point(lat, lng)
    db.commit()
    db.refresh(area)
    return area


def get_resumo(db: Session) -> dict:
    row = db.query(
        func.count().label("total"),
        func.sum(case((Area.status == "CRITICA", 1), else_=0)).label("critica"),
        func.sum(case((Area.status == "ATENCAO", 1), else_=0)).label("atencao"),
        func.sum(case((Area.status == "REGULAR", 1), else_=0)).label("regular"),
        func.coalesce(func.sum(Area.total_evidencias), 0).label("total_evidencias"),
        func.avg(Area.percentual_regeneracao).label("media_regeneracao"),
    ).one()
    return {
        "total": row.total or 0,
        "critica": row.critica or 0,
        "atencao": row.atencao or 0,
        "regular": row.regular or 0,
        "totalEvidencias": int(row.total_evidencias or 0),
        "mediaRegeneracao": round(float(row.media_regeneracao or 0.0), 1),
        "geradoEm": datetime.now(UTC).isoformat(),
    }


def get_resumo_por_municipio(db: Session) -> list[dict]:
    rows = db.query(
        Area.municipio,
        func.count().label("total"),
        func.sum(case((Area.status == "CRITICA", 1), else_=0)).label("critica"),
        func.sum(case((Area.status == "ATENCAO", 1), else_=0)).label("atencao"),
        func.sum(case((Area.status == "REGULAR", 1), else_=0)).label("regular"),
        func.avg(Area.percentual_regeneracao).label("media_regeneracao"),
    ).group_by(Area.municipio).order_by(func.count().desc()).all()

    return [
        {
            "municipio": r.municipio,
            "total": r.total,
            "critica": r.critica or 0,
            "atencao": r.atencao or 0,
            "regular": r.regular or 0,
            "mediaRegeneracao": round(float(r.media_regeneracao or 0.0), 1),
        }
        for r in rows
    ]
