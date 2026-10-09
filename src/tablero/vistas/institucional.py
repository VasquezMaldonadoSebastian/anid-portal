"""Vista 2 — Ranking institucional, con la cola larga declarada (regla R8)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from tablero import estilo
from tablero.datos import agrupar, medida_global, ordenar_por


def _nombre_visible(df: pd.DataFrame, claves) -> list[str]:
    """Un nombre por clave de institución: el que más filas aporta.

    41 claves traen más de un nombre declarado en el histórico. Agrupar por (clave, nombre) duplicaba
    filas del ranking —1.680 para 1.638 claves reales— y hacía que dos vistas mostraran totales
    distintos para la misma selección. Se resuelve con un conteo en Python, sin `groupby` por etiqueta.
    """
    conteo: dict[str, dict[str, int]] = {}
    for clave, nombre in zip(df["institucion_clave"].to_numpy(), df["institucion"].to_numpy(), strict=True):
        por_nombre = conteo.setdefault(clave, {})
        por_nombre[nombre] = por_nombre.get(nombre, 0) + 1
    return [
        max(conteo[c], key=conteo[c].get) if c in conteo else str(c)  # type: ignore[arg-type]
        for c in claves
    ]


def mostrar(df: pd.DataFrame, filtros: dict, meta: dict) -> None:
    st.subheader("Ranking institucional")
    st.caption(
        "Instituciones ordenadas por la unidad elegida. La última fila agrupa a las que quedan "
        "fuera del corte visible: ninguna desaparece en silencio."
    )
    if df.empty:
        st.info("Sin datos con los filtros actuales.")
        return

    izquierda, derecha = st.columns([1, 2])
    medida = izquierda.radio(
        "Unidad de conteo",
        options=["proyectos", "codigos", "filas"],
        format_func=lambda m: estilo.MEDIDAS[m],
        key="ranking_medida",
    )
    cuantas = derecha.slider("Instituciones visibles", 5, 50, 15, key="ranking_n")

    partes = df.assign(_par=df["codigo_proyecto"].astype(str) + "|" + df["anno_fallo"].astype(str))
    agg = agrupar(
        partes,
        ["institucion_clave"],
        {
            "filas": ("codigo_proyecto", "size"),
            "codigos": ("codigo_proyecto", "nunique"),
            "proyectos": ("_par", "nunique"),
            "monto_clp": ("monto_clp", "sum"),
            "monto_clp_real": ("monto_clp_real", "sum"),
        },
    )
    agg["institucion"] = _nombre_visible(df, agg["institucion_clave"])
    agg = ordenar_por(agg, [medida], False)

    visibles = agg.head(cuantas)
    resto = agg.tail(len(agg) - len(visibles))
    total = medida_global(df, medida)  # medido sobre la selección, no sumado desde los grupos
    reparto = float(agg[medida].sum())  # lo que reparten las instituciones (puede repetir un proyecto)

    columnas = st.columns(4)
    columnas[0].markdown(
        estilo.tarjeta("Selección", estilo.numero(total), estilo.UNIDADES[medida]),
        unsafe_allow_html=True,
    )
    columnas[1].markdown(
        estilo.tarjeta("Instituciones en la selección", estilo.numero(len(agg)), "claves distintas"),
        unsafe_allow_html=True,
    )
    columnas[2].markdown(
        estilo.tarjeta("Primera institución", estilo.numero(float(visibles[medida].iloc[0])), "de la selección"),
        unsafe_allow_html=True,
    )
    concentracion = 100 * float(visibles[medida].sum()) / reparto if reparto else 0.0
    columnas[3].markdown(
        estilo.tarjeta(
            f"Concentración del top {len(visibles)}",
            f"{estilo.numero(concentracion, 1)}%",
            "del reparto institucional",
        ),
        unsafe_allow_html=True,
    )

    if len(resto):
        partes_resto = resto[medida].sum()
        st.markdown(
            estilo.aviso(
                f"Quedan fuera del corte visible **{estilo.numero(len(resto))} instituciones** con "
                f"{estilo.numero(float(partes_resto))} {estilo.UNIDADES[medida]} "
                f"({estilo.numero(100 - concentracion, 1)}% de la selección). "
                "La cola larga es la mayoría del padrón: "
                f"{estilo.numero(100 * len(resto) / len(agg), 0)}% de las instituciones."
            ),
            unsafe_allow_html=True,
        )

    grafico = pd.DataFrame(
        {estilo.MEDIDAS[medida].capitalize(): visibles[medida].to_numpy()},
        index=[f"{n[:38]}…" if len(n) > 40 else n for n in visibles["institucion"].astype(str)],
    )
    st.bar_chart(grafico, horizontal=True, color=estilo.COLOR["primario"])

    tabla = pd.DataFrame(
        {
            "Institución": visibles["institucion"],
            estilo.MEDIDAS[medida].capitalize(): visibles[medida].to_numpy(),
            "Filas": visibles["filas"].to_numpy(),
            "Códigos": visibles["codigos"].to_numpy(),
            "Proyectos": visibles["proyectos"].to_numpy(),
            "Monto nominal (pesos)": visibles["monto_clp"].round(0).to_numpy(),
            "Monto real (pesos del año base)": visibles["monto_clp_real"].round(0).to_numpy(),
        }
    )
    st.dataframe(
        tabla,
        hide_index=True,
        width="stretch",
        column_config={
            "Monto nominal (pesos)": st.column_config.NumberColumn(format="%.0f"),
            "Monto real (pesos del año base)": st.column_config.NumberColumn(format="%.0f"),
        },
    )
    st.caption(
        "La clave de institución viene del RUT cuando el histórico permite deducirlo del cruce con "
        "Colaboración; si no, del nombre normalizado. "
        f"{estilo.numero(meta['hecho']['instituciones_homonimas'])} nombres homónimos quedan en claves distintas."
    )
    if round(reparto) != total:
        st.caption(
            f"El reparto por institución suma {estilo.numero(reparto)} y la selección son "
            f"{estilo.numero(total)} {estilo.UNIDADES[medida]}: un proyecto puede declararse con más de "
            "un nombre de institución, así que las instituciones reparten pero **no** totalizan."
        )
