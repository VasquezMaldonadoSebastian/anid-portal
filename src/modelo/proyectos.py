"""Hecho de proyectos adjudicados: una fila por registro del histórico, ya homologado.

Es el eje del tablero. Cada fila trae su región y macrozona canónicas, su institución con
clave, su monto nominal y su monto en pesos constantes, y las tres señales que el tablero
necesita para no mentir: si el monto es válido, si la institución tiene RUT deducido y si
la fila es parte de un código repetido.

Unidad de conteo: **el tablero nunca muestra "total" a secas** — muestra `filas`, `codigos`
o `proyectos` (par código+año), que dan 49.014 / 48.707 / 48.835 sobre esta base.
"""

from __future__ import annotations

import pandas as pd

from homologacion.categorias import homologar_sexo, homologar_tipo_beneficiario
from homologacion.institucion import normalizar_nombre
from homologacion.macrozona import macrozona_de_region
from homologacion.moneda import normalizar_montos
from homologacion.region import homologar_region
from homologacion.subdireccion import homologar_subdireccion

from .deflactores import Deflactores
from .instituciones import resolver_clave

# columnas del archivo → columnas del modelo
RENOMBRES = {
    "CODIGO_PROYECTO": "codigo_proyecto",
    "SUBDIRECCION": "subdireccion",
    "PROGRAMA": "programa",
    "INSTRUMENTO": "instrumento",
    "NOMBRE_CONCURSO": "nombre_concurso",
    "AGNO_CONCURSO": "anno_concurso",
    "AGNO_FALLO": "anno_fallo",
    "AREA_OCDE": "area_ocde",
    "DISCIPLINA_DETALLE": "disciplina",
    "DURACION_MESES": "duracion_meses",
    "NOMBRE_PROYECTO": "nombre_proyecto",
}

COLUMNAS = [
    "codigo_proyecto",
    "anno_fallo",
    "anno_concurso",
    "subdireccion",
    "programa",
    "instrumento",
    "nombre_concurso",
    "area_ocde",
    "disciplina",
    "duracion_meses",
    "tipo_beneficiario",
    "sexo",
    "institucion",
    "institucion_clave",
    "institucion_normalizada",
    "rut_deducido",
    "region",
    "macrozona",
    "moneda",
    "monto_clp",
    "monto_clp_real",
    "deflactor",
    "monto_valido",
    "codigo_repetido",
]


def construir_proyectos(
    historico: pd.DataFrame, deflactores: Deflactores, mapa_rut: dict[str, str]
) -> pd.DataFrame:
    """Hecho de proyectos, homologado y deflactado."""
    df = normalizar_montos(historico)

    out = pd.DataFrame(index=df.index)
    for origen, destino in RENOMBRES.items():
        out[destino] = df[origen].astype(str).str.strip()
    out["anno_fallo"] = pd.to_numeric(df["AGNO_FALLO"], errors="coerce").astype("Int64")
    out["anno_concurso"] = pd.to_numeric(df["AGNO_CONCURSO"], errors="coerce").astype("Int64")
    out["duracion_meses"] = pd.to_numeric(df["DURACION_MESES"], errors="coerce").astype("Int64")

    out["subdireccion"] = df["SUBDIRECCION"].map(homologar_subdireccion)
    out["tipo_beneficiario"] = df["TIPO_BENEFICIARIO"].map(homologar_tipo_beneficiario)
    out["sexo"] = df["SEXO"].map(homologar_sexo)
    out["region"] = df["REGION_EJECUCION"].map(homologar_region)
    out["macrozona"] = out["region"].map(macrozona_de_region)

    out["institucion"] = df["INSTITUCION_PRINCIPAL"].astype(str).str.strip()
    out["institucion_normalizada"] = out["institucion"].map(normalizar_nombre)
    claves = [resolver_clave(n, mapa_rut) for n in out["institucion"]]
    out["institucion_clave"] = [c for c, _ in claves]
    out["rut_deducido"] = [d for _, d in claves]

    out["moneda"] = df["moneda_homologada"]
    out["monto_clp"] = df["monto_clp"]
    out["monto_valido"] = df["monto_valido"]

    out = deflactores.aplicar(out, col_monto="monto_clp", col_anio="anno_fallo")

    repetidos = df["CODIGO_PROYECTO"].duplicated(keep=False)
    out["codigo_repetido"] = repetidos.to_numpy()

    return out[COLUMNAS].reset_index(drop=True)
