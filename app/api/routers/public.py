from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories import area as repo_area

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/resumo")
def resumo_publico(db: Session = Depends(get_db)):
    """Totais agregados de áreas — sem autenticação."""
    return repo_area.get_resumo(db)


@router.get("/municipios")
def municipios_publico(db: Session = Depends(get_db)):
    """Breakdown por município — sem autenticação."""
    return repo_area.get_resumo_por_municipio(db)
