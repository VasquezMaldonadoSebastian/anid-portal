"""H2 — Macrozona: la derivada de la región debe coincidir con la del archivo."""

from __future__ import annotations

import pytest

from homologacion.macrozona import (
    CONTROL_HISTORICO,
    macrozona_de_region,
    verificar_macrozona,
)
from homologacion.region import homologar_region

# El mapeo medido: dos diferencias con la agrupación que uno supondría
CASOS = [
    ("ARICA Y PARINACOTA", "NORTE"),
    ("ANTOFAGASTA", "NORTE"),
    ("ATACAMA", "NORTE"),
    ("TARAPACA", "NORTE"),
    ("COQUIMBO", "CENTRO"),  # NO va en Norte
    ("VALPARAISO", "CENTRO"),
    ("METROPOLITANA", "RM"),  # macrozona propia, no parte de Centro
    ("OHIGGINS", "CENTRO SUR"),  # NO va en Centro
    ("MAULE", "CENTRO SUR"),
    ("NUBLE", "CENTRO SUR"),
    ("BIOBIO", "CENTRO SUR"),
    ("ARAUCANIA", "SUR"),
    ("LOS RIOS", "SUR"),
    ("LOS LAGOS", "SUR"),
    ("AYSEN", "AUSTRAL"),
    ("MAGALLANES", "AUSTRAL"),
    ("SIN INFORMACION", "SIN INFORMACION"),
    ("EXTRANJERO", "EXTRANJERO"),
    ("MULTIREGIONAL", "MULTIREGIONAL"),
    ("NO APLICA", "NO APLICA"),
]


@pytest.mark.parametrize(("region", "macrozona"), CASOS)
def test_macrozona_de_region(region: str, macrozona: str) -> None:
    assert macrozona_de_region(region) == macrozona


def test_region_inventada_no_se_absorbe() -> None:
    assert macrozona_de_region("REGION DE LA NUEVA ARAUCANIA") == "NO CLASIFICADO"


def test_coincide_con_el_archivo_en_el_historico(historico) -> None:
    """49.014 filas: 0 excepciones. Es lo que valida el mapeo."""
    discrepancias = verificar_macrozona(historico)
    assert len(discrepancias) == 0, discrepancias.head(10).to_string()


def test_coincide_con_el_archivo_en_postulaciones(postulaciones) -> None:
    assert len(verificar_macrozona(postulaciones)) == 0


def test_becas_tiene_una_excepcion_declarada(becas) -> None:
    """ANID publica UNA fila de becas con región Metropolitana y macrozona CENTRO.

    La derivación dice RM; se conserva la derivación y la discrepancia queda
    documentada en vez de esconderse.
    """
    discrepancias = verificar_macrozona(becas, region="REGION_DE_ORIGEN")
    assert len(discrepancias) == 1
    fila = discrepancias.iloc[0]
    assert fila["region_homologada"] == "METROPOLITANA"
    assert fila["MACROZONA_MINCIENCIA"].strip().upper() == "CENTRO"
    assert fila["macrozona_derivada"] == "RM"


def test_sumas_por_macrozona_cuadran(historico) -> None:
    obtenido = (
        historico["REGION_EJECUCION"].map(homologar_region).map(macrozona_de_region).value_counts()
    )
    for macrozona, esperado in CONTROL_HISTORICO.items():
        assert int(obtenido.get(macrozona, 0)) == esperado, macrozona
    assert int(obtenido.sum()) == 49_014
