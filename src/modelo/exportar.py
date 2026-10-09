"""Construye el modelo completo y lo deja en `outputs/` (CSV + Parquet) con sus metadatos.

Uso: py -3.11 scripts/construir-modelo.py

Salidas:
- `proyectos`, `colaboracion`, `postulaciones`, `becas`, `dim_institucion`, `tasa_region`
- `agg_region`, `agg_institucion`, `agg_programa` (agregados que consume el tablero)
- `_meta.json` con la fecha y el hash del corte, los conteos y la fuente de los deflactores

`outputs/` está fuera de git: es reproducible desde `data/crudo/` con este comando.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from homologacion.fuentes import cargar

from .agregar import agrupar
from .becas import construir_becas
from .colaboracion import construir_colaboracion
from .deflactores import cargar_deflactores
from .instituciones import construir_dim_institucion, mapa_nombre_a_rut
from .postulaciones import construir_postulaciones, tasa_global, tasa_por_region
from .proyectos import construir_proyectos

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "outputs"
MANIFIESTO = RAIZ / "data" / "crudo" / "_manifiesto.md"
CHILE = timezone(timedelta(hours=-3))

# columnas de agrupación y medidas de los agregados del tablero.
# `filas_sin_deflactor` no es adorno: son las filas con monto válido pero sin IPC del año
# (2026), que quedan fuera del total real. Si no se declaran, el total real miente por omisión.
MEDIDAS = [
    "filas",
    "codigos",
    "proyectos",
    "monto_clp",
    "monto_clp_real",
    "filas_sin_monto",
    "filas_sin_deflactor",
]


def _corte() -> dict[str, str]:
    """Fecha y hash del corte, leídos del manifiesto (no se inventan)."""
    if not MANIFIESTO.exists():
        return {"fecha": "desconocida", "sha256_manifiesto": None}
    texto = MANIFIESTO.read_text(encoding="utf-8")
    m = re.search(r"Fecha de descarga:\*\*\s*([^\n]+)", texto)
    return {
        "fecha": m.group(1).strip() if m else "desconocida",
        "sha256_manifiesto": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
    }


def _agregar(df: pd.DataFrame, claves: list[str]) -> pd.DataFrame:
    """Agrega el hecho por las claves dadas, con las medidas del tablero.

    Usa `modelo.agregar` (construcción por arrays, sin búsquedas por etiqueta después del
    groupby): ver el docstring de ese módulo para el porqué. `proyectos` es el par
    (código, año) distinto: se materializa `_par` y se cuenta con `nunique`.
    """
    d = df.copy()
    d["_par"] = d["codigo_proyecto"].astype(str) + "|" + d["anno_fallo"].astype(str)
    d["_monto"] = d["monto_clp"].where(d["monto_valido"], 0.0)
    d["_real"] = d["monto_clp_real"].where(d["monto_valido"])  # NaN si no hay deflactor
    d["_sin_monto"] = (~d["monto_valido"]).astype("int64")
    d["_sin_deflactor"] = (d["monto_valido"] & d["monto_clp_real"].isna()).astype("int64")

    agg = agrupar(
        d,
        claves,
        {
            "filas": ("codigo_proyecto", "size"),
            "codigos": ("codigo_proyecto", "nunique"),
            "proyectos": ("_par", "nunique"),
            "monto_clp": ("_monto", "sum"),
            "monto_clp_real": ("_real", "sum"),
            "filas_sin_monto": ("_sin_monto", "sum"),
            "filas_sin_deflactor": ("_sin_deflactor", "sum"),
        },
    )
    agg["monto_clp"] = agg["monto_clp"].round(0)
    agg["monto_clp_real"] = agg["monto_clp_real"].round(0)
    for columna in ("filas", "codigos", "proyectos", "filas_sin_monto", "filas_sin_deflactor"):
        agg[columna] = agg[columna].astype("int64")
    esperadas = [*claves, *MEDIDAS]
    if list(agg.columns) != esperadas:
        # un agregado con otro orden rompería al tablero en silencio: mejor fallar acá
        raise ValueError(f"columnas del agregado fuera de contrato: {list(agg.columns)} != {esperadas}")
    return agg


def _nombre_mas_frecuente(df: pd.DataFrame, clave: str, columna: str) -> pd.DataFrame:
    """Tabla `clave` → valor más frecuente de `columna`, sin pasar por etiquetas.

    Se itera el groupby y se cuenta con numpy: un `groupby(...)[col].agg(moda)` sería más
    corto y es justo el patrón que este entorno rompe.
    """
    posicion = df.columns.get_loc(columna)
    filas = []
    for valor_clave, grupo in df.groupby(clave, sort=False):
        valores = grupo.iloc[:, posicion].to_numpy()
        unicos, conteos = np.unique(valores, return_counts=True)
        filas.append((valor_clave, unicos[conteos.argmax()]))
    return pd.DataFrame(filas, columns=[clave, columna])


def construir_todo(destino: Path | None = None) -> dict:
    """Construye hechos, dimensión y agregados. Devuelve los metadatos del corte."""
    salida = destino or SALIDA
    salida.mkdir(parents=True, exist_ok=True)

    h = cargar("historico")
    ci = cargar("instituciones")
    po = cargar("postulaciones")
    bc = cargar("becas")

    deflactores = cargar_deflactores()
    mapa_rut = mapa_nombre_a_rut(ci)

    proyectos = construir_proyectos(h, deflactores, mapa_rut)
    colaboracion = construir_colaboracion(ci, mapa_rut)
    postulaciones = construir_postulaciones(po)
    becas = construir_becas(bc, mapa_rut)
    dim_institucion = construir_dim_institucion(h, ci)
    tasa_region = tasa_por_region(postulaciones)

    agg_region = _agregar(
        proyectos, ["region", "macrozona", "anno_fallo", "subdireccion"]
    )
    agg_institucion = _agregar(
        proyectos, ["institucion_clave", "anno_fallo", "region", "subdireccion"]
    )
    agg_programa = _agregar(
        proyectos, ["anno_fallo", "subdireccion", "programa", "instrumento"]
    )
    # nombres visibles para el ranking, sin repetir el nombre en cada fila del agregado
    nombres = _nombre_mas_frecuente(proyectos, "institucion_clave", "institucion")
    agg_institucion = agg_institucion.merge(nombres, on="institucion_clave", how="left")

    tablas = {
        "proyectos": proyectos,
        "colaboracion": colaboracion,
        "postulaciones": postulaciones,
        "becas": becas,
        "dim_institucion": dim_institucion,
        "tasa_region": tasa_region,
        "agg_region": agg_region,
        "agg_institucion": agg_institucion,
        "agg_programa": agg_programa,
    }

    conteos: dict[str, int] = {}
    for nombre, df in tablas.items():
        df.to_parquet(salida / f"{nombre}.parquet", index=False)
        df.to_csv(salida / f"{nombre}.csv", index=False, sep=";", encoding="utf-8-sig")
        conteos[nombre] = int(len(df))

    meta = {
        "generado": f"{datetime.now(CHILE):%Y-%m-%d %H:%M} (hora Chile)",
        "corte": _corte(),
        "deflactores": {
            "fuente": deflactores.fuente,
            "fecha_consulta": deflactores.fecha_consulta,
            "base": deflactores.base,
            "anios": [min(deflactores.anios), max(deflactores.anios)],
        },
        "filas": conteos,
        "hecho": {
            "filas": int(len(proyectos)),
            "codigos": int(proyectos["codigo_proyecto"].nunique()),
            "pares_codigo_anio": int(
                (proyectos["codigo_proyecto"].astype(str) + "|" + proyectos["anno_fallo"].astype(str)).nunique()
            ),
            "instituciones_clave": int(proyectos["institucion_clave"].nunique()),
            "instituciones_homonimas": int(tablas["dim_institucion"]["nombre_normalizado"].duplicated().sum()),
            "montos_en_notacion_cientifica": int(proyectos["monto_cientifico"].sum()),
        },
        "tasa_adjudicacion_proyectos": tasa_global(postulaciones),
        "notas": [
            "monto_clp es nominal; monto_clp_real está en pesos del año base de los deflactores.",
            "2026 no tiene IPC anual cerrado: sus montos reales son nulos (el año va apagado por defecto).",
            "filas ≠ codigos ≠ proyectos: cada tarjeta del tablero declara cuál usa.",
            "montos_en_notacion_cientifica: celdas de la fuente del tipo '2E+05' que se interpretan "
            "tal como están escritas; se cuentan para que la corrección sea auditable.",
        ],
    }
    (salida / "_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta
