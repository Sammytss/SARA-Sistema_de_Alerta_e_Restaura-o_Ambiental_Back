"""
Matriz RBAC do backend SARA.
Espelha lib/features/access_control/permission_service.dart do app Flutter.
Manter em sincronia com o cliente.
"""

PERMISSOES_POR_PERFIL: dict[str, list[str]] = {
    "PUBLICO": [
        "AREA_VIEW_AGGREGATED",
    ],
    "GESTOR": [
        "AREA_VIEW_ALL",
        "SENSITIVE_DATA_VIEW",
        "AREA_ASSIGN",
    ],
    "TECNICO": [
        "AREA_VIEW_ASSIGNED",
        "SENSITIVE_DATA_VIEW",
        "EVIDENCE_CREATE",
        "SYNC_OFFLINE",
    ],
    "PRODUTOR": [
        "AREA_VIEW_OWN",
        "SENSITIVE_DATA_VIEW_OWN",
        "EVIDENCE_CREATE",
        "SYNC_OFFLINE",
    ],
    # Perfis pós-MVP (retornam permissões mínimas por ora)
    "ANALISTA": [
        "AREA_VIEW_ALL",
        "SENSITIVE_DATA_VIEW",
    ],
    "AUDITOR": [
        "AREA_VIEW_ALL",
        "SENSITIVE_DATA_VIEW",
    ],
    "OPERARIO": [
        "AREA_VIEW_ASSIGNED",
        "EVIDENCE_CREATE",
        "SYNC_OFFLINE",
    ],
}


def get_permissoes(perfil: str) -> list[str]:
    """Retorna a lista de permission codes para um perfil."""
    return PERMISSOES_POR_PERFIL.get(perfil.upper(), [])


def has_permissao(perfil: str, permissao: str) -> bool:
    return permissao in get_permissoes(perfil)
