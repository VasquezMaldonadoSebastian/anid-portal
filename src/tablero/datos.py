"""Carga del modelo curado y filtros del tablero.

El tablero NO lee los CSV crudos: consume `outputs/` (Fase 2). Si falta, el error dice qué
comando correr. Los filtros son funciones puras sobre esas tablas, salvo la ficha de institución,
que consulta el hecho.

Cuidado heredado de la Fase 2: para agregar se usa `modelo.agregar.agrupar` (construcción por
arrays y orden por posición), nunca una búsqueda por etiqueta después de un `groupby`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

from modelo.agregar import agrupar, ordenar_por  # noqa: E402

SALIDA = RAIZ / "outputs"
TABLAS = (
    "proyectos",
    "colaboracion",
    "postulaciones",
    "becas",
    "dim_institucion",
    "agg_region",
    "agg_institucion",
    "agg_programa",
    "tasa_region",
)


class ModeloAusente(RuntimeError):
    """El modelo curado no está en disco."""


@st.cache_data(show_spinner="Cargando el modelo curado…")
def cargar(nombre: str) -> pd.DataFrame:
    archivo = SALIDA / f"{nombre}.parquet"
    if not archivo.exists():
        raise ModeloAusente(
            f"Falta {archivo}. Correr: py -3.11 scripts/construir-modelo.py (después de "
            "bash scripts/refrescar-corte.sh si tampoco están los datos crudos)."
        )
    return pd.read_parquet(archivo)


@st.cache_data
def cargar_meta() -> dict:
    archivo = SALIDA / "_meta.json"
    if not archivo.exists():
        raise ModeloAusente(f"Falta {archivo}. Correr: py -3.11 scripts/construir-modelo.py")
    return json.loads(archivo.read_text(encoding="utf-8"))


def opciones(df: pd.DataFrame, columna: str) -> list[str]:
    """Valores distintos de una columna, ordenados, sin nulos. Nunca asume que la columna existe."""
    if columna not in df.columns:
        return []
    valores = df[columna].dropna().unique().tolist()
    return sorted(str(v) for v in valores)


def filtrar(
    df: pd.DataFrame,
    filtros: dict,
    columnas: tuple[str, ...] = ("region", "macrozona", "anno_fallo", "subdireccion", "instrumento"),
) -> pd.DataFrame:
    """Aplica los filtros del panel lateral a cualquier tabla del modelo.

    Sólo usa las columnas que existen en `df`: así la misma función sirve para el hecho, los
    agregados y la tabla de tasa (que no tiene subdirección). **No** filtra por institución salvo
    que se pida explícitamente, porque no todas las tablas la traen. La subdirección y el
    instrumento vienen por defecto: dejar el instrumento fuera del default hacía que su selector
    del panel no filtrara nada.
    """
    out = df
    if "region" in columnas and filtros.get("regiones") and "region" in out.columns:
        out = out[out["region"].isin(filtros["regiones"])]
    if "macrozona" in columnas and filtros.get("macrozonas") and "macrozona" in out.columns:
        out = out[out["macrozona"].isin(filtros["macrozonas"])]
    if "subdireccion" in columnas and filtros.get("subdirecciones") and "subdireccion" in out.columns:
        out = out[out["subdireccion"].isin(filtros["subdirecciones"])]
    if "instrumento" in columnas and filtros.get("instrumentos") and "instrumento" in out.columns:
        out = out[out["instrumento"].isin(filtros["instrumentos"])]
    if "anno_fallo" in out.columns:
        desde, hasta = filtros.get("anios", (1982, 2025))
        out = out[out["anno_fallo"].between(desde, hasta)]
    if "institucion_clave" in out.columns and filtros.get("instituciones"):
        out = out[out["institucion_clave"].isin(filtros["instituciones"])]
    return out


def _suma(serie: pd.Series) -> float:
    """Suma que distingue «0» de «sin dato»: si todos los valores del grupo son nulos, da NaN."""
    return float(serie.sum(min_count=1))


def medida_global(df: pd.DataFrame, medida: str) -> int:
    """La medida sobre TODA la selección, medida directamente (no sumada desde los grupos).

    Un proyecto puede tener filas en más de una región o macrozona: sumar los `nunique` de cada
    grupo cuenta dos veces el mismo par código · año y el «total» de la vista no coincide con el de
    las otras. Los grupos sirven para repartir, no para totalizar.
    """
    if medida == "filas":
        return int(len(df))
    if medida == "codigos":
        return int(df["codigo_proyecto"].nunique())
    return int((df["codigo_proyecto"].astype(str) + "|" + df["anno_fallo"].astype(str)).nunique())


def ficha_institucion(hecho: pd.DataFrame, clave: str) -> dict:
    """Todo lo que la ficha necesita, en un solo paso y sin búsquedas por etiqueta."""
    parte = hecho[hecho["institucion_clave"].eq(clave)]
    if parte.empty:
        return {}
    por_anio = agrupar(
        parte,
        ["anno_fallo"],
        {"filas": ("codigo_proyecto", "size"), "codigos": ("codigo_proyecto", "nunique")},
    )
    por_instrumento = agrupar(
        parte,
        ["instrumento"],
        {"filas": ("codigo_proyecto", "size"), "codigos": ("codigo_proyecto", "nunique")},
    )
    return {
        "nombre": str(parte["institucion"].mode().iloc[0]) if len(parte) else clave,
        "filas": int(len(parte)),
        "codigos": int(parte["codigo_proyecto"].nunique()),
        "monto_clp": _suma(parte.loc[parte["monto_valido"], "monto_clp"]),
        "monto_clp_real": _suma(parte.loc[parte["monto_valido"], "monto_clp_real"]),
        "regiones": sorted(parte["region"].dropna().unique().tolist()),
        "macrozonas": sorted(parte["macrozona"].dropna().unique().tolist()),
        "anios": (int(parte["anno_fallo"].min()), int(parte["anno_fallo"].max())),
        "por_anio": ordenar_por(por_anio, ["anno_fallo"], True),
        "por_instrumento": ordenar_por(por_instrumento, ["codigos"], False),
        "sin_monto": int((~parte["monto_valido"]).sum()),
        "sin_deflactor": int((parte["monto_valido"] & parte["monto_clp_real"].isna()).sum()),
    }
