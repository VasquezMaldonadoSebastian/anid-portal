"""H8 — Unidad de conteo.

En el histórico, filas ≠ códigos ≠ proyectos: 49.014 filas, 48.707 códigos únicos
y 136 códigos repetidos (443 filas, todas con contenido distinto: observaciones
astronómicas `GS-****-Q-*` y filas con el código `SININFORMACION`).

Por eso el tablero no muestra "total" a secas: muestra la métrica con su nombre.
"""

from __future__ import annotations

import pandas as pd

FILAS = "filas"
CODIGOS = "codigos_unicos"
PROYECTOS = "proyectos"

CONTROL_HISTORICO_FILAS = 49_014
CONTROL_HISTORICO_CODIGOS = 48_707
CONTROL_HISTORICO_CODIGOS_REPETIDOS = 136


def contar_filas(df: pd.DataFrame) -> int:
    """Filas físicas: una por registro del archivo."""
    return int(len(df))


def contar_codigos(df: pd.DataFrame, columna: str = "CODIGO_PROYECTO") -> int:
    """Códigos distintos: la unidad de 'cuántos proyectos', salvo códigos compartidos."""
    return int(df[columna].nunique())


def contar_proyectos(
    df: pd.DataFrame, columna: str = "CODIGO_PROYECTO", columna_anio: str = "AGNO_FALLO"
) -> int:
    """Pares (código, año) distintos: separa los códigos repetidos en años distintos."""
    return int(df[[columna, columna_anio]].drop_duplicates().shape[0])


def codigos_repetidos(df: pd.DataFrame, columna: str = "CODIGO_PROYECTO") -> pd.DataFrame:
    """Los códigos que aparecen más de una vez, con su conteo — para el detalle del tablero."""
    repetidos = df[df[columna].duplicated(keep=False)]
    resumen = (
        repetidos.groupby(columna)
        .size()
        .sort_values(ascending=False)
        .to_frame("filas")
    )
    resumen["contenido_distinto"] = (
        repetidos.groupby(columna)
        .apply(lambda g: g.drop(columns=["N"]).drop_duplicates().shape[0] > 1, include_groups=False)
    )
    return resumen
