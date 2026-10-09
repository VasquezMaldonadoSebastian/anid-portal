"""Identidad visual del tablero: un solo lugar para colores, formatos y avisos.

Regla del proyecto: **ninguna vista define colores ni formatos a mano**. Todo sale de acá, para
que el tablero se vea igual en las cinco vistas y para poder cambiarlo en un sitio.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------- tokens

COLOR = {
    "tinta": "#0F172A",  # texto principal
    "tinta_suave": "#475569",  # texto secundario
    "borde": "#E2E8F0",
    "fondo": "#F8FAFC",
    "superficie": "#FFFFFF",
    "primario": "#00539B",  # azul institucional
    "acento": "#00A0DF",
    "alerta": "#B45309",  # avisos de alcance (unidad, moneda, corte)
    "aviso_fondo": "#FFFBEB",  # fondo de los avisos: token, no literal en el CSS
    "ok": "#047857",
    "serie": ["#00539B", "#00A0DF", "#7C3AED", "#B45309", "#047857", "#64748B"],
}

TIPOGRAFIA = {
    "familia": '"Segoe UI", "Inter", system-ui, -apple-system, sans-serif',
    "titulo": "1.6rem",
    "subtitulo": "1.05rem",
    "cuerpo": "0.95rem",
    "menudo": "0.8rem",
}

UNIDADES = {
    "filas": "filas",
    "codigos": "códigos",
    "proyectos": "proyectos",
}

MEDIDAS = {
    "filas": "filas",
    "codigos": "códigos de proyecto",
    "proyectos": "proyectos (par código · año)",
}

_COLOR_SERIE = "color"
_CSS = f"""
<style>
  .stApp {{ background: {COLOR["fondo"]}; font-family: {TIPOGRAFIA["familia"]}; }}
  h1, h2, h3, h4 {{ color: {COLOR["tinta"]}; font-family: {TIPOGRAFIA["familia"]}; }}
  h1 {{ font-size: {TIPOGRAFIA["titulo"]}; }}
  h3 {{ font-size: {TIPOGRAFIA["subtitulo"]}; }}
  .anid-tarjeta {{
      background: {COLOR["superficie"]}; border: 1px solid {COLOR["borde"]};
      border-radius: 10px; padding: 0.9rem 1rem; height: 100%;
  }}
  .anid-tarjeta .etiqueta {{
      color: {COLOR["tinta_suave"]}; font-size: {TIPOGRAFIA["menudo"]};
      text-transform: uppercase; letter-spacing: 0.04em;
  }}
  .anid-tarjeta .valor {{
      color: {COLOR["tinta"]}; font-size: 1.5rem; font-weight: 600; line-height: 1.2;
  }}
  .anid-tarjeta .unidad {{ color: {COLOR["tinta_suave"]}; font-size: {TIPOGRAFIA["menudo"]}; }}
  .anid-aviso {{
      background: {COLOR["aviso_fondo"]}; border-left: 4px solid {COLOR["alerta"]};
      padding: 0.6rem 0.9rem; border-radius: 6px; color: {COLOR["tinta"]};
      font-size: {TIPOGRAFIA["cuerpo"]};
  }}
  .anid-pie {{ color: {COLOR["tinta_suave"]}; font-size: {TIPOGRAFIA["menudo"]}; }}
</style>
"""


def aplicar() -> None:
    """Inyecta los tokens en la página. Se llama una vez, al principio de `app.py`."""
    st.markdown(_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- formato chileno


def numero(valor: float | int | None, decimales: int = 0) -> str:
    """Formatea con separador de miles chileno. Los nulos se muestran como «—», no como 0."""
    if valor is None or (isinstance(valor, float) and valor != valor):
        return "—"
    formateado = f"{valor:,.{decimales}f}"
    return formateado.replace(",", "\u00a0").replace(".", ",").replace("\u00a0", ".")


def pesos(valor: float | None, real: bool = False) -> str | None:
    """Monto grande en una unidad legible, sin esconder cuál es."""
    if valor is None or valor != valor:
        return "—"
    etiqueta = "pesos del año base" if real else "pesos"
    if abs(valor) >= 1_000_000_000:
        return f"${numero(valor / 1_000_000_000, 1)} mil millones ({etiqueta})"
    if abs(valor) >= 1_000_000:
        return f"${numero(valor / 1_000_000, 1)} millones ({etiqueta})"
    return f"${numero(valor, 0)} ({etiqueta})"


def tarjeta(etiqueta: str, valor: str, unidad: str = "") -> str:
    """Tarjeta con la unidad SIEMPRE visible: es la regla R8/H8 del proyecto."""
    sufijo = f'<div class="unidad">{unidad}</div>' if unidad else ""
    return (
        f'<div class="anid-tarjeta"><div class="etiqueta">{etiqueta}</div>'
        f'<div class="valor">{valor}</div>{sufijo}</div>'
    )


def aviso(texto: str) -> str:
    return f'<div class="anid-aviso">{texto}</div>'
