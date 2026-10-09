"""H7 y H8 — Rol institucional y unidad de conteo."""

from __future__ import annotations

import pytest

from homologacion.metricas import (
    CONTROL_HISTORICO_CODIGOS,
    CONTROL_HISTORICO_CODIGOS_REPETIDOS,
    CONTROL_HISTORICO_FILAS,
    codigos_repetidos,
    contar_codigos,
    contar_filas,
    contar_proyectos,
)
from homologacion.roles import (
    ASOCIADA,
    BENEFICIARIA,
    EXTRANJERA,
    NO_APLICA,
    PATROCINANTE,
    ROLES_CANONICOS,
    homologar_rol,
    no_clasificados,
)


# --- H7 roles ---
@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("INSTITUCION BENEFICIARIA", BENEFICIARIA),
        ("INSTITUCION PRINCIPAL", BENEFICIARIA),
        ("INSTITUCION RESPONSABLE/PUBLICA", BENEFICIARIA),
        ("INSTITUCION RESPONSABLE/PRIVADA", BENEFICIARIA),
        ("INSTITUCION PATROCINANTE", PATROCINANTE),
        ("INSTITUCION ASOCIADA", ASOCIADA),
        ("INSTITUCIONES CO-EJECUTORAS", ASOCIADA),
        # un rol con dos nombres: gana el más fuerte
        ("INSTITUCION NACIONAL PATROCINANTE ASOCIADA", PATROCINANTE),
        # extranjera manda, aunque diga principal
        ("INSTITUCION EXTRANJERA PRINCIPAL", EXTRANJERA),
        ("INSTITUCION EJECUTORA RESPONSABLE EN CHINA", EXTRANJERA),
        ("NO APLICA", NO_APLICA),
    ],
)
def test_rol(crudo: str, esperado: str) -> None:
    assert homologar_rol(crudo) == esperado


def test_rol_desconocido_no_se_absorbe() -> None:
    assert homologar_rol("ROL NUEVO DE UN CONCURSO 2027") == "NO CLASIFICADO"
    assert homologar_rol("") == "NO CLASIFICADO"


def test_roles_cubren_todas_las_filas(colaboracion) -> None:
    """65 valores crudos → 10 canónicos, 0 sin clasificar en 33.731 filas."""
    rl = colaboracion["ROLINSTITUCION"].map(homologar_rol)
    assert colaboracion["ROLINSTITUCION"].nunique() == 65
    assert no_clasificados(colaboracion["ROLINSTITUCION"]) == {}
    assert set(rl.unique()) <= set(ROLES_CANONICOS)
    assert rl.value_counts().to_dict() == {
        BENEFICIARIA: 13_968,
        ASOCIADA: 12_273,
        EXTRANJERA: 2_820,
        PATROCINANTE: 2_367,
        "APORTANTE / COFINANCIAMIENTO": 1_293,
        "POSTULANTE": 395,
        "ALBERGANTE / PROCEDENCIA": 362,
        "OTRA ENTIDAD": 233,
        NO_APLICA: 20,
    }
    assert int(rl.count()) == 33_731


# --- H8 unidad de conteo ---
def test_tres_formas_de_contar_el_historico(historico) -> None:
    """49.014 filas, 48.707 códigos y 48.835 pares (código, año): no es lo mismo."""
    assert contar_filas(historico) == CONTROL_HISTORICO_FILAS
    assert contar_codigos(historico) == CONTROL_HISTORICO_CODIGOS
    assert contar_proyectos(historico) == 48_835
    assert contar_codigos(historico) != contar_filas(historico)


def test_codigos_repetidos_traen_contenido_distinto(historico) -> None:
    """Los 136 códigos repetidos no son duplicados exactos: hay que mirarlos."""
    rep = codigos_repetidos(historico)
    assert len(rep) == CONTROL_HISTORICO_CODIGOS_REPETIDOS
    assert int(rep["contenido_distinto"].sum()) == CONTROL_HISTORICO_CODIGOS_REPETIDOS
    assert int(rep["filas"].sum()) > len(rep)  # 443 filas para 136 códigos


def test_postulaciones(historico, postulaciones) -> None:
    assert contar_filas(postulaciones) == 139_517
    assert contar_codigos(postulaciones) == 139_369
    # el código del proyecto es alfanumérico: leerlo como número lo destruiría
    assert historico["CODIGO_PROYECTO"].astype(str).str.len().max() > 6
