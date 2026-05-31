"""Fixtures globais de teste."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import criar_access_token, criar_refresh_token, hash_senha


@pytest.fixture(scope="module")
def client() -> TestClient:
    # raise_server_exceptions=False → erros de DB retornam 500 em vez de levantar exceção
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def gestor_token() -> str:
    return criar_access_token("u001")


@pytest.fixture(scope="module")
def tecnico_token() -> str:
    return criar_access_token("u002")


@pytest.fixture(scope="module")
def produtor_token() -> str:
    return criar_access_token("u003")


@pytest.fixture
def auth_gestor(gestor_token) -> dict:
    return {"Authorization": f"Bearer {gestor_token}"}


@pytest.fixture
def auth_tecnico(tecnico_token) -> dict:
    return {"Authorization": f"Bearer {tecnico_token}"}


@pytest.fixture
def auth_produtor(produtor_token) -> dict:
    return {"Authorization": f"Bearer {produtor_token}"}
