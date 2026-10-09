"""H6 — Institución.

El histórico NO trae RUT: el cruce con Colaboración es por nombre y coincide en el
94% de los casos (el resto es la divergencia que ANID declara por cambios de
institución al firmar convenio). Regla: **el RUT manda cuando existe**; el nombre
normalizado es el respaldo.

Medido el 2026-10-09: Histórico 1.749 nombres → 1.733 normalizados (solo 16 grupos
fusionan variantes). Colaboración 5.694 → 5.574 con RUT 2.501 → 2.477. Hay 411 RUT
con más de un nombre y 117 nombres con más de un RUT: esas colisiones se REPORTAN
al usuario (docs/evidencia/instituciones-colisiones.md), no se resuelven solas.
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

SIN_INFORMACION = "SIN INFORMACION"

# Palabras que NO se quitan: la razón social es el activo, no ruido.
# Solo se normaliza tipografía (tildes, puntuación, espacios).


def _norm(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    s = s.upper().replace("-", " ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def normalizar_nombre(texto: str) -> str:
    """Nombre de institución comparable (sin tildes, sin puntuación, sin dobles espacios)."""
    return _norm(texto)


def normalizar_rut(valor: str) -> str | None:
    """RUT de institución normalizado (NNNNNNNN-K) o None si no es un RUT.

    Un guion, un vacío o el literal 'SIN INFORMACION' no son credenciales ni claves:
    se rechazan explícitamente en vez de pasar como identificador.
    """
    s = str(valor).strip().upper()
    if not s or s in {SIN_INFORMACION, "-", "NO APLICA", "NO REGISTRA"}:
        return None
    limpio = re.sub(r"[^0-9K]", "", s)
    if len(limpio) < 2:
        return None
    cuerpo, dv = limpio[:-1], limpio[-1]
    if not cuerpo.isdigit() or dv not in "0123456789K":
        return None
    return f"{cuerpo}-{dv}"


def clave_institucion(nombre: str, rut: str | None = None) -> str:
    """Clave canónica: RUT si es válido, si no el nombre normalizado."""
    r = normalizar_rut(rut) if rut is not None else None
    if r:
        return f"RUT:{r}"
    return f"NOMBRE:{normalizar_nombre(nombre)}"


def reporte_colisiones(df: pd.DataFrame, col_nombre: str, col_rut: str) -> dict[str, pd.DataFrame]:
    """Las dos ambigüedades de la clave institucional, para decisión del usuario.

    - `rut_con_varios_nombres`: un RUT con más de un nombre declarado
    - `nombre_con_varios_rut`: un nombre con más de un RUT declarado
    """
    d = df[[col_nombre, col_rut]].copy()
    d["_rut"] = d[col_rut].map(normalizar_rut)
    d["_nombre"] = d[col_nombre].map(normalizar_nombre)
    con_rut = d[d["_rut"].notna()]

    por_rut = (
        con_rut.groupby("_rut")["_nombre"]
        .nunique()
        .loc[lambda s: s > 1]
        .sort_values(ascending=False)
    )
    por_nombre = (
        con_rut.groupby("_nombre")["_rut"]
        .nunique()
        .loc[lambda s: s > 1]
        .sort_values(ascending=False)
    )

    detalle_rut = (
        con_rut[con_rut["_rut"].isin(por_rut.index)]
        .groupby("_rut")["_nombre"]
        .agg(lambda s: " | ".join(sorted(s.unique())))
        .to_frame("nombres")
    )
    detalle_rut["n_nombres"] = por_rut
    detalle_nombre = (
        con_rut[con_rut["_nombre"].isin(por_nombre.index)]
        .groupby("_nombre")["_rut"]
        .agg(lambda s: " | ".join(sorted(s.unique())))
        .to_frame("ruts")
    )
    detalle_nombre["n_ruts"] = por_nombre
    return {
        "rut_con_varios_nombres": detalle_rut.reset_index().sort_values("n_nombres", ascending=False),
        "nombre_con_varios_rut": detalle_nombre.reset_index().sort_values("n_ruts", ascending=False),
    }


# Cifras de control medidas el 2026-10-09 con scripts/cuadre_homologacion.py.
# Las colisiones se cuentan SÓLO sobre RUT válidos (un 'SIN INFORMACION' o un guion
# no es un identificador): de ahí la diferencia con el primer perfilado — que contaba
# el campo crudo y por eso inflaba el segundo número (117 nombres con "varios RUT"
# incluían los que compartían el RUT vacío).
CONTROL_HISTORICO_NOMBRES = 1_749
CONTROL_HISTORICO_NORMALIZADOS = 1_733
CONTROL_COLABORACION_NOMBRES = 5_694
CONTROL_COLABORACION_NORMALIZADOS = 5_574
CONTROL_COLABORACION_RUT = 2_476
CONTROL_RUT_CON_VARIOS_NOMBRES = 373
CONTROL_NOMBRE_CON_VARIOS_RUT = 21
