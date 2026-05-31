from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Banco de dados ────────────────────────────────────────
    database_url: str = "postgresql://sara:sara@localhost:5432/sara_db"

    # ── JWT ───────────────────────────────────────────────────
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_alg: str = "HS256"
    access_ttl_min: int = 30       # minutos
    refresh_ttl_days: int = 30     # dias

    # ── CORS ──────────────────────────────────────────────────
    # Em prod: lista de origens separadas por vírgula.
    cors_origins: str = "*"

    # ── Upload de fotos ───────────────────────────────────────
    upload_dir: str = "storage"
    max_foto_mb: int = 10

    # ── APIs externas (Fase 6) ────────────────────────────────
    # Credenciais ficam APENAS no servidor, nunca no app.
    inpe_base_url: str = "https://terrabrasilis.dpi.inpe.br/queimadas/bdqueimadas"
    cigma_base_url: str = ""
    cigma_token: str = ""
    mapbiomas_alerta_url: str = "https://plataforma.alerta.mapbiomas.org/api"
    mapbiomas_email: str = ""
    mapbiomas_senha: str = ""

    # ── Ambiente ─────────────────────────────────────────────
    env: str = "dev"

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def upload_dir_path(self) -> str:
        import os
        os.makedirs(self.upload_dir, exist_ok=True)
        return self.upload_dir


settings = Settings()
