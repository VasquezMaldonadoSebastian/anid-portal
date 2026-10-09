"""H2 — Macrozona Minciencia derivada de la región homologada.

El mapeo NO se copió de la definición general de Minciencia: se midió contra el
campo `MACROZONA_MINCIENCIA` del histórico (crosstab región × macrozona, 49.014
filas, 0 regiones con más de una macrozona). El resultado tiene dos diferencias
con la agrupación que uno supondría:

  - Coquimbo va en CENTRO (no en NORTE)
  - O'Higgins va en CENTRO SUR (no en CENTRO)
  - la Región Metropolitana es una macrozona propia (RM), no parte de CENTRO

Las cinco sumas por macrozona cuadran exactas contra el archivo, lo que confirma
que el mapeo es el que usó ANID.
"""

from __future__ import annotations

import pandas as pd

MACROZONAS = ("NORTE", "CENTRO", "RM", "CENTRO SUR", "SUR", "AUSTRAL")

_REGION_A_MACROZONA: dict[str, str] = {
    # NORTE
    "ARICA Y PARINACOTA": "NORTE",
    "TARAPACA": "NORTE",
    "ANTOFAGASTA": "NORTE",
    "ATACAMA": "NORTE",
    # CENTRO
    "COQUIMBO": "CENTRO",
    "VALPARAISO": "CENTRO",
    # RM (macrozona propia)
    "METROPOLITANA": "RM",
    # CENTRO SUR
    "OHIGGINS": "CENTRO SUR",
    "MAULE": "CENTRO SUR",
    "NUBLE": "CENTRO SUR",
    "BIOBIO": "CENTRO SUR",
    # SUR
    "ARAUCANIA": "SUR",
    "LOS RIOS": "SUR",
    "LOS LAGOS": "SUR",
    # AUSTRAL
    "AYSEN": "AUSTRAL",
    "MAGALLANES": "AUSTRAL",
    # no territoriales (se arrastran tal cual)
    "SIN INFORMACION": "SIN INFORMACION",
    "EXTRANJERO": "EXTRANJERO",
    "MULTIREGIONAL": "MULTIREGIONAL",
    # En becas, la region 'NO APLICA' (23 filas) tiene macrozona 'NO APLICA' en el
    # propio archivo: se respeta esa categoría en vez de forzarla a SIN INFORMACION.
    "NO APLICA": "NO APLICA",
}

# Sumas de control medidas el 2026-10-09 sobre BDH_HISTORICA (49.014 filas)
CONTROL_HISTORICO: dict[str, int] = {
    "RM": 27_212,
    "CENTRO SUR": 7_138,
    "CENTRO": 6_082,
    "SUR": 4_803,
    "NORTE": 2_357,
    "SIN INFORMACION": 697,
    "AUSTRAL": 490,
    "EXTRANJERO": 124,
    "MULTIREGIONAL": 111,
}


def macrozona_de_region(region: str) -> str:
    """Macrozona de una región ya homologada (ver region.homologar_region)."""
    return _REGION_A_MACROZONA.get(str(region).strip().upper(), "NO CLASIFICADO")


def verificar_macrozona(df: pd.DataFrame, region: str = "REGION_EJECUCION", macrozona: str = "MACROZONA_MINCIENCIA") -> pd.DataFrame:
    """Devuelve las filas donde la macrozona derivada difiere de la del archivo.

    Un DataFrame vacío es el resultado esperado sobre el histórico y las becas.
    """
    from .region import homologar_region  # import local: evita ciclo en la carga

    region_h = df[region].map(homologar_region)
    derivada = region_h.map(macrozona_de_region)
    del_archivo = df[macrozona].str.strip().str.upper()
    discrepan = derivada != del_archivo
    salida = df.loc[discrepan, [region, macrozona]].copy()
    salida["region_homologada"] = region_h[discrepan]
    salida["macrozona_derivada"] = derivada[discrepan]
    return salida
