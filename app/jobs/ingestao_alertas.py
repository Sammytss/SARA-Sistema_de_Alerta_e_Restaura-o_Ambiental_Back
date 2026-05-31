"""
Jobs de ingestão agendados — executados pelo APScheduler dentro do event loop asyncio.
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")


@scheduler.scheduled_job(
    IntervalTrigger(hours=1),
    id="ingestao_inpe",
    misfire_grace_time=300,
    max_instances=1,
)
async def job_ingestao_inpe() -> None:
    """Busca novos focos de queimada no INPE BDQueimadas a cada 1 hora."""
    from app.core.db import SessionLocal
    from app.services.ingestao.inpe import ingerir_focos_inpe

    db = SessionLocal()
    try:
        count = await ingerir_focos_inpe(db)
        logger.info("job_ingestao_inpe: %d alertas inseridos", count)
    except Exception as exc:
        logger.exception("job_ingestao_inpe falhou: %s", exc)
    finally:
        db.close()
