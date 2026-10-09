"""Vista 4 — Ficha de institución: proyectos, montos, instrumentos y territorios."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from tablero import estilo
from tablero.datos import ficha_institucion


def mostrar(hecho: pd.DataFrame, filtros: dict, meta: dict) -> None:
    st.subheader("Ficha de institución")
    st.caption(
        "Una institución a la vez. Los montos de esta vista son **nominales** (pesos de cada año); "
        "la serie real está en la vista temporal."
    )
    if hecho.empty:
        st.info("Sin datos con los filtros actuales.")
        return

    nombres = (
        hecho[["institucion_clave", "institucion"]]
        .drop_duplicates()
        .sort_values("institucion")
    )
    opciones = nombres["institucion_clave"].tolist()
    etiqueta = dict(zip(nombres["institucion_clave"], nombres["institucion"], strict=True))
    primero = next(
        (c for c in opciones if c in set(filtros.get("instituciones") or [])),
        opciones[0],
    )
    elegida = st.selectbox(
        "Institución (por nombre declarado en el histórico)",
        options=opciones,
        index=opciones.index(primero),
        format_func=lambda c: f"{etiqueta[c]}  ·  {c}",
        key="ficha_institucion",
    )

    ficha = ficha_institucion(hecho, elegida)
    if not ficha:
        st.warning("La institución no tiene registros con los filtros actuales.")
        return

    columnas = st.columns(4)
    columnas[0].markdown(
        estilo.tarjeta("Proyectos", estilo.numero(ficha["codigos"]), "códigos distintos"),
        unsafe_allow_html=True,
    )
    columnas[1].markdown(
        estilo.tarjeta("Filas en el histórico", estilo.numero(ficha["filas"]), f"{ficha['anios'][0]}–{ficha['anios'][1]}"),
        unsafe_allow_html=True,
    )
    columnas[2].markdown(
        estilo.tarjeta("Monto adjudicado", estilo.pesos(ficha["monto_clp"]), "nominal, pesos de cada año"),
        unsafe_allow_html=True,
    )
    columnas[3].markdown(
        estilo.tarjeta("Regiones", estilo.numero(len(ficha["regiones"])), "donde ejecuta"),
        unsafe_allow_html=True,
    )

    if len(ficha["regiones"]) > 1:
        st.markdown(
            estilo.aviso(
                f"Esta institución ejecuta en **{len(ficha['regiones'])} regiones** "
                f"({', '.join(ficha['regiones'])}). El filtro territorial del panel opera sobre el "
                "**proyecto**, no sobre la institución: al filtrar por una región, los totales de "
                "esta ficha bajan."
            ),
            unsafe_allow_html=True,
        )
    if ficha["sin_monto"]:
        st.caption(
            f"{estilo.numero(ficha['sin_monto'])} de sus filas no tienen monto en pesos: no suman al monto."
        )
    if ficha["sin_deflactor"]:
        st.caption(
            f"{estilo.numero(ficha['sin_deflactor'])} filas con monto quedan fuera del monto real "
            "(año sin IPC cerrado)."
        )

    st.divider()
    izquierda, derecha = st.columns(2)
    with izquierda:
        st.markdown("#### Evolución anual")
        anios = ficha["por_anio"]
        st.bar_chart(
            pd.DataFrame(
                {"Códigos": anios["codigos"].to_numpy()},
                index=[str(int(a)) for a in anios["anno_fallo"]],
            ),
            color=estilo.COLOR["primario"],
        )
    with derecha:
        st.markdown("#### Instrumentos principales")
        instrumentos = ficha["por_instrumento"].head(12)
        st.bar_chart(
            pd.DataFrame(
                {"Códigos": instrumentos["codigos"].to_numpy()},
                index=[str(i) for i in instrumentos["instrumento"]],
            ),
            horizontal=True,
            color=estilo.COLOR["acento"],
        )

    st.markdown("#### Detalle por año")
    anios = ficha["por_anio"]
    st.dataframe(
        pd.DataFrame(
            {
                "Año": [int(a) for a in anios["anno_fallo"]],
                "Filas": anios["filas"].to_numpy(),
                "Códigos": anios["codigos"].to_numpy(),
            }
        ),
        hide_index=True,
        width="stretch",
    )
    st.caption(
        f"Macrozonas donde ejecuta: {', '.join(ficha['macrozonas']) or '—'}. "
        "La ficha usa el nombre tal como lo declara el histórico; la clave de la institución puede "
        "venir del RUT deducido del cruce con Colaboración."
    )
