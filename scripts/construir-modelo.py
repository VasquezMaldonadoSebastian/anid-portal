"""Construye el modelo curado y deja los agregados que consume el tablero.

Uso: py -3.11 scripts/construir-modelo.py

Equivale a `modelo.exportar.construir_todo()`, pero desde la línea de comandos y con
salida legible. Las tablas llegan a `outputs/` en CSV y Parquet (fuera de git).
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from modelo.exportar import construir_todo  # noqa: E402


def main() -> int:
    meta = construir_todo()
    print(f"Modelo construido · corte: {meta['corte']['fecha']}")
    print(f"Deflactores: {meta['deflactores']['fuente']} (base {meta['deflactores']['base']})")
    print(f"Tasa de adjudicación de proyectos: {meta['tasa_adjudicacion_proyectos']['tasa']}%")
    print()
    for nombre, n in meta["filas"].items():
        print(f"  {nombre:<20} {n:>9,} filas".replace(",", "."))
    print(f"\nSalida: {RAIZ / 'outputs'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
