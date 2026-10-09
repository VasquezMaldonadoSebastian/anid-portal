"""Construye config/deflactores.csv: el IPC anual de Chile para llevar montos a pesos constantes.

Fuente: Banco Mundial, indicador `FP.CPI.TOTL` (índice de precios al consumidor, base 2010=100),
serie anual del país CHL. Se consulta una vez y se **versiona** el resultado, para que el tablero
no dependa de la red ni de que el Banco Mundial cambie la serie por debajo.

Uso: py -3.11 scripts/deflactores.py

Base del tablero: **2025** (último año cerrado con índice). `monto_clp_real` = monto_clp × IPC_2025 / IPC_año.
2026 queda sin factor porque el índice anual no existe todavía: el modelo lo marca, no lo estima.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "config" / "deflactores.csv"
URL = "https://api.worldbank.org/v2/country/CHL/indicator/FP.CPI.TOTL?format=json&per_page=100&date=1980:2026"
CHILE = timezone(timedelta(hours=-3))
BASE = 2025


def main() -> int:
    print(f"Consultando {URL}")
    try:
        with urllib.request.urlopen(URL, timeout=60) as r:  # noqa: S310 - URL fija del Banco Mundial
            datos = json.loads(r.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR al consultar el Banco Mundial: {exc}", file=sys.stderr)
        if DESTINO.exists():
            print(f"Se conserva el archivo existente: {DESTINO}", file=sys.stderr)
            return 0
        return 1

    consultado = datetime.now(CHILE)
    serie = {int(f["date"]): float(f["value"]) for f in datos[1] if f["value"] is not None}
    if BASE not in serie:
        print(f"ERROR: el año base {BASE} no viene en la serie", file=sys.stderr)
        return 1

    anios = sorted(serie)
    lineas = [
        "anio;ipc;base;fuente;url;fecha_consulta;provisional",
    ]
    for anio in anios:
        lineas.append(
            f"{anio};{serie[anio]};2010;Banco Mundial FP.CPI.TOTL (CHL);"
            f"{URL.split('?')[0]};{consultado:%Y-%m-%d};no"
        )

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(
        f"Escrito {DESTINO}: {len(serie)} años ({anios[0]}–{anios[-1]}) · base {BASE} · "
        f"IPC {BASE} = {serie[BASE]:.4f} · consultado {consultado:%Y-%m-%d}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
