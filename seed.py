"""
Popula o banco com usuários e áreas de teste (equivale aos mocks do app Flutter).
Uso: python seed.py
Pré-requisito: alembic upgrade head já executado.
"""
import os
import sys
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.core.db import SessionLocal
from app.core.security import hash_senha
from app.models import Area, Usuario  # garante que Base.metadata conhece as tabelas

SENHA_PADRAO = "123456"


def _seed_usuarios(db) -> None:
    usuarios = [
        {
            "id": "u001",
            "nome": "Carlos Gestor",
            "email": "gestor@sara.gov.br",
            "perfil": "GESTOR",
            "telefone": "(63) 99999-0001",
            "documento": "111.222.333-01",
            "orgao_instituicao": "NATURATINS",
        },
        {
            "id": "u002",
            "nome": "Maria Técnica",
            "email": "tecnico@sara.gov.br",
            "perfil": "TECNICO",
            "telefone": "(63) 99999-0002",
            "documento": "111.222.333-02",
            "orgao_instituicao": "NATURATINS",
        },
        {
            "id": "u003",
            "nome": "João Produtor",
            "email": "produtor@sara.gov.br",
            "perfil": "PRODUTOR",
            "telefone": "(63) 99999-0003",
            "documento": "111.222.333-03",
            "orgao_instituicao": "Fazenda Boa Vista",
        },
        # Usuários extras referenciados pelas áreas mock
        {"id": "u005", "nome": "Produtor Porto", "email": "porto@sara.gov.br", "perfil": "PRODUTOR"},
        {"id": "u006", "nome": "Produtor Gurupi", "email": "gurupi@sara.gov.br", "perfil": "PRODUTOR"},
        {"id": "u007", "nome": "Produtor Boa Esperança", "email": "boaesperanca@sara.gov.br", "perfil": "PRODUTOR"},
        {"id": "u008", "nome": "Técnico Sul", "email": "tecnico2@sara.gov.br", "perfil": "TECNICO"},
    ]
    for u in usuarios:
        if db.get(Usuario, u["id"]) is None:
            db.add(Usuario(**u, senha_hash=hash_senha(SENHA_PADRAO)))
            print(f"  + {u['perfil']:8s}  {u['email']}")
        else:
            print(f"  ~ {u['perfil']:8s}  {u['email']} (já existe)")


def _seed_areas(db) -> None:
    now = datetime.now(UTC)
    areas = [
        {
            "id": "a001",
            "nome": "Fazenda Santa Helena — Talhão 1",
            "municipio": "Palmas",
            "produtor_id": "u003",
            "tecnico_atribuido_id": "u002",
            "status": "ATENCAO",
            "percentual_regeneracao": 42.0,
            "centro_lat": -10.310,
            "centro_lng": -48.221,
            "total_evidencias": 3,
            "ultima_evidencia": datetime(2026, 5, 15, tzinfo=UTC),
            "updated_at": now,
        },
        {
            "id": "a002",
            "nome": "Fazenda Santa Helena — APP Rio",
            "municipio": "Palmas",
            "produtor_id": "u003",
            "tecnico_atribuido_id": "u002",
            "status": "CRITICA",
            "percentual_regeneracao": 18.5,
            "centro_lat": -10.318,
            "centro_lng": -48.228,
            "total_evidencias": 1,
            "ultima_evidencia": datetime(2026, 4, 28, tzinfo=UTC),
            "updated_at": now,
        },
        {
            "id": "a003",
            "nome": "Propriedade Beira Rio — RL Norte",
            "municipio": "Porto Nacional",
            "produtor_id": "u005",
            "tecnico_atribuido_id": "u002",
            "status": "REGULAR",
            "percentual_regeneracao": 78.3,
            "centro_lat": -10.701,
            "centro_lng": -48.415,
            "raio_metros": 800,
            "total_evidencias": 7,
            "ultima_evidencia": datetime(2026, 5, 20, tzinfo=UTC),
            "updated_at": now,
        },
        {
            "id": "a004",
            "nome": "Sítio Cerrado Vivo — Talhão A",
            "municipio": "Gurupi",
            "produtor_id": "u006",
            "tecnico_atribuido_id": "u002",
            "status": "ATENCAO",
            "percentual_regeneracao": 55.1,
            "centro_lat": -11.729,
            "centro_lng": -49.069,
            "total_evidencias": 0,
            "updated_at": now,
        },
        {
            "id": "a005",
            "nome": "Fazenda Boa Esperança — RL Sul",
            "municipio": "Araguaína",
            "produtor_id": "u007",
            "tecnico_atribuido_id": "u008",
            "status": "REGULAR",
            "percentual_regeneracao": 91.0,
            "centro_lat": -7.188,
            "centro_lng": -48.201,
            "raio_metros": 1200,
            "total_evidencias": 12,
            "ultima_evidencia": datetime(2026, 5, 25, tzinfo=UTC),
            "updated_at": now,
        },
        {
            "id": "a006",
            "nome": "Reflorestamento Municipal — Setor 3",
            "municipio": "Palmas",
            "produtor_id": None,
            "tecnico_atribuido_id": "u008",
            "status": "ATENCAO",
            "percentual_regeneracao": 34.7,
            "centro_lat": -10.245,
            "centro_lng": -48.300,
            "total_evidencias": 4,
            "ultima_evidencia": datetime(2026, 5, 10, tzinfo=UTC),
            "updated_at": now,
        },
    ]
    for a in areas:
        if db.get(Area, a["id"]) is None:
            area = Area(**a)
            area.localizacao = f"SRID=4326;POINT({a['centro_lng']} {a['centro_lat']})"
            db.add(area)
            print(f"  + {a['municipio']:15s}  {a['nome']}")
        else:
            print(f"  ~ {a['municipio']:15s}  {a['nome']} (já existe)")


def main() -> None:
    db = SessionLocal()
    try:
        print("\n=== Usuários ===")
        _seed_usuarios(db)
        print("\n=== Áreas ===")
        _seed_areas(db)
        db.commit()
        print("\nSeed concluído com sucesso!")
    except Exception as exc:
        db.rollback()
        print(f"\nErro no seed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
