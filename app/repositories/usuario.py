from sqlalchemy.orm import Session

from app.models.usuario import Usuario


def get_by_email(db: Session, email: str) -> Usuario | None:
    return (
        db.query(Usuario)
        .filter(Usuario.email == email.lower().strip())
        .first()
    )


def get_by_id(db: Session, user_id: str) -> Usuario | None:
    return db.get(Usuario, user_id)
