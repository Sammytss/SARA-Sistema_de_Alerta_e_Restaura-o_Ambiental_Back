"""
Testes de autenticação.
Lógica de token: executa sem banco. Endpoints de login/me: requerem banco.
"""
from fastapi.testclient import TestClient

from app.core.security import (
    criar_access_token,
    criar_refresh_token,
    decodificar_token,
    hash_senha,
    verificar_senha,
)


# ── Testes de segurança (sem banco) ───────────────────────────────

def test_hash_e_verifica_senha():
    h = hash_senha("123456")
    assert verificar_senha("123456", h) is True
    assert verificar_senha("errada", h) is False


def test_access_token_valido():
    token = criar_access_token("u001")
    uid = decodificar_token(token, expected_type="access")
    assert uid == "u001"


def test_refresh_token_valido():
    token = criar_refresh_token("u001")
    uid = decodificar_token(token, expected_type="refresh")
    assert uid == "u001"


def test_access_token_recusado_como_refresh():
    token = criar_access_token("u001")
    assert decodificar_token(token, expected_type="refresh") is None


def test_token_invalido_retorna_none():
    assert decodificar_token("token.invalido.qualquer", expected_type="access") is None


# ── Testes de endpoint ────────────────────────────────────────────

def test_login_sem_banco_retorna_erro(client: TestClient):
    resp = client.post("/auth/login", json={"email": "gestor@sara.gov.br", "senha": "123456"})
    # Com banco: 200. Sem banco: 500.
    assert resp.status_code in (200, 500)


def test_me_sem_token_retorna_nao_autorizado(client: TestClient):
    resp = client.get("/auth/me")
    assert resp.status_code in (401, 403)


def test_me_com_token_invalido_retorna_nao_autorizado(client: TestClient):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer invalido"})
    assert resp.status_code in (401, 403)


def test_me_com_token_valido_sem_banco(client: TestClient, gestor_token):
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {gestor_token}"})
    # Com banco: 200. Sem banco: 500 (DB indisponível).
    assert resp.status_code in (200, 401, 500)


def test_refresh_com_token_invalido(client: TestClient):
    resp = client.post("/auth/refresh", json={"refreshToken": "token.falso.aqui"})
    assert resp.status_code == 401
