"""H3 — Moneda y monto.

El monto del histórico viene en **miles de pesos** y con cuatro rótulos distintos
("Miles de pesos (M$)", "MILES DE PESOS (M$)", "M$", "Miles de pesos"), 38 filas
en EUROS y 2.423 filas sin monto. Un `58.191` significa $58.191.000.

Reglas:
  - los rótulos en pesos se llevan a pesos (× 1.000)
  - los euros NO se convierten ni se suman: van a una columna aparte
  - sin monto o valor no numérico → monto nulo y `valido = False` (no se imputa)
"""

from __future__ import annotations

import re

import pandas as pd

PESOS = "MILES DE PESOS"
EUROS = "EUROS"
SIN_MONEDA = "SIN MONEDA"

# Rótulos observados en BDH_HISTORICA.csv (2026-10-09)
_ROTULOS_PESOS = (
    "miles de pesos (m$)",
    "miles de pesos (m$)",
    "miles de pesos",
    "m$",
)
_ROTULOS_EUROS = ("euros", "euro", "eur")

# El literal aparece dos veces en el histórico y no es un monto
_NO_ES_MONTO = "no solicita a conicyt"


def rotulo_moneda(valor: str) -> str:
    """Normaliza el rótulo de moneda a PESOS / EUROS / SIN MONEDA."""
    s = str(valor).strip().lower()
    if not s:
        return SIN_MONEDA
    if any(s.startswith(r[:6]) for r in _ROTULOS_EUROS) or s in _ROTULOS_EUROS:
        return EUROS
    if any(s == r for r in _ROTULOS_PESOS) or "pesos" in s or s.replace(" ", "") == "m$":
        return PESOS
    return SIN_MONEDA


def es_pesos(valor: str) -> bool:
    return rotulo_moneda(valor) == PESOS


def es_notacion_cientifica(valor: str) -> bool:
    """True si el valor viene en notación científica ('2E+05'), como lo exporta Excel.

    Aparece **una vez** en el histórico (código 1261710, FONDECYT Regular 2026, rótulo
    `MILES DE PESOS (M$)`) y viene igual en el CSV y en el XLSX espejo de ANID: es un defecto
    de la fuente. Se cuenta aparte para que la corrección quede visible y auditable.
    """
    return bool(re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?[eE][+-]?\d+", str(valor).strip().replace("$", "")))


def _a_numero(valor: str) -> float | None:
    """'227.497,14' → 227497.14 · '' o 'NO SOLICITA A CONICYT' → None."""
    s = str(valor).strip()
    if not s or s.lower() == _NO_ES_MONTO:
        return None
    if es_notacion_cientifica(s):
        # Se interpreta el valor tal como está escrito. Sin esto el `re.sub` de más abajo deja
        # '205' y el monto se publica mil veces menor (el error que dejaba la suma del país
        # $199.795.000 por debajo de la real).
        try:
            return float(s.replace("$", "").strip().replace(",", "."))
        except ValueError:
            return None
    s = s.replace("$", "").replace(" ", "")
    # separador de miles '.', decimal ','
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    s = re.sub(r"[^0-9.\-]", "", s)
    if s in {"", ".", "-"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def a_pesos(valor: str, rotulo: str) -> float | None:
    """Monto en pesos. Devuelve None si el rótulo no es pesos o el valor no es numérico."""
    if rotulo_moneda(rotulo) != PESOS:
        return None
    n = _a_numero(valor)
    return None if n is None else n * 1000.0


def a_euros(valor: str, rotulo: str) -> float | None:
    if rotulo_moneda(rotulo) != EUROS:
        return None
    return _a_numero(valor)


def normalizar_montos(df: pd.DataFrame, col_monto: str = "MONTO_ADJUDICADO", col_moneda: str = "MONEDA") -> pd.DataFrame:
    """Agrega `monto_clp`, `monto_eur`, `moneda_homologada` y `monto_valido`.

    No filtra ni rellena: marca. El filtro lo decide cada métrica.
    """
    out = df.copy()
    out["moneda_homologada"] = out[col_moneda].map(rotulo_moneda)
    out["monto_clp"] = [
        a_pesos(v, r) for v, r in zip(out[col_monto], out[col_moneda], strict=True)
    ]
    out["monto_eur"] = [
        a_euros(v, r) for v, r in zip(out[col_monto], out[col_moneda], strict=True)
    ]
    out["monto_valido"] = out["monto_clp"].notna()
    return out


# Cifras de control medidas el 2026-10-09 con scripts/cuadre_homologacion.py.
# `sin monto en pesos` = 2.413 sin rótulo de moneda + 10 con rótulo de pesos y valor
# vacío + 2 con el literal "NO SOLICITA A CONICYT". Los 38 euros no se convierten.
CONTROL_SIN_MONTO = 2_425
CONTROL_EN_EUROS = 38
CONTROL_FILAS_PESOS = 46_563
CONTROL_FILAS_SIN_ROTULO = 2_413
# 2020-2025, sólo filas con rótulo en pesos y monto numérico: $1.160.514 millones (RM)
CONTROL_RM_2020_2025_CLP = 1_160_514_000_000.0
CONTROL_RM_2020_2025_FILAS = 6_093
CONTROL_PERIODO_2020_2025_FILAS = 11_395
CONTROL_NACIONAL_2020_2025_CLP = 2_095_227_000_000.0
