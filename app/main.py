from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.db import check_db_connection
from app.jobs.ingestao_alertas import scheduler
from app.api.routers import auth, areas, alertas, evidencias, public

# ── Rate limiter global ────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ── Lifespan: scheduler start/stop ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


# ── App ───────────────────────────────────────────────────────────
app = FastAPI(
    title="SARA Backend",
    description="Sistema de Acompanhamento da Restauração Ambiental — API REST",
    version="1.0.0",
    docs_url="/docs" if settings.is_dev else None,
    redoc_url="/redoc" if settings.is_dev else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (fotos enviadas pelo app) ────────────────────────
app.mount("/storage", StaticFiles(directory=settings.upload_dir_path), name="storage")

# ── Routers ───────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(areas.router)
app.include_router(alertas.router)
app.include_router(evidencias.router)
app.include_router(public.router)


# ── Healthcheck ───────────────────────────────────────────────────
@app.get("/health", tags=["infra"])
def health() -> dict:
    """Endpoint de healthcheck — usado por load balancer e docker-compose."""
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "ok" if db_ok else "error",
        "version": app.version,
        "env": settings.env,
    }
