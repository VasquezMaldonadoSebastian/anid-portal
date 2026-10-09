"""Dimensión institución: la clave que une el histórico (sin RUT) con Colaboración (con RUT).

El histórico solo trae el nombre; Colaboración trae nombre y RUT pero con variantes de
escritura. Estrategia:

1. Del nombre normalizado de Colaboración se construye un mapa nombre → RUT, **solo para
   los nombres que apuntan a un único RUT** (los ambiguos no se adivinan: quedan por nombre).
2. La clave canónica es `RUT:NNNNNNNN-K` si se conoce y `NOMBRE:<normalizado>` si no.
3. La dimensión conserva el nombre visible (el más frecuente) y las señales de calidad:
   en cuántas regiones aparece, si está en una base y no en la otra, y si su nombre es ambiguo.

Con esto la ficha de institución puede agregar histórico + colaboración bajo una sola clave,
sin fusionar nada a la fuerza.
"""

from __future__ import annotations

import pandas as pd

from homologacion.institucion import clave_institucion, normalizar_nombre, normalizar_rut
from homologacion.macrozona import macrozona_de_region
from homologacion.region import homologar_region


def mapa_nombre_a_rut(colaboracion: pd.DataFrame) -> dict[str, str]:
    """nombre normalizado → RUT, solo cuando el nombre apunta a un único RUT válido."""
    d = colaboracion[["INSTITUCION1ERNIVEL", "RUTINSTITUCION"]].copy()
    d["nombre"] = d["INSTITUCION1ERNIVEL"].map(normalizar_nombre)
    d["rut"] = d["RUTINSTITUCION"].map(normalizar_rut)
    d = d[d["rut"].notna()]
    unicos = d.groupby("nombre")["rut"].nunique()
    sin_ambiguedad = set(unicos[unicos == 1].index)
    d = d[d["nombre"].isin(sin_ambiguedad)]
    return dict(d.groupby("nombre")["rut"].agg(lambda s: s.mode().iloc[0]))


def resolver_clave(
    nombre: str, mapa: dict[str, str], rut: str | None = None
) -> tuple[str, bool]:
    """Clave canónica + si el RUT se dedujo del nombre (en vez de venir en la fila)."""
    r = normalizar_rut(rut) if rut is not None else None
    if r:
        return clave_institucion(nombre, r), False
    n = normalizar_nombre(nombre)
    if n in mapa:
        return clave_institucion(nombre, mapa[n]), True
    return clave_institucion(nombre, None), False


def construir_dim_institucion(
    historico: pd.DataFrame, colaboracion: pd.DataFrame
) -> pd.DataFrame:
    """Una fila por institución con su clave canónica y sus señales de calidad.

    Columnas: `institucion_clave`, `nombre_visible`, `rut`, `rut_deducido`,
    `en_historico`, `en_colaboracion`, `n_regiones`, `region_principal`, `macrozona`,
    `n_registros_historico`, `n_filas_colaboracion`.
    """
    mapa = mapa_nombre_a_rut(colaboracion)

    # --- señales desde el histórico ---
    h = historico[["INSTITUCION_PRINCIPAL", "REGION_EJECUCION"]].copy()
    h["region"] = h["REGION_EJECUCION"].map(homologar_region)
    claves = [resolver_clave(n, mapa) for n in h["INSTITUCION_PRINCIPAL"]]
    h["institucion_clave"] = [c for c, _ in claves]
    h["rut_deducido"] = [d for _, d in claves]
    hist = (
        h.groupby("institucion_clave")
        .agg(
            n_registros_historico=("institucion_clave", "size"),
            n_regiones=("region", "nunique"),
            region_principal=("region", lambda s: s.mode().iloc[0] if len(s) else None),
        )
        .reset_index()
    )

    # --- señales desde colaboración ---
    c = colaboracion[["INSTITUCION1ERNIVEL", "REGIONINSTITUCION", "PAISINSTITUCION"]].copy()
    c["institucion_clave"] = [
        resolver_clave(n, mapa, r)[0]
        for n, r in zip(c["INSTITUCION1ERNIVEL"], colaboracion["RUTINSTITUCION"], strict=True)
    ]
    col = (
        c.groupby("institucion_clave")
        .agg(
            n_filas_colaboracion=("institucion_clave", "size"),
            pais=("PAISINSTITUCION", lambda s: s.mode().iloc[0] if len(s) else None),
            region_colaboracion=("REGIONINSTITUCION", lambda s: s.mode().iloc[0] if len(s) else None),
        )
        .reset_index()
    )

    dim = hist.merge(col, on="institucion_clave", how="outer")

    # --- nombre visible y RUT desde ambas bases ---
    nombres_h = (
        h.assign(nombre=lambda d: d["INSTITUCION_PRINCIPAL"])
        .groupby("institucion_clave")["nombre"]
        .agg(lambda s: s.mode().iloc[0])
    )
    nombres_c = (
        c.assign(nombre=lambda d: d["INSTITUCION1ERNIVEL"])
        .groupby("institucion_clave")["nombre"]
        .agg(lambda s: s.mode().iloc[0])
    )
    nombres = nombres_h.combine_first(nombres_c)
    dim["nombre_visible"] = dim["institucion_clave"].map(nombres)
    dim["nombre_normalizado"] = dim["nombre_visible"].map(normalizar_nombre)
    dim["rut"] = [
        k.split(":", 1)[1] if str(k).startswith("RUT:") else None
        for k in dim["institucion_clave"]
    ]
    dim["rut_deducido"] = dim.get("rut_deducido", pd.Series(False, index=dim.index)).fillna(False)
    dim["en_historico"] = dim["n_registros_historico"].notna()
    dim["en_colaboracion"] = dim["n_filas_colaboracion"].notna()
    dim["n_registros_historico"] = dim["n_registros_historico"].fillna(0).astype(int)
    dim["n_filas_colaboracion"] = dim["n_filas_colaboracion"].fillna(0).astype(int)
    dim["n_regiones"] = dim["n_regiones"].fillna(0).astype(int)

    # región de la institución: la del histórico manda; si no está, la de colaboración
    region = dim["region_principal"].where(
        dim["region_principal"].notna() & (dim["region_principal"] != "SIN INFORMACION"),
        dim["region_colaboracion"].map(lambda v: homologar_region(v) if pd.notna(v) else None),
    )
    dim["region"] = region.fillna("SIN INFORMACION")
    dim["macrozona"] = dim["region"].map(macrozona_de_region)

    columnas = [
        "institucion_clave",
        "nombre_visible",
        "nombre_normalizado",
        "rut",
        "rut_deducido",
        "pais",
        "region",
        "macrozona",
        "n_regiones",
        "en_historico",
        "en_colaboracion",
        "n_registros_historico",
        "n_filas_colaboracion",
    ]
    return dim[columnas].sort_values("n_registros_historico", ascending=False).reset_index(drop=True)
