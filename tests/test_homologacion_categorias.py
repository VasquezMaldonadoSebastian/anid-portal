"""H4 y H5 — Subdirección, tipo de beneficiario y sexo."""

from __future__ import annotations

import pytest

from homologacion.categorias import (
    HOMBRE,
    MUJER,
    TIPO_JURIDICA,
    TIPO_MIXTA,
    TIPO_NATURAL,
    homologar_sexo,
    homologar_tipo_beneficiario,
)
from homologacion.subdireccion import NO_APLICA, homologar_subdireccion


# --- H4 subdirección ---
@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("Proyectos de Investigación", "PROYECTOS DE INVESTIGACION"),
        ("Capital Humano", "CAPITAL HUMANO"),
        ("Centros e Investigación Asociativa", "CENTROS E INVESTIGACION ASOCIATIVA"),
        ("Investigación Aplicada", "INVESTIGACION APLICADA"),
        ("Redes Estrategia y Conocimiento", "REDES ESTRATEGIA Y CONOCIMIENTO"),
        # la misma área con y sin coma: dos rótulos, un destino
        ("Redes, Estrategia y Conocimiento", "REDES ESTRATEGIA Y CONOCIMIENTO"),
        ("REDES ESTRATEGIA Y CONOCIMIENTO", "REDES ESTRATEGIA Y CONOCIMIENTO"),
        # no es una subdirección: es el pasado pre-2010
        ("NO APLICA", NO_APLICA),
        ("SIN INFORMACION", "NO CLASIFICADO"),
    ],
)
def test_subdireccion(crudo: str, esperado: str) -> None:
    assert homologar_subdireccion(crudo) == esperado


def test_subdireccion_no_pierde_filas(historico) -> None:
    sd = historico["SUBDIRECCION"].map(homologar_subdireccion)
    assert historico["SUBDIRECCION"].nunique() == 7
    assert int((sd == "NO CLASIFICADO").sum()) == 0
    assert sd.value_counts().to_dict() == {
        "PROYECTOS DE INVESTIGACION": 33_392,
        "REDES ESTRATEGIA Y CONOCIMIENTO": 5_951,
        "INVESTIGACION APLICADA": 5_667,
        NO_APLICA: 2_484,
        "CENTROS E INVESTIGACION ASOCIATIVA": 1_332,
        "CAPITAL HUMANO": 188,
    }
    assert int(sd.count()) == 49_014


# --- H5 tipo de beneficiario ---
@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("PERSONA NATURAL", TIPO_NATURAL),
        ("PERSONA JURIDICA", TIPO_JURIDICA),
        ("Persona Natural", TIPO_NATURAL),
        ("PERSONA NATURAL O PERSONA JURIDICA", TIPO_MIXTA),
        ("NATURAL O JURIDICA", TIPO_MIXTA),
        ("SIN INFORMACION", "SIN INFORMACION"),
        ("", "NO CLASIFICADO"),
    ],
)
def test_tipo_beneficiario(crudo: str, esperado: str) -> None:
    assert homologar_tipo_beneficiario(crudo) == esperado


def test_los_mixtos_no_se_reparten(historico) -> None:
    """61 filas declaran 'natural o jurídica': se cuentan como tales, no se adivina."""
    tb = historico["TIPO_BENEFICIARIO"].map(homologar_tipo_beneficiario)
    assert int((tb == TIPO_MIXTA).sum()) == 61
    assert tb.value_counts().to_dict() == {
        TIPO_NATURAL: 37_187,
        TIPO_JURIDICA: 11_565,
        "SIN INFORMACION": 201,
        TIPO_MIXTA: 61,
    }


# --- H5 sexo ---
@pytest.mark.parametrize(
    ("crudo", "esperado"),
    [
        ("HOMBRE", HOMBRE),
        ("Hombre", HOMBRE),
        ("MASCULINO", HOMBRE),
        ("MUJER", MUJER),
        ("FEMENINO", MUJER),
        ("SIN INFORMACION", "SIN INFORMACION"),
        ("", "NO CLASIFICADO"),
    ],
)
def test_sexo(crudo: str, esperado: str) -> None:
    assert homologar_sexo(crudo) == esperado


def test_sexo_en_becas(becas) -> None:
    """HOMBRE/MUJER y FEMENINO/MASCULINO conviven: 4 rótulos → 2."""
    assert becas["SEXO"].nunique() == 4
    sx = becas["SEXO"].map(homologar_sexo)
    assert sx.value_counts().to_dict() == {HOMBRE: 10_269, MUJER: 9_019}
    assert int(sx.count()) == 19_288
