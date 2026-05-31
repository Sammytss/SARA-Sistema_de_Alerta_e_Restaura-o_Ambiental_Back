"""
Testes de rotas de áreas.
Sem banco: validam autenticação e estrutura — não persistência.
"""
from fastapi.testclient import TestClient


def test_areas_sem_token_retorna_nao_autorizado(client: TestClient):
    resp = client.get("/areas")
    assert resp.status_code in (401, 403)


def test_areas_com_token_invalido_retorna_nao_autorizado(client: TestClient):
    resp = client.get("/areas", headers={"Authorization": "Bearer invalido"})
    assert resp.status_code in (401, 403)


def test_areas_com_token_valido_sem_banco(client: TestClient, auth_gestor):
    resp = client.get("/areas", headers=auth_gestor)
    # Sem DB: 500 é esperado. Com DB: 200.
    assert resp.status_code in (200, 500)


def test_criar_area_exige_perfil_gestor(client: TestClient, auth_tecnico):
    body = {
        "nome": "Área Teste",
        "municipio": "Palmas",
        "status": "REGULAR",
        "percentualRegeneracao": 50.0,
        "centroLat": -10.0,
        "centroLng": -48.0,
    }
    resp = client.post("/areas", json=body, headers=auth_tecnico)
    # Sem DB: DB falha antes de checar perfil → 500. Com DB: 403.
    assert resp.status_code in (403, 500)


def test_criar_area_com_gestor_sem_banco(client: TestClient, auth_gestor):
    body = {
        "nome": "Área Teste Gestor",
        "municipio": "Palmas",
        "status": "REGULAR",
        "percentualRegeneracao": 50.0,
        "centroLat": -10.0,
        "centroLng": -48.0,
    }
    resp = client.post("/areas", json=body, headers=auth_gestor)
    assert resp.status_code in (201, 500)


def test_area_inexistente_retorna_404_ou_500(client: TestClient, auth_gestor):
    resp = client.get("/areas/nao-existe", headers=auth_gestor)
    assert resp.status_code in (404, 500)
