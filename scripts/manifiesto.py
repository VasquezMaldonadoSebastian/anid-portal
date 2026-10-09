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


# Codificaciones que se prueban en orden. Los CSV de ANID son utf-8-sig, pero
# `FONDECYT-Abstracts/Abstract_Iniciación_2016_2025.csv` viene en latin-1 (byte 0xf3
# en posición 101): leerlo con utf-8 lo mata.
CODIFICACIONES = ("utf-8-sig", "utf-8", "latin-1")


def contar_filas(ruta: Path) -> tuple[int | None, str | None]:
    """Filas con su codificación. (None, None) si no se puede leer como tabla."""
    if ruta.suffix.lower() == ".csv":
        for codificacion in CODIFICACIONES:
            try:
                df = pd.read_csv(
                    ruta, sep=";", encoding=codificacion, dtype=str, low_memory=False
                )
            except UnicodeDecodeError:
                continue
            except Exception as exc:  # noqa: BLE001 - el manifiesto no debe caerse por un archivo raro
                print(f"    ! no se pudo contar {ruta.name}: {exc}", file=sys.stderr)
                return None, None
            return int(len(df)), codificacion
        print(f"    ! ninguna codificación funcionó para {ruta.name}", file=sys.stderr)
        return None, None

    try:
        return int(len(pd.read_excel(ruta, dtype=str))), None
    except Exception as exc:  # noqa: BLE001
        print(f"    ! no se pudo contar {ruta.name}: {exc}", file=sys.stderr)
        return None, None


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
        "El CSV y el XLSX de cada base son **el mismo contenido en dos formatos** (verificado: mismos",
        "conteos), así que el total de filas se cuenta **sólo sobre los CSV** — sumar ambos duplicaría",
        "cada base. Los XLSX quedan listados como espejo, con su propio conteo, para detectar que un",
        "formato se actualice y el otro no.",
        "",
        "| Repo | Archivo | Formato | Filas | Tamaño (MB) | sha256 (primeros 16) |",
        "|------|---------|---------|-------|-------------|----------------------|",
    ]
    filas_csv = 0
    filas_xlsx = 0
    n_csv = 0
    n_xlsx = 0
    sin_leer: list[str] = []
    discrepancias: list[str] = []
    por_base: dict[str, dict[str, int]] = {}
    for repo in sorted(p for p in CRUDO.iterdir() if p.is_dir()):
        for archivo in sorted(repo.iterdir()):
            if archivo.suffix.lower() not in EXTENSIONES or archivo.name in EXCLUIR:
                continue
            filas, codificacion = contar_filas(archivo)
            mb = archivo.stat().st_size / 1e6
            formato = archivo.suffix.lower().lstrip(".")
            if filas is None:
                sin_leer.append(f"`{archivo.name}`")
            # la codificación se hace visible cuando no es la esperada
            nota = f" ({codificacion})" if codificacion and codificacion != "utf-8-sig" else ""
            lineas.append(
                f"| `{repo.name}` | `{archivo.name}`{nota} | {formato} | "
                f"{filas if filas is not None else '—'} | {mb:.1f} | "
                f"`{sha256(archivo)[:16]}` |"
            )
            base = archivo.stem
            por_base.setdefault(base, {})[formato] = filas or 0
            if formato == "csv":
                filas_csv += filas or 0
                n_csv += 1
            else:
                filas_xlsx += filas or 0
                n_xlsx += 1

    for base, formatos in sorted(por_base.items()):
        if "csv" in formatos and "xlsx" in formatos and formatos["csv"] != formatos["xlsx"]:
            discrepancias.append(
                f"`{base}`: CSV {formatos['csv']} vs XLSX {formatos['xlsx']}"
            )

    lineas += [
        "",
        f"**CSV (base canónica):** {n_csv} archivos · **{filas_csv:,} filas**".replace(",", "."),
        f"**XLSX (espejo, no se suma):** {n_xlsx} archivos · {filas_xlsx:,} filas".replace(",", "."),
        "",
        *([f"**⚠️ No se pudieron leer:** {' · '.join(sin_leer)}"] if sin_leer else []),
        (
            "**Sin discrepancias entre CSV y XLSX.**"
            if not discrepancias
            else "**⚠️ CSV y XLSX no coinciden en:** " + " · ".join(discrepancias)
        ),
        "",
        "> Cifras de referencia por archivo en `docs/datos.md`. Si un conteo de este manifiesto",
        "> difiere del documentado, gana este manifiesto y `docs/datos.md` debe corregirse.",
    ]

    DESTINO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    # copia versionada: `data/` está fuera de git, y el manifiesto es la trazabilidad
    # del corte (hash + fecha de cada archivo), así que también vive con la evidencia
    COPIA = RAIZ / "docs" / "evidencia" / "manifiesto-corte.md"
    COPIA.parent.mkdir(parents=True, exist_ok=True)
    COPIA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Manifiesto escrito: {DESTINO} ({n_csv} CSV, {filas_csv} filas; {n_xlsx} XLSX espejo)")
    print(f"Copia versionada: {COPIA}")
    if discrepancias:
        for d in discrepancias:
            print(f"  ! CSV/XLSX difieren: {d}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
