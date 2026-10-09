"""Carga de los archivos crudos — una sola forma de leer, sin excepciones.

Los CSV de ANID son `;`-delimitados, con BOM UTF-8 y saltos de línea dentro de
campos citados. Leerlos por defecto (coma) falla o devuelve 1 columna.

El módulo se llama `fuentes` y no `cargar` para que `homologacion.cargar` sea
siempre la función y nunca el módulo.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
CRUDO = RAIZ / "data" / "crudo"

# nombre lógico → (repo, archivo)
FUENTES: dict[str, tuple[str, str]] = {
    "historico": ("Historico-de-Proyectos-Adjudicados", "BDH_HISTORICA.csv"),
    "proyectos_milenio": ("Historico-de-Proyectos-Adjudicados", "BDH_PROYECTOS_MILENIO.csv"),
    "instituciones": ("Colaboracion_Institucional", "CONSOLIDADO_INSTITUCIONES.csv"),
    "spi_investigadores": ("Colaboracion_Institucional", "SPI_INVESTIGADORES.csv"),
    "postulaciones": ("Postulaciones", "POSTULACIONES_2016_2025.csv"),
    "postulaciones_milenio": ("Postulaciones", "POSTULACIONES_MILENIO.csv"),
    "becas": ("Becas", "BDH_BECAS SCH.csv"),
    "palabras_proyectos": ("Palabras_claves", "BD_Palabras_claves_Proyectos.csv"),
    "palabras_becas": ("Palabras_claves", "BD_Palabras_claves_Becas.csv"),
}


def cargar(nombre: str) -> pd.DataFrame:
    """Carga una fuente por su nombre lógico, siempre como texto.

    `dtype=str` no es un detalle: el código de proyecto es alfanumérico y los
    montos traen separador de miles. Todo se castea explícitamente después.
    """
    repo, archivo = FUENTES[nombre]
    ruta = CRUDO / repo / archivo
    if not ruta.exists():
        raise FileNotFoundError(f"falta {ruta} — corre scripts/refrescar-corte.sh")
    df = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str, low_memory=False)
    df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]
    return df
