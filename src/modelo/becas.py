"""Hecho de becas adjudicadas (Capital Humano).

19.288 becas con institución, región de origen, sexo, destino y estado de graduación. Es el
destino real de las adjudicaciones de Capital Humano: en el tablero las becas **nunca** se suman
con los proyectos (son universos distintos), y el indicador lo dice.
"""

from __future__ import annotations

import pandas as pd

from homologacion.categorias import homologar_sexo
from homologacion.institucion import normalizar_nombre
from homologacion.macrozona import macrozona_de_region
from homologacion.region import homologar_region
from homologacion.subdireccion import homologar_subdireccion

from .instituciones import resolver_clave

COLUMNAS = [
    "codigo_beca",
    "anno_fallo",
    "subdireccion",
    "programa",
    "tipo_beca",
    "nivel_beca",
    "tipo_programa",
    "programa_estudios",
    "disciplina",
    "institucion",
    "institucion_clave",
    "sexo",
    "region_origen",
    "macrozona",
    "destino",
    "pais_programa",
    "estado_graduacion",
]


def construir_becas(becas: pd.DataFrame, mapa_rut: dict[str, str]) -> pd.DataFrame:
    """Hecho de becas, homologado (sexo, región de origen, institución)."""
    out = pd.DataFrame(index=becas.index)
    out["codigo_beca"] = becas["CODIGO_BECA"].astype(str).str.strip()
    out["anno_fallo"] = pd.to_numeric(becas["AGNO_FALLO"], errors="coerce").astype("Int64")
    out["subdireccion"] = becas["SUBDIRECCION"].map(homologar_subdireccion)
    out["programa"] = becas["PROGRAMA"].astype(str).str.strip()
    out["tipo_beca"] = becas["TIPO_BECA"].astype(str).str.strip()
    out["nivel_beca"] = becas["NIVEL_BECA"].astype(str).str.strip()
    out["tipo_programa"] = becas["TIPO_PROGRAMA"].astype(str).str.strip()
    out["programa_estudios"] = becas["PROGRAMA_DE_ESTUDIOS"].astype(str).str.strip()
    out["disciplina"] = becas["DISCIPLINA_OCDE"].astype(str).str.strip()

    out["institucion"] = becas["INSTITUCION_PRINCIPAL"].astype(str).str.strip()
    out["institucion_clave"] = [
        resolver_clave(n, mapa_rut)[0] for n in out["institucion"]
    ]
    out["institucion_normalizada"] = out["institucion"].map(normalizar_nombre)

    out["sexo"] = becas["SEXO"].map(homologar_sexo)
    out["region_origen"] = becas["REGION_DE_ORIGEN"].map(homologar_region)
    out["macrozona"] = out["region_origen"].map(macrozona_de_region)
    out["destino"] = becas["DESTINO"].astype(str).str.strip()
    out["pais_programa"] = becas["PAIS_PROGRAMA"].astype(str).str.strip().str.upper()
    out["estado_graduacion"] = becas["ESTADO_GRADUACION"].astype(str).str.strip()

    return out[COLUMNAS].reset_index(drop=True)
