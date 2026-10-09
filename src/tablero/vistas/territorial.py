"""Vista 1 — Panorama territorial: proyectos y montos por macrozona y región."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from tablero import estilo
from tablero.datos import agrupar, ordenar_por


def mostrar(df: pd.DataFrame, filtros: dict, meta: dict) -> None:
    st.subheader("Panorama territorial")
    st.caption(
        "Proyectos adjudicados por macrozona y región, con la unidad de conteo elegida a la vista."
    )

    medida = st.radio(
        "Unidad de conteo",
        options=["proyectos", "codigos", "filas"],
        format_func=lambda m: estilo.MEDIDAS[m],
        horizontal=True,
        key="territorial_medida",
    )
    if df.empty:
        st.info("Sin datos con los filtros actuales.")
        return

    por_macro = agrupar(
        df,
        ["macrozona"],
        {
            "filas": ("codigo_proyecto", "size"),
            "codigos": ("codigo_proyecto", "nunique"),
            "monto_clp": ("monto_clp", "sum"),
            "monto_clp_real": ("monto_clp_real", "sum"),
            "sin_monto": ("monto_valido", "size"),
        },
    )
    por_macro["proyectos"] = agrupar(
        df.assign(_par=df["codigo_proyecto"].astype(str) + "|" + df["anno_fallo"].astype(str)),
        ["macrozona"],
        {"p": ("_par", "nunique")},
    )["p"].to_numpy()
    por_macro = ordenar_por(por_macro, [medida], False)

    total = float(por_macro[medida].sum())
    monto = float(df.loc[df["monto_valido"], "monto_clp"].sum())
    monto_real = float(df.loc[df["monto_valido"], "monto_clp_real"].sum())
    sin_monto = int((~df["monto_valido"]).sum())
    sin_deflactor = int((df["monto_valido"] & df["monto_clp_real"].isna()).sum())

    columnas = st.columns(4)
    columnas[0].markdown(
        estilo.tarjeta("Selección actual", estilo.numero(total), estilo.UNIDADES[medida]),
        unsafe_allow_html=True,
    )
    columnas[1].markdown(
        estilo.tarjeta("Monto nominal", estilo.pesos(monto), "pesos de cada año"),
        unsafe_allow_html=True,
    )
    columnas[2].markdown(
        estilo.tarjeta("Monto real", estilo.pesos(monto_real, real=True), f"base {meta['deflactores']['base']}"),
        unsafe_allow_html=True,
    )
    columnas[3].markdown(
        estilo.tarjeta("Filas sin monto", estilo.numero(sin_monto), "no suman al monto"),
        unsafe_allow_html=True,
    )

    if sin_deflactor:
        st.markdown(
            estilo.aviso(
                f"**{estilo.numero(sin_deflactor)} filas** con monto no tienen IPC del año "
                "(2026 no tiene índice anual cerrado): entran al nominal y **no** al real."
            ),
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("#### Por macrozona")
    etiquetas = [f"{m}" for m in por_macro["macrozona"]]
    datos_grafico = pd.DataFrame({estilo.MEDIDAS[medida]: por_macro[medida].to_numpy()}, index=etiquetas)
    st.bar_chart(datos_grafico, horizontal=True, color=estilo.COLOR["primario"])

    st.markdown("#### Por región")
    por_region = agrupar(
        df,
        ["region", "macrozona"],
        {
            "filas": ("codigo_proyecto", "size"),
            "codigos": ("codigo_proyecto", "nunique"),
            "monto_clp": ("monto_clp", "sum"),
            "monto_clp_real": ("monto_clp_real", "sum"),
        },
    )
    por_region["proyectos"] = agrupar(
        df.assign(_par=df["codigo_proyecto"].astype(str) + "|" + df["anno_fallo"].astype(str)),
        ["region", "macrozona"],
        {"p": ("_par", "nunique")},
    )["p"].to_numpy()
    por_region = ordenar_por(por_region, [medida], False)
    tabla = pd.DataFrame(
        {
            "Región": por_region["region"],
            "Macrozona": por_region["macrozona"],
            estilo.MEDIDAS[medida].capitalize(): por_region[medida].to_numpy(),
            "Monto nominal (pesos)": por_region["monto_clp"].round(0).to_numpy(),
            "Monto real (pesos del año base)": por_region["monto_clp_real"].round(0).to_numpy(),
        }
    )
    st.dataframe(
        tabla,
        hide_index=True,
        width="stretch",
        column_config={
            estilo.MEDIDAS[medida].capitalize(): st.column_config.NumberColumn(format="%d"),
            "Monto nominal (pesos)": st.column_config.NumberColumn(format="%.0f"),
            "Monto real (pesos del año base)": st.column_config.NumberColumn(format="%.0f"),
        },
    )
    st.caption(
        f"La tabla muestra sólo el **{estilo.MEDIDAS[medida]}** en su columna numérica: "
        "cambiar la unidad arriba cambia la columna, no el filtro."
    )
