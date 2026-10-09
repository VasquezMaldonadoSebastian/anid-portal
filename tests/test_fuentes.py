"""Test de humo de las fuentes: cada base carga y trae las filas medidas el 2026-10-09.

Si el proximo corte cambia un conteo, este test lo dice en un comando en vez de
obligar a releer docs/datos.md.

Las cifras esperadas vienen de docs/datos.md (perfilado medido, no de los README).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
CRUDO = RAIZ / "data" / "crudo"

# (repo, archivo, filas esperadas)
FUENTES = [
    ("Historico-de-Proyectos-Adjudicados", "BDH_HISTORICA.csv", 49_014),
    ("Historico-de-Proyectos-Adjudicados", "BDH_PROYECTOS_MILENIO.csv", 136),
    ("Colaboracion_Institucional", "CONSOLIDADO_INSTITUCIONES.csv", 33_731),
    ("Colaboracion_Institucional", "SPI_INVESTIGADORES.csv", 20_620),
    ("Postulaciones", "POSTULACIONES_2016_2025.csv", 139_517),
    ("Postulaciones", "POSTULACIONES_MILENIO.csv", 1_205),
    ("Becas", "BDH_BECAS SCH.csv", 19_288),
    ("Palabras_claves", "BD_Palabras_claves_Proyectos.csv", 12_873),
    ("Palabras_claves", "BD_Palabras_claves_Becas.csv", 17_245),
]

TOTAL_ESPERADO = 293_629


def cargar(repo: str, archivo: str) -> pd.DataFrame:
    ruta = CRUDO / repo / archivo
    if not ruta.exists():
        pytest.skip(f"falta {ruta} — corre scripts/refrescar-corte.sh")
    return pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)


@pytest.mark.parametrize(("repo", "archivo", "esperadas"), FUENTES)
def test_filas_por_fuente(repo: str, archivo: str, esperadas: int) -> None:
    df = cargar(repo, archivo)
    assert len(df) == esperadas, f"{archivo}: {len(df)} filas, se esperaban {esperadas}"


def test_total_de_filas() -> None:
    total = 0
    for repo, archivo, _ in FUENTES:
        ruta = CRUDO / repo / archivo
        if not ruta.exists():
            pytest.skip(f"falta {ruta}")
        total += len(cargar(repo, archivo))
    assert total == TOTAL_ESPERADO


def test_delimitador_y_bom() -> None:
    """El CSV es ';'-delimitado con BOM: leerlo por defecto debe fallar o traer 1 columna."""
    df = cargar("Historico-de-Proyectos-Adjudicados", "BDH_HISTORICA.csv")
    assert df.shape[1] == 23
    assert list(df.columns)[0] == "N"  # sin el BOM residual (\ufeffN)


def test_la_region_cruda_sigue_teniendo_mas_etiquetas_que_regiones() -> None:
    """Control de la regla R2: si alguien 'limpia' el crudo, esto avisa."""
    df = cargar("Historico-de-Proyectos-Adjudicados", "BDH_HISTORICA.csv")
    assert df["REGION_EJECUCION"].nunique() == 24
    assert (df["REGION_EJECUCION"] == "REGION METROPOLITANA DE SANTIAGO").sum() == 878
