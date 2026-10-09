"""Test de humo del proyecto (reemplaza el assert True del scaffold).

Verifica que el entorno de trabajo es el correcto: el `python` del PATH no sirve para el proyecto
no trae pandas, este proyecto se corre con `py -3.11`.
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def test_estructura_del_proyecto() -> None:
    for relativo in ("README.md", "AGENTS.md", "MEMORIA.md", "docs/datos.md", "docs/homologacion.md"):
        assert (RAIZ / relativo).exists(), f"falta {relativo}"


def test_pandas_disponible() -> None:
    import pandas  # noqa: PLC0415

    assert pandas.__version__.startswith("2.")
