"""H6 — Institución: el RUT manda, el nombre respalda, las colisiones se reportan."""

from __future__ import annotations

import pytest

from homologacion.institucion import (
    CONTROL_COLABORACION_NOMBRES,
    CONTROL_COLABORACION_NORMALIZADOS,
    CONTROL_COLABORACION_RUT,
    CONTROL_HISTORICO_NOMBRES,
    CONTROL_HISTORICO_NORMALIZADOS,
    CONTROL_NOMBRE_CON_VARIOS_RUT,
    CONTROL_RUT_CON_VARIOS_NOMBRES,
    clave_institucion,
    normalizar_nombre,
    normalizar_rut,
    reporte_colisiones,
)


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("UNIVERSIDAD DE LA FRONTERA", "UNIVERSIDAD DE LA FRONTERA"),
        ("Universidad de La Frontera", "UNIVERSIDAD DE LA FRONTERA"),
        ("UNIVERSIDAD  DE   LA FRONTERA ", "UNIVERSIDAD DE LA FRONTERA"),
        ("UNIVERSIDAD DE CHILE.", "UNIVERSIDAD DE CHILE"),
        ("PONTIFICIA UNIVERSIDAD CATÓLICA DE CHILE", "PONTIFICIA UNIVERSIDAD CATOLICA DE CHILE"),
        # se conserva la razón social: no se quitan palabras
        ("UNIVERSIDAD DE CONCEPCIÓN", "UNIVERSIDAD DE CONCEPCION"),
    ],
)
def test_normalizar_nombre(crudo: str, esperado: str) -> None:
    assert normalizar_nombre(crudo) == esperado


@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("76.086.428-5", "76086428-5"),
        ("76086428-5", "76086428-5"),
        ("760864285", "76086428-5"),  # sin guion: se acepta y se reescribe con guion
        ("76.086.428-K", "76086428-K"),
        ("SIN INFORMACION", None),
        ("-", None),
        ("", None),
        (None, None),
    ],
)
def test_normalizar_rut(crudo, esperado) -> None:
    assert normalizar_rut(crudo) == esperado


def test_clave_institucion_prefiere_rut() -> None:
    assert clave_institucion("UNIVERSIDAD DE LA FRONTERA", "76.086.428-5") == "RUT:76086428-5"
    assert clave_institucion("Universidad  de la Frontera", None) == "NOMBRE:UNIVERSIDAD DE LA FRONTERA"
    # mismo RUT, dos grafías → misma clave
    assert clave_institucion("U. DE LA FRONTERA", "76086428-5") == clave_institucion(
        "UNIVERSIDAD DE LA FRONTERA", "76086428-5"
    )
    # sin RUT, dos grafías distintas NO se fusionan solas
    assert clave_institucion("U. DE LA FRONTERA") != clave_institucion("UNIVERSIDAD DE LA FRONTERA")


def test_conteos_en_el_historico(historico) -> None:
    """El histórico no trae RUT: solo se pueden normalizar 16 grupos."""
    col = historico["INSTITUCION_PRINCIPAL"]
    assert col.nunique() == CONTROL_HISTORICO_NOMBRES
    assert col.map(normalizar_nombre).nunique() == CONTROL_HISTORICO_NORMALIZADOS


def test_conteos_en_colaboracion(colaboracion) -> None:
    nombres = colaboracion["INSTITUCION1ERNIVEL"]
    assert nombres.nunique() == CONTROL_COLABORACION_NOMBRES
    assert nombres.map(normalizar_nombre).nunique() == CONTROL_COLABORACION_NORMALIZADOS
    assert colaboracion["RUTINSTITUCION"].map(normalizar_rut).nunique() == CONTROL_COLABORACION_RUT


def test_colisiones_se_reportan(colaboracion) -> None:
    """Se cuentan sobre RUT válidos: es la única forma de que la cifra signifique algo."""
    col = reporte_colisiones(colaboracion, "INSTITUCION1ERNIVEL", "RUTINSTITUCION")
    assert len(col["rut_con_varios_nombres"]) == CONTROL_RUT_CON_VARIOS_NOMBRES
    assert len(col["nombre_con_varios_rut"]) == CONTROL_NOMBRE_CON_VARIOS_RUT
    # el reporte trae el detalle para decidir, no solo el número
    assert set(col["rut_con_varios_nombres"].columns) >= {"_rut", "nombres", "n_nombres"}
    assert col["rut_con_varios_nombres"]["n_nombres"].iloc[0] >= 2
