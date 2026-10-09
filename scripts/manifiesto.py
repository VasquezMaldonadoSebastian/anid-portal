"""Genera data/crudo/_manifiesto.md: repo, archivo, filas reales, tamano, sha256 y fecha.

Las filas se cuentan con pandas (los CSV de ANID traen saltos de linea dentro de
campos citados, asi que `wc -l` da un numero distinto al real).

Uso: py -3.11 scripts/manifiesto.py
"""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CRUDO = RAIZ / "data" / "crudo"
DESTINO = CRUDO / "_manifiesto.md"

# Archivos tabulares de interes (los PDF y licencias no se cuentan)
EXTENSIONES = {".csv", ".xlsx"}
EXCLUIR = {"_manifiesto.md"}
CHILE = timezone(timedelta(hours=-3))  # CLT (verano); -4 en invierno


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def contar_filas(ruta: Path) -> int | None:
    """Filas de datos (sin encabezado). None si no se puede leer como tabla."""
    try:
        if ruta.suffix.lower() == ".csv":
            df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
        else:
            df = pd.read_excel(ruta, dtype=str)
        return int(len(df))
    except Exception as exc:  # noqa: BLE001 - el manifiesto no debe caerse por un archivo raro
        print(f"    ! no se pudo contar {ruta.name}: {exc}", file=sys.stderr)
        return None


def main() -> int:
    if not CRUDO.is_dir():
        print(f"No existe {CRUDO}. Corre primero scripts/refrescar-corte.sh", file=sys.stderr)
        return 1

    ahora = datetime.now(CHILE)
    lineas = [
        "# Manifiesto del corte crudo",
        "",
        f"**Fecha de descarga:** {ahora:%Y-%m-%d %H:%M} (hora Chile)",
        f"**Directorio:** `data/crudo/`",
        "",
        "| Repo | Archivo | Filas | Tamaño (MB) | sha256 (primeros 16) |",
        "|------|---------|-------|-------------|----------------------|",
    ]
    total_filas = 0
    n = 0
    for repo in sorted(p for p in CRUDO.iterdir() if p.is_dir()):
        for archivo in sorted(repo.iterdir()):
            if archivo.suffix.lower() not in EXTENSIONES or archivo.name in EXCLUIR:
                continue
            filas = contar_filas(archivo)
            mb = archivo.stat().st_size / 1e6
            lineas.append(
                f"| `{repo.name}` | `{archivo.name}` | "
                f"{filas if filas is not None else '—'} | {mb:.1f} | "
                f"`{sha256(archivo)[:16]}` |"
            )
            total_filas += filas or 0
            n += 1

    lineas += [
        "",
        f"**Archivos tabulares:** {n} · **Filas totales:** {total_filas:,}".replace(",", "."),
        "",
        "> Cifras de referencia por archivo en `docs/datos.md`. Si un conteo de este manifiesto",
        "> difiere del documentado, gana este manifiesto y `docs/datos.md` debe corregirse.",
    ]

    DESTINO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Manifiesto escrito: {DESTINO} ({n} archivos, {total_filas} filas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
