"""H1 — Región: cada etiqueta cruda cae en su región, sin perder filas."""

from __future__ import annotations

import pytest

from homologacion.region import NO_CLASIFICADO, homologar_region, no_clasificados

# (etiqueta cruda, región canónica) — los casos sucios que obligan a la regla
CASOS = [
    ("REGION DE METROPOLITANA", "METROPOLITANA"),
    ("REGION METROPOLITANA DE SANTIAGO", "METROPOLITANA"),  # etiqueta 2026
    ("REGION METROPOLITANA", "METROPOLITANA"),  # archivos Milenio
    ("REGION DE VALPARAISO", "VALPARAISO"),
    ("REGION DEL BIOBIO", "BIOBIO"),
    ("REGION DEL BIO-BIO", "BIOBIO"),  # así viene en Colaboración
    ("REGION DE ÑUBLE", "NUBLE"),
    ("REGION DEL NUBLE", "NUBLE"),
    ("REGION DE NUBLE", "NUBLE"),
    ("REGION DE LA ARAUCANIA", "ARAUCANIA"),
    ("REGION DE LOS RIOS", "LOS RIOS"),
    ("REGION DE OHIGGINS", "OHIGGINS"),
    ("REGION DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS", "OHIGGINS"),
    ("REGION DE MAGALLANES Y ANTARTICA CHILENA", "MAGALLANES"),
    ("REGION DE MAGALLANES Y DE LA ANTARTICA CHILENA", "MAGALLANES"),
    ("REGION DE AYSEN", "AYSEN"),
    ("REGION DE AYSEN DEL GENERAL CARLOS IBANEZ DEL CAMPO", "AYSEN"),
    ("REGION DE ARICA Y PARINACOTA", "ARICA Y PARINACOTA"),
    # no territoriales
    ("SIN INFORMACION", "SIN INFORMACION"),
    ("NO REGISTRA REGION", "SIN INFORMACION"),  # así viene en Colaboración
    ("EXTRANJERO", "EXTRANJERO"),
    ("MULTIREGIONAL", "MULTIREGIONAL"),
    ("NO APLICA", "NO APLICA"),
]


@pytest.mark.parametrize(("crudo", "esperado"), CASOS)
def test_etiqueta_cruda(crudo: str, esperado: str) -> None:
    assert homologar_region(crudo) == esperado


def test_etiqueta_desconocida_no_se_absorbe() -> None:
    """Un territorio nuevo (o mal escrito) NO se adivina: se marca y se reporta."""
    assert homologar_region("REGION DE LA NUEVA ARAUCANIA") == NO_CLASIFICADO
    assert homologar_region("") == NO_CLASIFICADO
    assert homologar_region("NO DEFINIDA") == NO_CLASIFICADO


def test_no_pierde_filas_en_el_historico(historico) -> None:
    assert len(historico) == 49_014
    region = historico["REGION_EJECUCION"].map(homologar_region)
    assert region.notna().all()
    assert no_clasificados(historico["REGION_EJECUCION"]) == {}


def test_region_metropolitana_cuadra_despues_de_homologar(historico) -> None:
    """Antes: 26.334 (una sola etiqueta). Después: 27.212 (las dos formas juntas)."""
    crudo = historico["REGION_EJECUCION"]
    assert int((crudo == "REGION DE METROPOLITANA").sum()) == 26_334
    assert int((crudo == "REGION METROPOLITANA DE SANTIAGO").sum()) == 878
    assert int((crudo.map(homologar_region) == "METROPOLITANA").sum()) == 27_212


def test_nuble_con_dos_grafias_en_el_historico(historico) -> None:
    """'REGION DE NUBLE' y 'REGION DEL NUBLE' suman 57.

    Ojo con el detalle que enseña el caso: buscar `"NUBLE"` en el texto crudo NO
    encuentra `REGION DE ÑUBLE` (esa grafía está en Becas y Postulaciones), así que
    todo filtro sobre texto crudo tiene que ser insensible a la tilde.
    """
    crudo = historico["REGION_EJECUCION"]
    assert sorted(crudo[crudo.str.contains("NUBLE|ÑUBLE", regex=True)].unique()) == [
        "REGION DE NUBLE",
        "REGION DEL NUBLE",
    ]
    assert int(crudo.str.contains("NUBLE", regex=False).sum()) == 57
    assert int((crudo.map(homologar_region) == "NUBLE").sum()) == 57
    assert homologar_region("REGION DE ÑUBLE") == "NUBLE"


def test_sin_clasificar_en_las_otras_tres_bases(becas, colaboracion, postulaciones) -> None:
    """La regla no puede servir sólo para el histórico."""
    assert no_clasificados(becas["REGION_DE_ORIGEN"]) == {}
    assert no_clasificados(colaboracion["REGIONINSTITUCION"]) == {}
    assert no_clasificados(postulaciones["REGION_EJECUCION"]) == {}
