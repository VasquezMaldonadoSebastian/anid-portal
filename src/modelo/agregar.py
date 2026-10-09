"""Agregación sin búsquedas por etiqueta — a propósito.

Por qué este módulo existe: en el entorno de trabajo (pandas 2.3.3 + numpy 2.4.6 sobre
Python 3.11 en Windows) aparece de forma **intermitente** el siguiente fallo, reproducible
con pandas puro y datos sintéticos, sin código de este proyecto:

    agg = df.groupby(claves, dropna=False).agg(...).reset_index()
    "col" in agg.columns        # True
    agg.sort_values(["col"])    # KeyError: 'col'
    agg["col"]                  # a veces KeyError, a veces no

Es decir: el nombre está (lo dice `in`) pero el índice del DataFrame no lo resuelve
(`get_loc` falla), y el fallo va y viene entre procesos con el mismo código y los mismos
datos. Un fallo así es peor que un error limpio: produce resultados silenciosamente
distintos. Por eso la regla del paquete es:

    **Después de un `groupby`, nunca se busca por etiqueta.**

Las claves de agrupación se extraen del índice como arrays y el resultado se construye
como un DataFrame nuevo con nombres propios. El orden también se resuelve por posición
(`np.lexsort` + `iloc`), nunca con `sort_values(by=...)`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import numpy as np
import pandas as pd

# nombre de la medida → (columna, función)
FUNCIONES = ("size", "nunique", "sum")


def agrupar(
    df: pd.DataFrame, claves: list[str], medidas: Mapping[str, tuple[str, str]]
) -> pd.DataFrame:
    """Agrupa `df` por `claves` y devuelve un DataFrame nuevo con las `medidas`.

    `medidas` mapea nombre resultante → (columna, función), con función en `FUNCIONES`.
    La construcción es por arrays: no depende de que las etiquetas del groupby sean
    resolubles por nombre después.
    """
    g = df.groupby(claves, dropna=False, sort=False)
    indice = g.size().index

    datos: dict[str, object] = {}
    for posicion, clave in enumerate(claves):
        valores = indice.get_level_values(posicion) if len(claves) > 1 else indice
        datos[clave] = np.asarray(valores)

    for nombre, (columna, funcion) in medidas.items():
        if funcion == "size":
            datos[nombre] = g.size().to_numpy()
        elif funcion == "nunique":
            datos[nombre] = g[columna].nunique().to_numpy()
        elif funcion == "sum":
            # min_count=1: si todos los valores del grupo son nulos, la suma queda nula y no 0.
            # Sin esto el año 2026 (sin IPC cerrado) mostraría «0 pesos reales» en vez de «sin dato».
            datos[nombre] = g[columna].sum(min_count=1).to_numpy()
        else:  # pragma: no cover - proteger de un nombre mal escrito
            raise ValueError(f"función de agregación no soportada: {funcion!r}")

    return pd.DataFrame(datos)


def ordenar_por(
    df: pd.DataFrame, columnas: Iterable[str], ascendentes: Iterable[bool] | bool = True
) -> pd.DataFrame:
    """Ordena por posición, sin `sort_values(by=...)`.

    Equivale a ordenar por varias columnas: se usa `np.lexsort`, que aplica la última
    clave como primaria, así que el orden de las columnas se invierte al pasar a llaves.
    """
    columnas = list(columnas)
    if isinstance(ascendentes, bool):
        ascendentes = [ascendentes] * len(columnas)
    ascendentes = list(ascendentes)
    if len(ascendentes) != len(columnas):
        raise ValueError("hacen falta tantas direcciones como columnas")

    llaves = []
    for columna, ascendente in zip(reversed(columnas), reversed(ascendentes), strict=True):
        valores = df[columna].to_numpy()
        llaves.append(valores if ascendente else _invertir(valores))
    return df.iloc[np.lexsort(llaves)].reset_index(drop=True)


def _invertir(valores: np.ndarray) -> np.ndarray:
    """Negativo para numéricos; para texto se ordena descendente por rango invertido."""
    if np.issubdtype(valores.dtype, np.number) or valores.dtype == object and _es_numerico(valores):
        return -valores.astype(float)
    _, codigos = np.unique(valores, return_inverse=True)
    return -codigos


def _es_numerico(valores: np.ndarray) -> bool:
    try:
        valores.astype(float)
    except (TypeError, ValueError):
        return False
    return True
