"""H3 — Moneda: los cuatro rótulos, los euros y el monto que no está."""

from __future__ import annotations

import pytest

from homologacion.macrozona import macrozona_de_region
from homologacion.moneda import (
    CONTROL_EN_EUROS,
    CONTROL_FILAS_PESOS,
    CONTROL_FILAS_SIN_ROTULO,
    CONTROL_NACIONAL_2020_2025_CLP,
    CONTROL_PERIODO_2020_2025_FILAS,
    CONTROL_RM_2020_2025_CLP,
    CONTROL_RM_2020_2025_FILAS,
    CONTROL_SIN_MONTO,
    a_euros,
    a_pesos,
    es_pesos,
    normalizar_montos,
    rotulo_moneda,
)
from homologacion.region import homologar_region


@pytest.mark.parametrize(
    ("rotulo", "esperado"),
    [
        ("Miles de pesos (M$)", "MILES DE PESOS"),
        ("MILES DE PESOS (M$)", "MILES DE PESOS"),
        ("Miles de pesos ", "MILES DE PESOS"),
        ("M$", "MILES DE PESOS"),  # rótulo nuevo (2024), es la misma unidad
        ("m$", "MILES DE PESOS"),
        ("EUROS", "EUROS"),
        ("Euros", "EUROS"),
        ("", "SIN MONEDA"),
        ("SIN INFORMACION", "SIN MONEDA"),
    ],
)
def test_rotulo(rotulo: str, esperado: str) -> None:
    assert rotulo_moneda(rotulo) == esperado


def test_es_pesos() -> None:
    assert es_pesos("Miles de pesos (M$)")
    assert not es_pesos("EUROS")


def test_a_pesos_convierte_miles() -> None:
    """`58.191` miles de pesos son $58.191.000 — el error de mil veces es el riesgo real."""
    assert a_pesos("58.191", "Miles de pesos (M$)") == 58_191_000.0
    assert a_pesos("227.497,14", "M$") == 227_497_140.0


def test_a_pesos_no_inventa_valor() -> None:
    assert a_pesos("", "Miles de pesos (M$)") is None
    assert a_pesos("nan", "Miles de pesos (M$)") is None
    assert a_pesos("NO SOLICITA A CONICYT", "Miles de pesos (M$)") is None
    assert a_pesos("100", "EUROS") is None  # un euro no es un peso


def test_euros_van_aparte() -> None:
    assert a_euros("1.234", "EUROS") == 1_234.0
    assert a_euros("1.234", "Miles de pesos (M$)") is None


def test_rotulos_en_el_archivo(historico) -> None:
    conteo = historico["MONEDA"].map(rotulo_moneda).value_counts().to_dict()
    assert conteo.get("MILES DE PESOS") == CONTROL_FILAS_PESOS
    assert conteo.get("SIN MONEDA") == CONTROL_FILAS_SIN_ROTULO
    assert conteo.get("EUROS") == CONTROL_EN_EUROS
    assert sum(conteo.values()) == 49_014


def test_filas_sin_monto(historico) -> None:
    """2.425 filas sin monto en pesos: no se imputan, se marcan."""
    hm = normalizar_montos(historico)
    sin_monto = int((hm["moneda_homologada"] == "MILES DE PESOS").sum() - hm["monto_clp"].notna().sum())
    assert sin_monto == CONTROL_SIN_MONTO - CONTROL_FILAS_SIN_ROTULO
    assert hm["monto_valido"].sum() == 46_551


def test_monto_metropolitano_2020_2025(historico) -> None:
    """RM: $1.160.514 millones en 6.093 filas (la cifra cambió al clasificar 'M$' como pesos)."""
    hm = normalizar_montos(historico)
    hm["anno"] = hm["AGNO_FALLO"].astype(int)
    rm = hm[
        (hm["anno"].between(2020, 2025))
        & hm["monto_valido"]
        & (hm["REGION_EJECUCION"].map(homologar_region) == "METROPOLITANA")
    ]
    assert len(rm) == CONTROL_RM_2020_2025_FILAS
    assert abs(rm["monto_clp"].sum() - CONTROL_RM_2020_2025_CLP) < 1_000_000


def test_monto_nacional_2020_2025(historico) -> None:
    """País: 11.395 filas de 11.782 del período tienen monto utilizable."""
    hm = normalizar_montos(historico)
    hm["anno"] = hm["AGNO_FALLO"].astype(int)
    periodo = hm[hm["anno"].between(2020, 2025) & hm["monto_valido"]]
    assert len(periodo) == CONTROL_PERIODO_2020_2025_FILAS
    assert abs(periodo["monto_clp"].sum() - CONTROL_NACIONAL_2020_2025_CLP) < 1_000_000


def test_macrozona_con_mayor_monto(historico) -> None:
    """RM concentra cerca de dos tercios del monto del período."""
    hm = normalizar_montos(historico)
    hm["anno"] = hm["AGNO_FALLO"].astype(int)
    periodo = hm[hm["anno"].between(2020, 2025) & hm["monto_valido"]].copy()
    periodo["mz"] = periodo["REGION_EJECUCION"].map(homologar_region).map(macrozona_de_region)
    por_mz = periodo.groupby("mz")["monto_clp"].sum().sort_values(ascending=False)
    assert por_mz.index[0] == "RM"
    assert 0.5 < por_mz.iloc[0] / por_mz.sum() < 0.6
