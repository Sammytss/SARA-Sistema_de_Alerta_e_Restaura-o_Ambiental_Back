"""
Teste de smoke para o healthcheck.
Executa sem banco de dados (DB retorna degraded, mas o endpoint responde 200).
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_has_status_field() -> None:
    data = client.get("/health").json()
    assert "status" in data
    assert data["status"] in ("ok", "degraded")


def test_health_has_version() -> None:
    data = client.get("/health").json()
    assert data["version"] == "1.0.0"
