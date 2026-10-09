"""ANID-Portal — tablero de la cartera de proyectos adjudicados por ANID.

Levantar:  py -3.11 -m streamlit run src/tablero/app.py

Consume el modelo curado (`outputs/`, Fase 2) y **no** lee los CSV crudos: si falta el modelo, la
app dice qué comando correr. Todas las tarjetas declaran su unidad de conteo, la fecha del corte
sale del manifiesto y las filas con fallo del año en curso entran apagadas por defecto.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

from tablero import datos, estilo  # noqa: E402
from tablero.vistas import ficha, institucional, red, serie, territorial  # noqa: E402

ANIO_SIN_IPC = 2026  # el año en curso no tiene IPC anual cerrado
HORAS_CHILE = timezone(timedelta(hours=-3))  # verano en Chile (UTC-3)


def anios_minimo(hecho) -> int:
    """Primer año con datos: el tablero no fija 1982 a mano, lo mide."""
    minimo = hecho["anno_fallo"].min()
    return int(minimo) if minimo == minimo else 1982


def barra_lateral(hecho, meta) -> dict:
    """Filtros globales en cascada: cada uno acota las opciones de los siguientes."""
    with st.sidebar:
        st.markdown("### Filtros")
        st.caption("Los filtros se aplican a todas las vistas salvo donde se indique lo contrario.")

        macrozonas = st.multiselect("Macrozona", datos.opciones(hecho, "macrozona"), key="f_macro")
        base_region = hecho
        if macrozonas:
            base_region = hecho[hecho["macrozona"].isin(macrozonas)]
        regiones = st.multiselect(
            "Región", datos.opciones(base_region, "region"), key="f_region"
        )

        base_sub = base_region
        if regiones:
            base_sub = base_region[base_region["region"].isin(regiones)]
        subdirecciones = st.multiselect(
            "Subdirección", datos.opciones(base_sub, "subdireccion"), key="f_subdir"
        )

        base_inst = base_sub
        if subdirecciones:
            base_inst = base_sub[base_sub["subdireccion"].isin(subdirecciones)]
        instituciones = st.multiselect(
            "Institución (opcional)",
            datos.opciones(base_inst, "institucion_clave"),
            format_func=lambda c: c.replace("RUT:", "").replace("NOMBRE:", ""),
            key="f_institucion",
        )

        instrumentos = st.multiselect(
            "Instrumento", datos.opciones(base_inst, "instrumento"), key="f_instrumento"
        )

        anios = datos.opciones(hecho, "anno_fallo")
        anio_min = int(anios[0]) if anios else 1982
        anio_max = int(anios[-1]) if anios else 2025
        desde, hasta = st.slider(
            "Años de fallo",
            anio_min,
            anio_max,
            (anio_min, min(anio_max, ANIO_SIN_IPC - 1)),
            help=f"El año {ANIO_SIN_IPC} no se incluye desde acá: se activa con la casilla de abajo.",
            key="f_anios",
        )

        incluir_actual = st.checkbox(
            f"Incluir {ANIO_SIN_IPC} (sin IPC cerrado)",
            value=False,
            help=(
                f"La base declara el corte en {ANIO_SIN_IPC - 1}, pero trae filas con año de fallo "
                f"{ANIO_SIN_IPC}: se pueden ver, pero no entran por defecto."
            ),
            key="f_2026",
        )
        if incluir_actual:
            # la casilla manda sobre el deslizador: si no, habría que mover los dos controles
            hasta = anio_max
            st.caption(f"La casilla manda sobre el deslizador: la selección llega hasta {anio_max}.")

        st.divider()
        st.caption(f"Corte de los datos: {meta['corte']['fecha']}")
        st.caption(f"Manifiesto sha256: `{meta['corte']['sha256_manifiesto'][:12]}…`")

    return {
        "macrozonas": macrozonas,
        "regiones": regiones,
        "subdirecciones": subdirecciones,
        "instituciones": instituciones,
        "instrumentos": instrumentos,
        "anios": (desde, hasta),
        "incluir_actual": incluir_actual,
    }


def pie(meta, hecho_filtrado, incluir_actual: bool, excluidas_actual: int) -> None:
    """Avisos permanentes: unidad de conteo, corte, moneda y año en curso."""
    avisos = [
        f"<b>Unidad de conteo:</b> cada tarjeta declara si cuenta filas, códigos o proyectos "
        f"(par código · año). En el histórico son distintos: {estilo.numero(meta['filas']['proyectos'])} "
        f"filas, 48.707 códigos.",
        f"<b>Moneda:</b> los montos nominales son pesos de cada año; los reales están en pesos de "
        f"{meta['deflactores']['base']} según IPC del {meta['deflactores']['fuente']}. "
        f"Cada monto dice cuál es.",
        f"<b>Corte:</b> {meta['corte']['fecha']} · manifiesto "
        f"{meta['corte']['sha256_manifiesto'][:12]}… · generado {meta['generado']}.",
    ]
    if excluidas_actual and not incluir_actual:
        avisos.append(
            f"<b>{ANIO_SIN_IPC}:</b> hay {estilo.numero(excluidas_actual)} filas con fallo {ANIO_SIN_IPC} "
            "que coinciden con los filtros, <b>fuera de los totales</b> porque el año no tiene IPC cerrado "
            f"y la base declara el corte en {ANIO_SIN_IPC - 1}. Activar la casilla del panel para incluirlas."
        )
    if incluir_actual:
        avisos.append(
            f"<b>{ANIO_SIN_IPC} está incluido.</b> Sus montos entran al nominal y quedan fuera del real."
        )
    for aviso in avisos:
        st.markdown(estilo.aviso(aviso), unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="ANID-Portal · cartera de proyectos adjudicados",
        page_icon="📊",
        layout="wide",
    )
    estilo.aplicar()

    st.title("Cartera de proyectos adjudicados por ANID")
    st.caption(
        "1982 → hoy, sobre los 8 repositorios públicos de ANID-GITHUB (CC0-1.0). "
        "Filtros por región, macrozona, institución, subdirección e instrumento."
    )

    try:
        meta = datos.cargar_meta()
        hecho = datos.cargar("proyectos")
    except datos.ModeloAusente as error:
        st.error(str(error))
        st.stop()

    filtros = barra_lateral(hecho, meta)
    hecho_filtrado = datos.filtrar(hecho, filtros)
    # Cuántas filas del año en curso quedan fuera: se cuentan sobre los mismos filtros pero sin el
    # rango de años, porque ese rango ya las excluye (si no, el aviso del pie nunca aparecería).
    con_anio_actual = datos.filtrar(hecho, {**filtros, "anios": (anios_minimo(hecho), ANIO_SIN_IPC)})
    excluidas_actual = int(con_anio_actual["anno_fallo"].eq(ANIO_SIN_IPC).sum())

    tabs = st.tabs(
        [
            "🗺️ Panorama territorial",
            "🏛️ Ranking institucional",
            "📈 Serie temporal",
            "🔎 Ficha de institución",
            "🕸️ Red y embudo",
        ]
    )
    with tabs[0]:
        territorial.mostrar(hecho_filtrado, filtros, meta)
    with tabs[1]:
        institucional.mostrar(hecho_filtrado, filtros, meta)
    with tabs[2]:
        serie.mostrar(hecho_filtrado, filtros, meta)
    with tabs[3]:
        ficha.mostrar(hecho_filtrado, filtros, meta)
    with tabs[4]:
        red.mostrar(filtros, meta)

    st.divider()
    pie(meta, hecho_filtrado, filtros["incluir_actual"], excluidas_actual)
    st.caption(
        f"Vista generada {datetime.now(HORAS_CHILE).strftime('%Y-%m-%d %H:%M')} (hora Chile). "
        "Las cifras salen del modelo curado en `outputs/`; los CSV crudos no se leen desde la app."
    )


main()
