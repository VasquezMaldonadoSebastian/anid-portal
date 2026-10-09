"""Mide las cifras de control de la Fase 1 con el código de homologación ya escrito.

Salida: docs/evidencia/cuadre-homologacion.md (y la misma tabla por stdout).
No modifica datos: solo lee y cuenta.

Uso: py -3.11 scripts/cuadre_homologacion.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd  # noqa: E402

from homologacion import cargar  # noqa: E402
from homologacion.categorias import (  # noqa: E402
    homologar_sexo,
    homologar_tipo_beneficiario,
)
from homologacion.institucion import (  # noqa: E402
    normalizar_nombre,
    normalizar_rut,
    reporte_colisiones,
)
from homologacion.macrozona import CONTROL_HISTORICO, macrozona_de_region, verificar_macrozona  # noqa: E402
from homologacion.metricas import (  # noqa: E402
    codigos_repetidos,
    contar_codigos,
    contar_filas,
    contar_proyectos,
)
from homologacion.moneda import normalizar_montos, rotulo_moneda  # noqa: E402
from homologacion.region import NO_CLASIFICADO, homologar_region, no_clasificados  # noqa: E402
from homologacion.roles import homologar_rol, no_clasificados as roles_no_clasificados  # noqa: E402
from homologacion.subdireccion import homologar_subdireccion  # noqa: E402

DESTINO = RAIZ / "docs" / "evidencia" / "cuadre-homologacion.md"
lineas: list[str] = []


def p(texto: str = "") -> None:
    print(texto)
    lineas.append(texto)


def main() -> int:
    h = cargar("historico")
    bc = cargar("becas")
    ci = cargar("instituciones")
    po = cargar("postulaciones")

    p("# Cuadre de la homologación (Fase 1)")
    p()
    p(f"**Generado por** `scripts/cuadre_homologacion.py` · **Filas de entrada:** "
      f"histórico {len(h):,} · becas {len(bc):,} · colaboración {len(ci):,} · postulaciones {len(po):,}".replace(",", "."))
    p()

    # --- H1 región ---
    p("## H1 — Región")
    reg = h["REGION_EJECUCION"].map(homologar_region)
    p(f"- filas: {len(h)} · sin clasificar: {int((reg == NO_CLASIFICADO).sum())} · "
      f"etiquetas crudas: {h['REGION_EJECUCION'].nunique()} → destinos: {reg.nunique()}")
    p(f"- METROPOLITANA: **{int((reg == 'METROPOLITANA').sum())}** (crudo con la etiqueta más usada: 26.334)")
    p(f"- NUBLE: {int((reg == 'NUBLE').sum())} · OHIGGINS: {int((reg == 'OHIGGINS').sum())} · "
      f"MAGALLANES: {int((reg == 'MAGALLANES').sum())} · AYSEN: {int((reg == 'AYSEN').sum())}")
    p(f"- sin clasificar en histórico: {no_clasificados(h['REGION_EJECUCION']) or 'ninguna'}")
    for nombre, df in (("becas", bc), ("colaboración", ci), ("postulaciones", po)):
        col = "REGION_DE_ORIGEN" if nombre == "becas" else ("REGIONINSTITUCION" if nombre == "colaboración" else "REGION_EJECUCION")
        mapa = df[col].map(homologar_region)
        p(f"- {nombre} ({col}): sin clasificar {int((mapa == NO_CLASIFICADO).sum())} · "
          f"valores pendientes: {no_clasificados(df[col]) or 'ninguno'}")
    p()

    # --- H2 macrozona ---
    p("## H2 — Macrozona derivada")
    for nombre, df, col in (
        ("histórico", h, "REGION_EJECUCION"),
        ("becas", bc, "REGION_DE_ORIGEN"),
        ("postulaciones", po, "REGION_EJECUCION"),
    ):
        exc = verificar_macrozona(df, region=col)
        p(f"- {nombre}: excepciones contra el archivo = **{len(exc)}** de {len(df)} filas")
        if len(exc):
            p(f"  - detalle: {exc[col].value_counts().to_dict()}")
    suma = h["REGION_EJECUCION"].map(homologar_region).map(macrozona_de_region).value_counts()
    for mz, esperado in CONTROL_HISTORICO.items():
        obtenido = int(suma.get(mz, 0))
        marca = "OK" if obtenido == esperado else "DESVÍO"
        p(f"- {mz}: esperado {esperado} · obtenido {obtenido} → {marca}")
    p()

    # --- H3 moneda ---
    p("## H3 — Moneda y monto")
    hm = normalizar_montos(h)
    conteo = hm["moneda_homologada"].value_counts().to_dict()
    p(f"- rótulos homologados: {conteo}")
    p(f"- sin monto (monto_clp nulo): **{int((~hm['monto_valido']).sum())}** de {len(hm)}")
    p(f"- en euros: {int((hm['moneda_homologada'] == 'EUROS').sum())} filas · monto_eur suma {hm['monto_eur'].sum():,.0f}".replace(",", "."))
    hm["anno"] = pd.to_numeric(hm["AGNO_FALLO"], errors="coerce")
    w = hm[(hm["anno"].between(2020, 2025)) & hm["monto_valido"]]
    total = w["monto_clp"].sum()
    p(f"- 2020-2025, sólo pesos con monto ({len(w)} de {int(hm['anno'].between(2020, 2025).sum())} filas del período): "
      f"**${total / 1e6:,.0f} millones**".replace(",", "."))
    p("- por macrozona:")
    t = (
        w.assign(mz=w["REGION_EJECUCION"].map(homologar_region).map(macrozona_de_region))
        .groupby("mz")["monto_clp"]
        .agg(filas="count", clp="sum")
        .sort_values("clp", ascending=False)
    )
    for mz, fila in t.iterrows():
        p(f"  - {mz}: {int(fila['filas'])} filas · ${fila['clp'] / 1e6:,.0f} millones".replace(",", "."))
    p()

    # --- H4 subdirección ---
    p("## H4 — Subdirección")
    sd = h["SUBDIRECCION"].map(homologar_subdireccion)
    p(f"- histórico: {h['SUBDIRECCION'].nunique()} rótulos → {sd.nunique()} destinos · sin clasificar {int((sd == 'NO CLASIFICADO').sum())}")
    for k, v in sd.value_counts().items():
        p(f"  - {k}: {v}")
    p()

    # --- H5 categorías ---
    p("## H5 — Tipo de beneficiario y sexo")
    tb = h["TIPO_BENEFICIARIO"].map(homologar_tipo_beneficiario)
    p(f"- tipo beneficiario: {h['TIPO_BENEFICIARIO'].nunique()} rótulos → {tb.nunique()} · {tb.value_counts().to_dict()}")
    sx = bc["SEXO"].map(homologar_sexo)
    p(f"- sexo en becas: {bc['SEXO'].nunique()} rótulos → {sx.nunique()} · {sx.value_counts().to_dict()}")
    p()

    # --- H6 institución ---
    p("## H6 — Institución")
    p(f"- histórico: {h['INSTITUCION_PRINCIPAL'].nunique()} nombres → {h['INSTITUCION_PRINCIPAL'].map(normalizar_nombre).nunique()} normalizados")
    p(f"- colaboración: {ci['INSTITUCION1ERNIVEL'].nunique()} nombres → {ci['INSTITUCION1ERNIVEL'].map(normalizar_nombre).nunique()} normalizados · "
      f"RUT {ci['RUTINSTITUCION'].map(normalizar_rut).nunique()} válidos de {ci['RUTINSTITUCION'].nunique()} crudos")
    col = reporte_colisiones(ci, "INSTITUCION1ERNIVEL", "RUTINSTITUCION")
    p(f"- RUT con más de un nombre: **{len(col['rut_con_varios_nombres'])}** · nombres con más de un RUT: **{len(col['nombre_con_varios_rut'])}**")

    # tabla de decisiones para el usuario (no se resuelve automáticamente)
    DESTINO_COL = RAIZ / "docs" / "evidencia" / "instituciones-colisiones.md"
    rc = col["rut_con_varios_nombres"]
    rn = col["nombre_con_varios_rut"]
    lineas_col = [
        "# Colisiones de la clave institucional (Colaboración)",
        "",
        "Contadas **sólo sobre RUT válidos**: un campo vacío, un guion o el literal `SIN INFORMACION`",
        "no son identificadores, y tratarlos como tales inventa colisiones.",
        "",
        f"**{len(rc)} RUT con más de un nombre** · **{len(rn)} nombres con más de un RUT** · {ci['RUTINSTITUCION'].map(normalizar_rut).nunique()} RUT válidos.",
        "",
        "## RUT con más de un nombre (top 25)",
        "",
        "| RUT | Nombres declarados | N° |",
        "|---|---|---|",
    ]
    for _, f in rc.head(25).iterrows():
        nombres_escapados = str(f["nombres"]).replace("|", "·")
        lineas_col.append(f"| `{f['_rut']}` | {nombres_escapados} | {int(f['n_nombres'])} |")
    lineas_col += [
        "",
        "## Nombres con más de un RUT (todos)",
        "",
        "| Nombre | RUT declarados | N° |",
        "|---|---|---|",
    ]
    for _, f in rn.iterrows():
        lineas_col.append(f"| {f['_nombre']} | `{f['ruts']}` | {int(f['n_ruts'])} |")
    lineas_col += [
        "",
        "## Decisión pendiente del usuario",
        "",
        "Estas colisiones **no se resuelven solas**: qué nombre es el correcto (y si un RUT repetido es un",
        "error de la fuente) lo decide quien conoce las instituciones. El modelo usa el RUT como clave cuando",
        "existe y deja el nombre como etiqueta visible, así que un cambio de decisión no obliga a rehacer el ETL.",
    ]
    DESTINO_COL.write_text("\n".join(lineas_col) + "\n", encoding="utf-8")
    print(f"Escrito: {DESTINO_COL}")
    p()

    # --- H7 roles ---
    p("## H7 — Rol institucional")
    rl = ci["ROLINSTITUCION"].map(homologar_rol)
    p(f"- 65 rótulos crudos → {rl.nunique()} canónicos · sin clasificar: **{int((rl == 'NO CLASIFICADO').sum())}** filas")
    for k, v in rl.value_counts().items():
        p(f"  - {k}: {v}")
    pend = roles_no_clasificados(ci["ROLINSTITUCION"])
    if pend:
        p(f"- valores pendientes (decisión del usuario): {pend}")
    p()

    # --- H8 unidad de conteo ---
    p("## H8 — Unidad de conteo")
    p(f"- histórico: filas {contar_filas(h)} · códigos {contar_codigos(h)} · "
      f"pares (código, año) {contar_proyectos(h)}")
    rep = codigos_repetidos(h)
    p(f"- códigos repetidos: {len(rep)} (con contenido distinto entre sus filas: {int(rep['contenido_distinto'].sum())})")
    p(f"- postulaciones: filas {contar_filas(po)} · códigos {contar_codigos(po)}")

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\nEscrito: {DESTINO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
