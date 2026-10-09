"""Vista 3 — Serie temporal por año, con interruptor nominal/real."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from tablero import estilo
from tablero.datos import agrupar, ordenar_por


def mostrar(df: pd.DataFrame, filtros: dict, meta: dict) -> None:
    st.subheader("Serie temporal")
    st.caption(
        "Montos por año de fallo. El nominal es la suma de pesos de cada año; el real lleva todo a "
        f"pesos de {meta['deflactores']['base']} con el IPC anual de Chile."
    )
    if df.empty:
        st.info("Sin datos con los filtros actuales.")
        return

    izquierda, derecha = st.columns([1, 1])
    medida = izquierda.radio(
        "Unidad de conteo",
        options=["proyectos", "codigos", "filas"],
        format_func=lambda m: estilo.MEDIDAS[m],
        key="serie_medida",
    )
    unidad_monto = derecha.radio(
        "Moneda",
        options=["real", "nominal"],
        format_func=lambda m: (
            f"Real (pesos de {meta['deflactores']['base']})" if m == "real" else "Nominal (pesos de cada año)"
        ),
        key="serie_moneda",
    )

    partes = df.assign(_par=df["codigo_proyecto"].astype(str) + "|" + df["anno_fallo"].astype(str))
    por_anio = agrupar(
        partes,
        ["anno_fallo"],
        {
            "filas": ("codigo_proyecto", "size"),
            "codigos": ("codigo_proyecto", "nunique"),
            "proyectos": ("_par", "nunique"),
            "monto_clp": ("monto_clp", "sum"),
            "monto_clp_real": ("monto_clp_real", "sum"),
            "sin_deflactor": ("monto_clp_real", "size"),
        },
    )
    por_anio = ordenar_por(por_anio, ["anno_fallo"], True)

    columna_monto = "monto_clp_real" if unidad_monto == "real" else "monto_clp"
    etiqueta_monto = (
        f"Monto real (pesos de {meta['deflactores']['base']})"
        if unidad_monto == "real"
        else "Monto nominal (pesos del año)"
    )

    grafico = pd.DataFrame(
        {
            estilo.MEDIDAS[medida].capitalize(): por_anio[medida].to_numpy(),
            etiqueta_monto: por_anio[columna_monto].round(0).to_numpy(),
        },
        index=[str(a) for a in por_anio["anno_fallo"]],
    )
    st.bar_chart(grafico, color=[estilo.COLOR["primario"], estilo.COLOR["acento"]])

    sin_ipc = por_anio.loc[por_anio[columna_monto].isna(), "anno_fallo"]
    if unidad_monto == "real" and len(sin_ipc):
        st.markdown(
            estilo.aviso(
                "Años sin monto real: "
                + ", ".join(str(int(a)) for a in sin_ipc)
                + ". No hay IPC anual cerrado para el año en curso, y esos montos **no se imputan** "
                "(quedan fuera del real y dentro del nominal)."
            ),
            unsafe_allow_html=True,
        )

    ultimo = por_anio.iloc[-1]
    columnas = st.columns(3)
    columnas[0].markdown(
        estilo.tarjeta("Último año de la selección", str(int(ultimo["anno_fallo"])), "año de fallo"),
        unsafe_allow_html=True,
    )
    columnas[1].markdown(
        estilo.tarjeta(
            f"{estilo.MEDIDAS[medida].capitalize()} en {int(ultimo['anno_fallo'])}",
            estilo.numero(float(ultimo[medida])),
            estilo.UNIDADES[medida],
        ),
        unsafe_allow_html=True,
    )
    columnas[2].markdown(
        estilo.tarjeta("Años en la selección", estilo.numero(len(por_anio)), "desde 1982"),
        unsafe_allow_html=True,
    )

    tabla = pd.DataFrame(
        {
            "Año": [int(a) for a in por_anio["anno_fallo"]],
            estilo.MEDIDAS[medida].capitalize(): por_anio[medida].to_numpy(),
            "Filas": por_anio["filas"].to_numpy(),
            "Códigos": por_anio["codigos"].to_numpy(),
            "Proyectos": por_anio["proyectos"].to_numpy(),
            "Monto nominal (pesos)": por_anio["monto_clp"].round(0).to_numpy(),
            f"Monto real (pesos de {meta['deflactores']['base']})": por_anio["monto_clp_real"].round(0).to_numpy(),
        }
    )
    st.dataframe(
        tabla,
        hide_index=True,
        width="stretch",
        column_config={
            "Monto nominal (pesos)": st.column_config.NumberColumn(format="%.0f"),
            f"Monto real (pesos de {meta['deflactores']['base']})": st.column_config.NumberColumn(format="%.0f"),
        },
    )
    st.caption(
        f"Deflactores: {meta['deflactores']['fuente']} · base {meta['deflactores']['base']} · "
        f"consulta {meta['deflactores']['fecha_consulta']}."
    )
