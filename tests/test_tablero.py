"""Tests del tablero: que la app corra y que las cifras visibles sean las del modelo.

Se ejecuta la app real con `AppTest` (una sola vez por módulo: carga el hecho completo). El detalle
de cada verificación queda en `docs/evidencia/render-tablero.md` vía `scripts/verificar-render.py`.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
APP = RAIZ / "src" / "tablero" / "app.py"
SALIDA = RAIZ / "outputs"


@pytest.fixture(scope="module")
def app() -> AppTest:
    if not (SALIDA / "proyectos.parquet").exists():
        pytest.skip("falta outputs/ · correr py -3.11 scripts/construir-modelo.py")
    return AppTest.from_file(str(APP), default_timeout=300).run()


def _todo(app: AppTest) -> str:
    partes = []
    for atributo in ("title", "subheader", "markdown", "caption", "info", "warning", "error"):
        for elemento in getattr(app, atributo, []):
            valor = getattr(elemento, "value", None)
            if valor:
                partes.append(str(valor))
    for elemento in app.dataframe:
        try:
            partes.append(" ".join(str(c) for c in elemento.value.columns))
        except AttributeError:
            pass
    return "\n".join(partes)


def test_la_app_corre_sin_excepcion(app: AppTest):
    assert not app.exception, str(app.exception)


def test_las_cinco_vistas_estan_montadas(app: AppTest):
    etiquetas = " · ".join(getattr(b, "label", "") for b in app.tabs)
    for vista in (
        "Panorama territorial",
        "Ranking institucional",
        "Serie temporal",
        "Ficha de institución",
        "Red y embudo",
    ):
        assert vista in etiquetas, f"falta la pestaña {vista}"


def test_toda_tarjeta_declara_su_unidad_y_moneda(app: AppTest):
    contenido = _todo(app)
    for marca in ("Unidad de conteo", "Moneda", "pesos del año base", "Corte", "IPC"):
        assert marca in contenido, f"falta el aviso obligatorio: {marca}"


def test_2026_entra_apagado_y_avisado(app: AppTest):
    casillas = [c for c in app.checkbox if "2026" in (c.label or "")]
    assert len(casillas) == 1, "debe existir una sola casilla para el año en curso"
    assert casillas[0].value is False, "el año en curso no puede venir encendido"
    assert "fuera de los totales" in _todo(app), "el pie debe avisar que el año en curso queda fuera"


def test_las_cifras_del_hecho_aparecen_en_la_app(app: AppTest):
    contenido = _todo(app)
    hecho = len(__import__("pandas").read_parquet(SALIDA / "proyectos.parquet"))
    numero = f"{hecho:,}".replace(",", ".")
    assert numero in contenido, f"las filas del hecho ({numero}) no aparecen en el tablero"
