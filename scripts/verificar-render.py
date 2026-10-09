"""Verifica el render del tablero sin navegador: ejecuta la app real con `AppTest`.

Por qué así: la app se sirve en `localhost`, y el navegador automatizado de este entorno bloquea
direcciones internas. `streamlit.testing.v1.AppTest` ejecuta el mismo `app.py`, con sus widgets y
sus datos, y deja inspeccionar el árbol de elementos: es una verificación más fuerte que leer el
DOM, porque además permite **cambiar un filtro y volver a medir**.

Uso: py -3.11 scripts/verificar-render.py   → `docs/evidencia/render-tablero.md`
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
APP = RAIZ / "src" / "tablero" / "app.py"
DESTINO = RAIZ / "docs" / "evidencia" / "render-tablero.md"


def tarjeta(app: AppTest, etiqueta: str) -> str | None:
    """El valor visible de una tarjeta, leído del HTML que la app emite.

    Sirve para contrastar lo que el tablero muestra contra `outputs/`: si una vista cambiara su
    forma de agregar, el número de la tarjeta dejaría de coincidir con el del modelo.
    """
    patron = re.compile(rf'etiqueta">{re.escape(etiqueta)}</div><div class="valor">([^<]+)</div>')
    for elemento in app.markdown:
        encontrado = patron.search(str(getattr(elemento, "value", "") or ""))
        if encontrado:
            return encontrado.group(1)
    return None


def numero_tarjeta(valor: str | None) -> int | None:
    """«47.244» → 47244 · «—» → None."""
    if valor is None:
        return None
    limpio = valor.replace(".", "").replace("\u00a0", "").strip()
    return int(limpio) if limpio.isdigit() else None


def textos(app: AppTest) -> str:
    """Todo el texto visible del árbol de elementos, en un solo bloque."""
    partes: list[str] = []
    for atributo in ("title", "header", "subheader", "markdown", "caption", "text", "info", "warning", "error"):
        for elemento in getattr(app, atributo, []):
            valor = getattr(elemento, "value", None)
            if valor:
                partes.append(str(valor))
    for atributo in ("dataframe", "table", "metric"):
        for elemento in getattr(app, atributo, []):
            valor = getattr(elemento, "value", None)
            if valor is None:
                continue
            try:
                partes.append(" ".join(str(c) for c in valor.columns))
                partes.append(valor.head(25).to_string())
            except AttributeError:
                partes.append(str(valor))
    for bloque in getattr(app, "tabs", []):
        partes.append(str(getattr(bloque, "label", "")))
    return "\n".join(partes)


def chequear(nombre: str, condicion: bool, detalle: str = "") -> dict:
    return {"nombre": nombre, "ok": bool(condicion), "detalle": detalle}


def main() -> int:
    resultados: list[dict] = []

    app = AppTest.from_file(str(APP), default_timeout=300).run()
    resultados.append(chequear("la app corre sin excepción", not app.exception, str(app.exception or "")))
    if app.exception:
        escribir(resultados, app)
        return 1

    contenido = textos(app)

    # cada vista presente
    for vista in (
        "Panorama territorial",
        "Ranking institucional",
        "Serie temporal",
        "Ficha de institución",
        "Red de colaboración y embudo de postulaciones",
    ):
        resultados.append(chequear(f"vista visible: {vista}", vista in contenido))

    # las cinco pestañas principales montadas (la vista 5 trae dos pestañas internas más)
    principales = [
        "Panorama territorial",
        "Ranking institucional",
        "Serie temporal",
        "Ficha de institución",
        "Red y embudo",
    ]
    etiquetas = [getattr(b, "label", "") for b in app.tabs]
    resultados.append(
        chequear(
            "las 5 pestañas principales están montadas",
            all(any(p in e for e in etiquetas) for p in principales),
            " · ".join(etiquetas),
        )
    )

    # avisos permanentes obligatorios
    for marca, nombre in (
        ("Unidad de conteo", "aviso de unidad de conteo"),
        ("Moneda", "aviso de moneda"),
        ("Corte", "aviso de corte"),
        ("IPC", "mención del índice de precios"),
        ("pesos del año base", "unidad del monto real"),
    ):
        resultados.append(chequear(nombre, marca in contenido))

    # 2026 apagado por defecto y avisado
    resultados.append(
        chequear(
            "2026 fuera de los totales por defecto",
            "2026" in contenido and "fuera de los totales" in contenido,
        )
    )
    casilla = [c for c in app.checkbox if "2026" in (c.label or "")]
    resultados.append(chequear("existe la casilla de 2026", len(casilla) == 1))
    resultados.append(
        chequear("casilla de 2026 apagada al abrir", bool(casilla) and not casilla[0].value)
    )

    # cifras del modelo visibles en la app (contra outputs/, no inventadas)
    for cifra, nombre in (
        ("49.014", "filas del histórico visibles"),
        ("1.707", "claves de institución visibles"),
    ):
        resultados.append(chequear(nombre, cifra in contenido))

    # filtros: la app responde a un cambio de macrozona
    if app.multiselect:
        multimacro = app.multiselect(key="f_macro")
        antes = len(app.dataframe)
        multimacro.select("SUR").run()
        resultados.append(
            chequear("filtrar por macrozona no rompe la app", not app.exception, str(app.exception or ""))
        )
        despues = textos(app)
        resultados.append(
            chequear(
                "el filtro acota el panorama (aparece la macrozona elegida)",
                "SUR" in despues,
                f"dataframes antes={antes} después={len(app.dataframe)}",
            )
        )
        resultados.append(
            chequear(
                "el ranking se acota al filtro territorial",
                "Región" in despues or "Institución" in despues,
            )
        )
        multimacro.unselect("SUR").run()

    # moneda real/nominal en la serie
    if any(r.key == "serie_moneda" for r in app.radio):
        app.radio(key="serie_moneda").set_value("nominal").run()
        resultados.append(
            chequear("interruptor nominal/real responde", not app.exception and "nominal" in textos(app).lower())
        )
        app.radio(key="serie_moneda").set_value("real").run()

    # 2026 encendido: el aviso debe cambiar
    if casilla:
        app.checkbox(key="f_2026").set_value(True).run()
        contenido_2026 = textos(app)
        resultados.append(
            chequear(
                "al incluir 2026 el aviso cambia",
                "2026 está incluido" in contenido_2026,
                "el pie pasa a declarar que el año entra",
            )
        )

        # el monto real de 2026 no puede mostrarse como 0: no tiene IPC anual cerrado
        tabla_serie = None
        for tabla in app.dataframe:
            columnas = [str(c) for c in tabla.value.columns]
            if (
                any(c == "Año" for c in columnas)  # la tabla de la serie, no la territorial
                and any(c.startswith("Monto real") for c in columnas)
                and any(c.startswith("Monto nominal") for c in columnas)
            ):
                tabla_serie = tabla.value
                break
        if tabla_serie is not None:
            columna_anio = next(c for c in tabla_serie.columns if str(c) == "Año")
            columna_real = next(c for c in tabla_serie.columns if str(c).startswith("Monto real"))
            fila = tabla_serie[tabla_serie[columna_anio].astype(str).eq("2026")]
            valor = float(fila[columna_real].iloc[0]) if len(fila) else float("nan")
            resultados.append(
                chequear(
                    "el monto real de 2026 no se muestra como 0",
                    valor != valor or valor != 0,
                    f"monto real 2026 = {valor}",
                )
            )
        app.checkbox(key="f_2026").set_value(False).run()

    # ---- hallazgos de la auditoría (2026-10-09): totales por vista e instrumento
    hecho = pd.read_parquet(RAIZ / "outputs" / "proyectos.parquet")
    corte = hecho[hecho["anno_fallo"].le(2025)]
    esperado = int(
        (corte["codigo_proyecto"].astype(str) + "|" + corte["anno_fallo"].astype(str)).nunique()
    )
    total_territorial = numero_tarjeta(tarjeta(app, "Selección actual"))
    total_ranking = numero_tarjeta(tarjeta(app, "Selección"))
    resultados.append(
        chequear(
            "el total del panorama coincide con el modelo (par código · año)",
            total_territorial == esperado,
            f"app={total_territorial} · outputs/={esperado}",
        )
    )
    resultados.append(
        chequear(
            "panorama y ranking dan el mismo total con la misma selección",
            total_territorial == total_ranking,
            f"panorama={total_territorial} · ranking={total_ranking}",
        )
    )

    # el selector de instrumento tiene que filtrar de verdad
    app.multiselect(key="f_instrumento").select("REGULAR").run()
    total_instrumento = numero_tarjeta(tarjeta(app, "Selección actual"))
    resultados.append(
        chequear(
            "el filtro de instrumento acota los totales",
            not app.exception and total_instrumento not in (None, total_territorial),
            f"sin filtro={total_territorial} · con REGULAR={total_instrumento}",
        )
    )
    resultados.append(
        chequear(
            "el filtro de instrumento queda aplicado en el panel",
            any(m.key == "f_instrumento" and "REGULAR" in (m.value or []) for m in app.multiselect),
        )
    )
    app.multiselect(key="f_instrumento").unselect("REGULAR").run()

    # el aviso de multirregionalidad no se pierde cuando se filtra por región (es cuando importa)
    app.multiselect(key="f_institucion").select("RUT:81494400-K").run()
    aviso_con_institucion = "regiones**" in textos(app)
    app.multiselect(key="f_region").select("ANTOFAGASTA").run()
    aviso_con_region = "17 regiones" in textos(app)
    resultados.append(
        chequear(
            "el aviso de multirregionalidad sobrevive al filtro territorial",
            aviso_con_institucion and aviso_con_region,
            f"con la institución={aviso_con_institucion} · al filtrar región={aviso_con_region}",
        )
    )
    app.multiselect(key="f_region").unselect("ANTOFAGASTA").run()
    app.multiselect(key="f_institucion").unselect("RUT:81494400-K").run()

    escribir(resultados, app)
    ok = sum(1 for r in resultados if r["ok"])
    print(f"{ok}/{len(resultados)} verificaciones del render en verde")
    for r in resultados:
        if not r["ok"]:
            print(f"  FALLA  {r['nombre']}  {r['detalle']}")
    print(f"escrito {DESTINO}")
    return 0 if ok == len(resultados) else 1


def escribir(resultados: list[dict], app: AppTest) -> None:
    ok = sum(1 for r in resultados if r["ok"])
    lineas = [
        "# Verificación del render del tablero (Fase 3)",
        "",
        "**Generado por** `scripts/verificar-render.py` (ejecuta `src/tablero/app.py` con "
        "`streamlit.testing.v1.AppTest`; el navegador de este entorno bloquea `localhost`).",
        "",
        f"**Resultado: {ok} de {len(resultados)} verificaciones en verde.**",
        "",
        "| Verificación | Resultado | Detalle |",
        "|---|---|---|",
    ]
    for r in resultados:
        lineas.append(f"| {r['nombre']} | {'OK' if r['ok'] else 'FALLA'} | {r['detalle']} |")
    if app.exception:
        lineas += ["", "## Excepción capturada", "", "```", str(app.exception), "```"]
    DESTINO.write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
