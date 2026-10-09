"""Vista 2 — Ranking institucional, con la cola larga declarada (regla R8)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from tablero import estilo
from tablero.datos import agrupar, ordenar_por


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
        ["institucion_clave", "institucion"],
        {
            "filas": ("codigo_proyecto", "size"),
            "codigos": ("codigo_proyecto", "nunique"),
            "proyectos": ("_par", "nunique"),
            "monto_clp": ("monto_clp", "sum"),
            "monto_clp_real": ("monto_clp_real", "sum"),
        },
    )
    agg = ordenar_por(agg, [medida], False)

    visibles = agg.head(cuantas)
    resto = agg.tail(len(agg) - len(visibles))
    total = float(agg[medida].sum())

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
    concentracion = 100 * float(visibles[medida].sum()) / total if total else 0.0
    columnas[3].markdown(
        estilo.tarjeta(
            f"Concentración del top {len(visibles)}",
            f"{estilo.numero(concentracion, 1)}%",
            "del total seleccionado",
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
        "Colaboración; si no, del nombre normalizado. 21 nombres homónimos quedan en claves distintas."
    )
