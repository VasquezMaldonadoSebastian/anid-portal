"""Hecho de colaboración institucional: una fila por (proyecto, institución, rol).

33.731 filas / 16.426 proyectos. Es la única base con RUT de institución, país y rol, así que
alimenta dos cosas: la red de co-participación y el enriquecimiento de la dimensión institución.

El rol se homologa a los 9 canónicos (0 sin clasificar) y `rol_original` se conserva para poder
auditar cualquier agrupamiento contra el archivo.
"""

from __future__ import annotations

import pandas as pd

from homologacion.institucion import normalizar_nombre, normalizar_rut
from homologacion.macrozona import macrozona_de_region
from homologacion.region import homologar_region
from homologacion.roles import homologar_rol
from homologacion.subdireccion import homologar_subdireccion

from .instituciones import resolver_clave

COLUMNAS = [
    "codigo_proyecto",
    "anno_fallo",
    "subdireccion",
    "nombre_concurso",
    "rol",
    "rol_original",
    "institucion",
    "institucion_clave",
    "institucion_normalizada",
    "rut",
    "pais",
    "es_extranjera",
    "region",
    "macrozona",
]


def construir_colaboracion(
    colaboracion: pd.DataFrame, mapa_rut: dict[str, str]
) -> pd.DataFrame:
    """Hecho de colaboración, homologado."""
    out = pd.DataFrame(index=colaboracion.index)
    out["codigo_proyecto"] = colaboracion["CODIGO_PROYECTO"].astype(str).str.strip()
    out["anno_fallo"] = pd.to_numeric(colaboracion["AGNO_FALLO"], errors="coerce").astype("Int64")
    out["subdireccion"] = colaboracion["SUBDIRECCION"].map(homologar_subdireccion)
    out["nombre_concurso"] = colaboracion["NOMBRE_CONCURSO"].astype(str).str.strip()
    out["rol_original"] = colaboracion["ROLINSTITUCION"].astype(str).str.strip()
    out["rol"] = colaboracion["ROLINSTITUCION"].map(homologar_rol)

    out["institucion"] = colaboracion["INSTITUCION1ERNIVEL"].astype(str).str.strip()
    out["institucion_normalizada"] = out["institucion"].map(normalizar_nombre)
    claves = [
        resolver_clave(n, mapa_rut, r)
        for n, r in zip(out["institucion"], colaboracion["RUTINSTITUCION"], strict=True)
    ]
    out["institucion_clave"] = [c for c, _ in claves]
    out["rut"] = colaboracion["RUTINSTITUCION"].map(normalizar_rut)

    out["pais"] = colaboracion["PAISINSTITUCION"].astype(str).str.strip().str.upper()
    out["es_extranjera"] = out["pais"].ne("CHILE")
    out["region"] = colaboracion["REGIONINSTITUCION"].map(homologar_region)
    out["macrozona"] = out["region"].map(macrozona_de_region)

    return out[COLUMNAS].reset_index(drop=True)
