from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # reconecta se a conexão cair
    pool_size=10,
    max_overflow=20,
    echo=settings.is_dev,  # loga SQL em dev
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os models ORM."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency FastAPI: entrega uma session e garante o fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Verifica se o banco responde (usado no healthcheck)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
