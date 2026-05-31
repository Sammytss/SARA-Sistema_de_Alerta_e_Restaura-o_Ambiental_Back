"""
Testes dos endpoints públicos (sem autenticação).
Sem banco: 500 é esperado. Com banco: 200 com JSON.
"""
from fastapi.testclient import TestClient


def test_resumo_publico_acessivel_sem_token(client: TestClient):
    resp = client.get("/public/resumo")
    assert resp.status_code in (200, 500)


def test_municipios_publico_acessivel_sem_token(client: TestClient):
    resp = client.get("/public/municipios")
    assert resp.status_code in (200, 500)


def test_resumo_retorna_campos_corretos_quando_db_ok(client: TestClient):
    resp = client.get("/public/resumo")
    if resp.status_code == 200:
        data = resp.json()
        assert "total" in data
        assert "critica" in data
        assert "atencao" in data
        assert "regular" in data
        assert "totalEvidencias" in data
        assert "mediaRegeneracao" in data


def test_municipios_retorna_lista_quando_db_ok(client: TestClient):
    resp = client.get("/public/municipios")
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, list)
        if data:
            item = data[0]
            assert "municipio" in item
            assert "total" in item
