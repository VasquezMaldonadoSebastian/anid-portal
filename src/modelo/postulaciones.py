"""Hecho de postulaciones: el único lugar donde existe el denominador.

139.517 postulaciones 2016-2025 con estado (adjudicada / no adjudicada / fuera de base) y región.
El tablero puede calcular tasa de adjudicación **por región** y por instrumento, **nunca por
institución**: esta base no trae nombre de institución y las no adjudicadas no tienen institución
en ninguna otra base. Por eso el modelo expone la tasa solo en las dimensiones donde el
denominador es completo.

Aviso que el modelo hace explícito: **Capital Humano no compite por proyectos** — sus
adjudicaciones viven en Becas. Mezclarlo con las demás subdirecciones mueve el indicador, así que
la fila lleva `es_capital_humano` y las agregaciones de proyectos lo excluyen.
"""

from __future__ import annotations

import pandas as pd

from homologacion.categorias import homologar_sexo, homologar_tipo_beneficiario
from homologacion.macrozona import macrozona_de_region
from homologacion.region import homologar_region
from homologacion.subdireccion import homologar_subdireccion

from .agregar import agrupar, ordenar_por

ADJUDICADO = "ADJUDICADO"

COLUMNAS = [
    "codigo_proyecto",
    "anno_fallo",
    "subdireccion",
    "es_capital_humano",
    "programa",
    "instrumento",
    "instrumento_recat",
    "nombre_concurso",
    "estado",
    "adjudicado",
    "tipo_beneficiario",
    "tipo_institucion",
    "sexo",
    "region",
    "macrozona",
]


def construir_postulaciones(postulaciones: pd.DataFrame) -> pd.DataFrame:
    """Hecho de postulaciones, homologado, con el estado legible."""
    out = pd.DataFrame(index=postulaciones.index)
    out["codigo_proyecto"] = postulaciones["CODIGO_PROYECTO"].astype(str).str.strip()
    out["anno_fallo"] = pd.to_numeric(postulaciones["AGNO_FALLO"], errors="coerce").astype("Int64")
    out["subdireccion"] = postulaciones["SUBDIRECCION"].map(homologar_subdireccion)
    out["es_capital_humano"] = out["subdireccion"].eq("CAPITAL HUMANO")
    out["programa"] = postulaciones["PROGRAMA"].astype(str).str.strip()
    out["instrumento"] = postulaciones["INSTRUMENTO"].astype(str).str.strip()
    out["instrumento_recat"] = postulaciones["INSTRUMENTO_RECAT"].astype(str).str.strip()
    out["nombre_concurso"] = postulaciones["NOMBRE_CONCURSO"].astype(str).str.strip()

    estado = postulaciones["ESTADO_RESOLUCION_CONCURSO"].astype(str).str.strip().str.upper()
    out["estado"] = estado
    out["adjudicado"] = estado.eq(ADJUDICADO)

    out["tipo_beneficiario"] = postulaciones["TIPO_BENEFICIARIO"].map(homologar_tipo_beneficiario)
    out["tipo_institucion"] = postulaciones["TIPO_INSTITUCION"].astype(str).str.strip().str.upper()
    out["sexo"] = postulaciones["SEXO"].map(homologar_sexo)
    out["region"] = postulaciones["REGION_EJECUCION"].map(homologar_region)
    out["macrozona"] = out["region"].map(macrozona_de_region)

    return out[COLUMNAS].reset_index(drop=True)


def tasa_por_region(postulaciones: pd.DataFrame) -> pd.DataFrame:
    """Tasa de adjudicación por región y año **de proyectos** (excluye Capital Humano).

    Devuelve `region`, `macrozona`, `anno_fallo`, `postulaciones`, `adjudicadas` y `tasa`
    (porcentaje). Es la única agregación con denominador completo: la base de postulaciones
    no identifica institución.

    Se construye con `modelo.agregar` (agrupación por arrays, orden por posición): ver el
    docstring de ese módulo para el porqué.
    """
    proy = postulaciones[~postulaciones["es_capital_humano"]]
    agg = agrupar(
        proy,
        ["region", "macrozona", "anno_fallo"],
        {"postulaciones": ("adjudicado", "size"), "adjudicadas": ("adjudicado", "sum")},
    )
    agg["adjudicadas"] = agg["adjudicadas"].astype("int64")
    agg["tasa"] = (100 * agg["adjudicadas"] / agg["postulaciones"]).round(2)
    return ordenar_por(agg, ["anno_fallo", "postulaciones"], [False, False])


def tasa_global(postulaciones: pd.DataFrame) -> dict[str, float]:
    """Tasa de adjudicación de proyectos 2016-2025 (control: 26,8%)."""
    proy = postulaciones[~postulaciones["es_capital_humano"]]
    total = len(proy)
    adj = int(proy["adjudicado"].sum())
    return {
        "postulaciones": total,
        "adjudicadas": adj,
        "tasa": round(100 * adj / total, 2),
    }
