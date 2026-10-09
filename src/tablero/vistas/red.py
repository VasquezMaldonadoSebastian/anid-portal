"""Vista 5 — Red de colaboración y embudo de postulaciones."""

from __future__ import annotations

from itertools import combinations

import pandas as pd
import streamlit as st

from tablero import estilo
from tablero.datos import agrupar, cargar, filtrar, ordenar_por

MAX_SOCIOS_POR_PROYECTO = 60  # un proyecto con más instituciones que esto no aporta pares legibles


def _pares(colaboracion: pd.DataFrame) -> pd.DataFrame:
    """Cuenta pares de instituciones que coinciden en un mismo proyecto."""
    conteo: dict[tuple[str, str], int] = {}
    for _, grupo in colaboracion.groupby("codigo_proyecto", sort=False):
        socios = sorted(set(grupo["institucion_clave"].dropna().tolist()))
        if not (2 <= len(socios) <= MAX_SOCIOS_POR_PROYECTO):
            continue
        for a, b in combinations(socios, 2):
            conteo[(a, b)] = conteo.get((a, b), 0) + 1
    if not conteo:
        return pd.DataFrame(columns=["institucion_a", "institucion_b", "proyectos"])
    return pd.DataFrame(
        [(a, b, n) for (a, b), n in conteo.items()], columns=["institucion_a", "institucion_b", "proyectos"]
    )


def _nombres(colaboracion: pd.DataFrame) -> dict[str, str]:
    """Nombre más frecuente por clave, contado con numpy (sin `groupby` + etiqueta)."""
    nombres: dict[str, str] = {}
    for clave, grupo in colaboracion.groupby("institucion_clave", sort=False):
        valores = grupo["institucion"].dropna().to_numpy()
        if not len(valores):
            continue
        unicos = pd.unique(valores)
        conteos = [int((valores == u).sum()) for u in unicos]
        nombres[clave] = str(unicos[int(pd.Series(conteos).to_numpy().argmax())])
    return nombres


