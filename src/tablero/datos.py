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
    columnas: tuple[str, ...] = ("region", "macrozona", "anno_fallo", "subdireccion"),
) -> pd.DataFrame:
    """Aplica los filtros del panel lateral a cualquier tabla del modelo.

    Sólo usa las columnas que existen en `df`: así la misma función sirve para el hecho, los
    agregados y la tabla de tasa (que no tiene subdirección). **No** filtra por institución ni
    instrumento salvo que se pidan explícitamente, porque no todas las tablas los traen.
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


def resumen_territorial(df: pd.DataFrame, nivel: str, medida: str) -> pd.DataFrame:
    """Agrega el hecho por `nivel` (region o macrozona) con la medida elegida."""
    med = "filas" if medida == "filas" else medida
    otras = [m for m in ("filas", "codigos", "proyectos", "monto_clp", "monto_clp_real") if m != med]
    agg = agrupar(
        df,
        [nivel],
        {med: ("codigo_proyecto", "size" if med == "filas" else "nunique"), **{
            m: ("monto_clp" if m == "monto_clp" else "monto_clp_real", "sum") for m in otras if m.startswith("monto")
        }, **{
            m: ("codigo_proyecto", "nunique") for m in otras if not m.startswith("monto")
        }},
    )
    return ordenar_por(agg, [med], False)


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
        "monto_clp": float(parte.loc[parte["monto_valido"], "monto_clp"].sum()),
        "monto_clp_real": float(parte.loc[parte["monto_valido"], "monto_clp_real"].sum()),
        "regiones": sorted(parte["region"].dropna().unique().tolist()),
        "macrozonas": sorted(parte["macrozona"].dropna().unique().tolist()),
        "anios": (int(parte["anno_fallo"].min()), int(parte["anno_fallo"].max())),
        "por_anio": ordenar_por(por_anio, ["anno_fallo"], True),
        "por_instrumento": ordenar_por(por_instrumento, ["codigos"], False),
        "sin_monto": int((~parte["monto_valido"]).sum()),
        "sin_deflactor": int((parte["monto_valido"] & parte["monto_clp_real"].isna()).sum()),
    }
