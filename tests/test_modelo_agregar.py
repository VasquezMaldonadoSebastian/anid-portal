"""Tests de `modelo.agregar` y del contrato de `modelo.exportar._agregar`.

Estos tests fijan el punto que este entorno rompe de forma intermitente: que la agregación
no dependa de resolver etiquetas después del `groupby`. Ver el docstring de `modelo.agregar`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from homologacion.moneda import a_pesos, es_notacion_cientifica
from modelo.agregar import agrupar, ordenar_por
from modelo.exportar import MEDIDAS, _agregar

# ---------------------------------------------------------------- agrupar


def test_agrupar_cuenta_y_suma_por_grupo():
    df = pd.DataFrame(
        {
            "region": ["A", "A", "B", "B", "B"],
            "anno": [2020, 2020, 2020, 2021, 2021],
            "codigo": ["P1", "P1", "P2", "P3", "P3"],
            "monto": [10, 20, 5, 1, 2],
        }
    )
    out = agrupar(
        df,
        ["region", "anno"],
        {"filas": ("codigo", "size"), "codigos": ("codigo", "nunique"), "monto": ("monto", "sum")},
    )
    assert list(out.columns) == ["region", "anno", "filas", "codigos", "monto"]
    assert out["filas"].sum() == len(df)
    # (A, 2020): 2 filas pero un solo código → la unidad de conteo tiene que verse
    primera = out.iloc[0].to_dict()
    if primera["region"] == "A":
        assert primera["filas"] == 2 and primera["codigos"] == 1 and primera["monto"] == 30
    assert out["monto"].sum() == 38
    assert out["codigos"].sum() == 3


def test_agrupar_una_sola_clave_devuelve_columna_simple():
    df = pd.DataFrame({"region": ["A", "B", "A"], "monto": [1, 2, 3]})
    out = agrupar(df, ["region"], {"filas": ("monto", "size"), "monto": ("monto", "sum")})
    assert list(out.columns) == ["region", "filas", "monto"]
    assert out.set_index("region")["monto"].to_dict() == {"A": 4, "B": 2}


def test_agrupar_conserva_nulos_y_ordena_por_aparicion():
    # dropna=False: una región nula es un grupo, no un descarte silencioso
    df = pd.DataFrame({"region": [None, "A", None], "monto": [1, 2, 4]})
    out = agrupar(df, ["region"], {"filas": ("monto", "size"), "monto": ("monto", "sum")})
    assert out["filas"].sum() == 3
    assert out.iloc[0]["monto"] == 5  # el grupo nulo aparece primero, como en los datos
    assert bool(out.iloc[0]["region"] is None) or pd.isna(out.iloc[0]["region"])


def test_agrupar_funcion_desconocida_falla():
    df = pd.DataFrame({"region": ["A"], "monto": [1]})
    with pytest.raises(ValueError, match="no soportada"):
        agrupar(df, ["region"], {"x": ("monto", "moda")})


# ---------------------------------------------------------------- ordenar_por


def test_ordenar_por_descendente_numerico():
    df = pd.DataFrame({"anno": [2019, 2021, 2020], "n": [1, 2, 3]})
    assert ordenar_por(df, ["anno"], False)["anno"].tolist() == [2021, 2020, 2019]


def test_ordenar_por_dos_claves_direcciones_distintas():
    df = pd.DataFrame({"anno": [2020, 2021, 2020, 2021], "n": [1, 1, 9, 9]})
    out = ordenar_por(df, ["anno", "n"], [False, False])
    assert list(zip(out["anno"], out["n"], strict=True)) == [(2021, 9), (2021, 1), (2020, 9), (2020, 1)]


def test_ordenar_por_texto_descendente():
    df = pd.DataFrame({"region": ["A", "B", "C"], "n": [3, 1, 2]})
    assert ordenar_por(df, ["region"], False)["region"].tolist() == ["C", "B", "A"]


def test_ordenar_por_reinicia_el_indice():
    df = pd.DataFrame({"n": [3, 1, 2]})
    assert ordenar_por(df, ["n"], True).index.tolist() == [0, 1, 2]


def test_ordenar_por_direcciones_incompletas_falla():
    df = pd.DataFrame({"n": [3, 1, 2], "m": [1, 2, 3]})
    with pytest.raises(ValueError, match="tantas direcciones"):
        ordenar_por(df, ["n", "m"], [False])


# ---------------------------------------------------------------- _agregar (contrato)


def _hecho():
    """4 filas que cubren todos los casos: con monto, sin monto, euros, y 2026 sin IPC."""
    return pd.DataFrame(
        {
            "region": ["METROPOLITANA", "METROPOLITANA", "BIOBIO", "BIOBIO"],
            "anno_fallo": [2020, 2020, 2025, 2026],
            "codigo_proyecto": ["P1", "P1", "P2", "P3"],
            "monto_clp": [100.0, 0.0, 50.0, 70.0],
            "monto_valido": [True, False, True, True],
            "monto_clp_real": [80.0, np.nan, 50.0, np.nan],  # 2026 no tiene deflactor
        }
    )


def test_agregar_respeta_el_contrato_de_columnas():
    out = _agregar(_hecho(), ["region", "anno_fallo"])
    assert list(out.columns) == ["region", "anno_fallo", *MEDIDAS]


def test_agregar_no_pierde_filas_y_avisa_de_lo_que_no_suma():
    hecho = _hecho()
    out = _agregar(hecho, ["region", "anno_fallo"])
    assert out["filas"].sum() == len(hecho)
    assert int(out["filas_sin_monto"].sum()) == 1
    assert int(out["filas_sin_deflactor"].sum()) == 1
    # el monto suma sólo lo válido, y el real deja fuera la fila 2026 sin IPC
    assert float(out["monto_clp"].sum()) == 220.0
    assert float(out["monto_clp_real"].sum()) == 130.0


def test_agregar_cuenta_proyectos_por_par_codigo_anio():
    out = _agregar(_hecho(), ["region"])
    # 4 filas, pero P1 está dos veces en METROPOLITANA → 3 códigos distintos (P1, P2, P3)
    assert out["filas"].sum() == 4
    assert out["codigos"].sum() == 3
    # y (P1, 2020) es un solo proyecto aunque ocupe dos filas
    assert out["proyectos"].sum() == 3
    assert out.set_index("region")["filas"].to_dict() == {"METROPOLITANA": 2, "BIOBIO": 2}


# ---------------------------------------------------------------- hallazgos de la auditoría (2026-10-09)

def test_notacion_cientifica_se_interpreta_tal_cual():
    """'2E+05' son 200.000 miles de pesos, no 205: el re.sub dejaba '205' y publicaba $205.000."""
    assert a_pesos("2E+05", "MILES DE PESOS (M$)") == 200_000_000.0
    assert es_notacion_cientifica("2E+05")
    assert es_notacion_cientifica("1.5e+07")
    assert not es_notacion_cientifica("227.497")
    assert not es_notacion_cientifica("NO SOLICITA A CONICYT")
    # los montos normales siguen leyéndose igual (con los rótulos reales de la base)
    assert a_pesos("58.191", "M$") == 58_191_000.0
    assert a_pesos("227.497,14", "MILES DE PESOS (M$)") == 227_497_140.0


def test_agregar_suma_distingue_cero_de_sin_dato():
    """Un grupo con todos los valores nulos suma nulo, no 0: si no, 2026 mostraba «0 pesos reales»."""
    df = pd.DataFrame(
        {
            "grupo": ["b", "a", "a"],
            "valor": pd.array([None, 1.0, 2.0], dtype="Float64"),
        }
    )
    out = agrupar(df, ["grupo"], {"total": ("valor", "sum")})
    por_grupo = dict(zip(out["grupo"].tolist(), out["total"].tolist(), strict=True))
    assert por_grupo["a"] == 3.0
    assert por_grupo["b"] != por_grupo["b"]  # nulo, no 0.0


def test_medida_global_no_cuenta_dos_veces_un_par():
    """El total de una selección se mide directo; sumar los grupos cuenta doble un proyecto multirregión."""
    from tablero.datos import medida_global

    df = pd.DataFrame(
        {
            "codigo_proyecto": ["P1", "P1", "P2"],
            "anno_fallo": pd.array([2005, 2005, 2010], dtype="Int64"),
            "macrozona": ["NORTE", "SUR", "NORTE"],
        }
    )
    assert medida_global(df, "filas") == 3
    assert medida_global(df, "codigos") == 2
    assert medida_global(df, "proyectos") == 2  # P1|2005 aparece en dos macrozonas: un solo par
    # la suma de los grupos sí lo cuenta dos veces: por eso el total no se suma desde los grupos
    assert int(df.groupby("macrozona")["codigo_proyecto"].count().sum()) == 3