def mostrar(filtros: dict, meta: dict) -> None:
    st.subheader("Red de colaboración y embudo de postulaciones")
    izquierda, derecha = st.tabs(["Red de colaboración", "Embudo de postulaciones"])

    with izquierda:
        colaboracion = cargar("colaboracion")
        colaboracion = filtrar(colaboracion, filtros, columnas=("anno_fallo",))
        if colaboracion.empty:
            st.info("Sin datos de colaboración con los filtros actuales.")
        else:
            proyectos = colaboracion["codigo_proyecto"].nunique()
            instituciones = colaboracion["institucion_clave"].nunique()
            pares = _pares(colaboracion)
            columnas = st.columns(3)
            columnas[0].markdown(
                estilo.tarjeta("Proyectos con colaboración", estilo.numero(proyectos), "códigos distintos"),
                unsafe_allow_html=True,
            )
            columnas[1].markdown(
                estilo.tarjeta("Instituciones participantes", estilo.numero(instituciones), "claves distintas"),
                unsafe_allow_html=True,
            )
            columnas[2].markdown(
                estilo.tarjeta("Pares que coinciden", estilo.numero(len(pares)), "pares de instituciones"),
                unsafe_allow_html=True,
            )
            st.markdown(
                estilo.aviso(
                    "La región y la macrozona de esta base son las de la **institución**, no las del "
                    "proyecto. Por eso el filtro territorial del panel no se aplica acá: sólo el año de fallo."
                ),
                unsafe_allow_html=True,
            )
            if pares.empty:
                st.info("Ningún proyecto de la selección tiene dos o más instituciones.")
            else:
                nombres = _nombres(colaboracion)
                pares = ordenar_por(pares, ["proyectos"], False).head(25)
                tabla = pd.DataFrame(
                    {
                        "Institución A": [nombres.get(c, c) for c in pares["institucion_a"]],
                        "Institución B": [nombres.get(c, c) for c in pares["institucion_b"]],
                        "Proyectos en común": pares["proyectos"].to_numpy(),
                    }
                )
                st.markdown("#### Pares con más proyectos en común")
                st.dataframe(tabla, hide_index=True, width="stretch")

                socios = pd.concat(
                    [
                        pares.rename(columns={"institucion_a": "clave"})[["clave", "proyectos"]],
                        pares.rename(columns={"institucion_b": "clave"})[["clave", "proyectos"]],
                    ]
                )
                grado = agrupar(socios, ["clave"], {"pares": ("proyectos", "size"), "proyectos": ("proyectos", "sum")})
                grado = ordenar_por(grado, ["pares"], False).head(15)
                st.markdown("#### Instituciones con más socios distintos")
                st.bar_chart(
                    pd.DataFrame(
                        {"Pares distintos": grado["pares"].to_numpy()},
                        index=[nombres.get(c, c) for c in grado["clave"]],
                    ),
                    horizontal=True,
                    color=estilo.COLOR["acento"],
                )

    with derecha:
        postulaciones = cargar("postulaciones")
        postulaciones = filtrar(postulaciones, filtros, columnas=("region", "macrozona", "anno_fallo"))
        if postulaciones.empty:
            st.info("Sin postulaciones con los filtros actuales.")
            return

        por_estado = agrupar(
            postulaciones, ["estado"], {"filas": ("codigo_proyecto", "size"), "codigos": ("codigo_proyecto", "nunique")}
        )
        por_estado = ordenar_por(por_estado, ["filas"], False)
        columnas = st.columns(3)
        columnas[0].markdown(
            estilo.tarjeta("Postulaciones", estilo.numero(int(por_estado["filas"].sum())), "filas"),
            unsafe_allow_html=True,
        )
        columnas[1].markdown(
            estilo.tarjeta("Adjudicadas", estilo.numero(int(postulaciones["adjudicado"].sum())), "filas"),
            unsafe_allow_html=True,
        )
        tasa = 100 * float(postulaciones["adjudicado"].mean()) if len(postulaciones) else 0.0
        columnas[2].markdown(
            estilo.tarjeta("Tasa de adjudicación", f"{estilo.numero(tasa, 1)}%", "sobre todas las postulaciones"),
            unsafe_allow_html=True,
        )
        st.markdown(
            estilo.aviso(
                "Esta tasa mezcla proyectos y Capital Humano, y cuenta también las postulaciones "
                "**fuera de base**. La tasa limpia es la de la tabla de abajo: sólo proyectos y sólo "
                "el estado adjudicado contra lo postulado."
            ),
            unsafe_allow_html=True,
        )

        st.markdown("#### Estado de las postulaciones")
        st.dataframe(
            pd.DataFrame(
                {
                    "Estado": por_estado["estado"],
                    "Filas": por_estado["filas"].to_numpy(),
                    "Códigos": por_estado["codigos"].to_numpy(),
                }
            ),
            hide_index=True,
            width="stretch",
        )

        tasa_region = cargar("tasa_region")
        tasa_region = filtrar(tasa_region, filtros, columnas=("region", "macrozona", "anno_fallo"))
        st.markdown("#### Tasa de adjudicación por región (sólo proyectos)")
        if tasa_region.empty:
            st.info("Sin tasa calculable con los filtros actuales.")
        else:
            resumen = agrupar(
                tasa_region,
                ["region", "macrozona"],
                {"postulaciones": ("postulaciones", "sum"), "adjudicadas": ("adjudicadas", "sum")},
            )
            resumen["tasa"] = (100 * resumen["adjudicadas"] / resumen["postulaciones"]).round(1)
            resumen = ordenar_por(resumen, ["tasa"], False)
            st.dataframe(
                pd.DataFrame(
                    {
                        "Región": resumen["region"],
                        "Macrozona": resumen["macrozona"],
                        "Postulaciones": resumen["postulaciones"].to_numpy(),
                        "Adjudicadas": resumen["adjudicadas"].to_numpy(),
                        "Tasa (%)": resumen["tasa"].to_numpy(),
                    }
                ),
                hide_index=True,
                width="stretch",
            )
            st.caption(
                "No existe tasa por institución: la base de postulaciones no identifica institución y "
                "las no adjudicadas no la traen en ninguna otra base."
            )
