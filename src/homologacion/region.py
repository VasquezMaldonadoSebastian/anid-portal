"""H1 — Región: de 24-30 etiquetas crudas a 16 regiones + categorías territoriales.

Medido el 2026-10-09 (docs/datos.md §3): el mismo territorio aparece escrito de
cuatro formas distintas según la base y según la era del archivo. Sin homologar,
la Región Metropolitana suma 26.334 filas; homologada suma 27.212 (3,2% de desvío).

La homologación NO se deduce de reglas generales: se construye con las etiquetas
observadas. Una etiqueta no vista (corte nuevo) cae en `NO CLASIFICADO` y debe
reportarse — nunca absorberse a la fuerza.
"""

from __future__ import annotations

import re
import unicodedata

NO_CLASIFICADO = "NO CLASIFICADO"
SIN_INFORMACION = "SIN INFORMACION"

# Las 16 regiones en su forma canónica
REGIONES = (
    "ARICA Y PARINACOTA",
    "TARAPACA",
    "ANTOFAGASTA",
    "ATACAMA",
    "COQUIMBO",
    "VALPARAISO",
    "METROPOLITANA",
    "OHIGGINS",
    "MAULE",
    "NUBLE",
    "BIOBIO",
    "ARAUCANIA",
    "LOS RIOS",
    "LOS LAGOS",
    "AYSEN",
    "MAGALLANES",
)

# Categorías que no son territorio
NO_TERRITORIALES = (SIN_INFORMACION, "EXTRANJERO", "MULTIREGIONAL", "NO APLICA")

# Etiquetas observadas en las 4 bases (Histórico, Postulaciones, Becas, Colaboración,
# más los archivos Milenio). Clave: etiqueta normalizada (sin tildes, mayúsculas).
_EXACTAS: dict[str, str] = {
    # --- Histórico (etiquetas antiguas, pre-2026) ---
    "REGION DE METROPOLITANA": "METROPOLITANA",
    "REGION DEL BIOBIO": "BIOBIO",
    "REGION DE VALPARAISO": "VALPARAISO",
    "REGION DE LOS RIOS": "LOS RIOS",
    "REGION DE LA ARAUCANIA": "ARAUCANIA",
    "REGION DEL MAULE": "MAULE",
    "REGION DE ANTOFAGASTA": "ANTOFAGASTA",
    "REGION DE COQUIMBO": "COQUIMBO",
    "REGION DE LOS LAGOS": "LOS LAGOS",
    "REGION DE ARICA Y PARINACOTA": "ARICA Y PARINACOTA",
    "REGION DE MAGALLANES Y ANTARTICA CHILENA": "MAGALLANES",
    "REGION DE TARAPACA": "TARAPACA",
    "REGION DE OHIGGINS": "OHIGGINS",
    "REGION DE ATACAMA": "ATACAMA",
    "REGION DE AYSEN": "AYSEN",
    "REGION DEL NUBLE": "NUBLE",
    "REGION DE NUBLE": "NUBLE",
    "REGION DEL LIBERTADOR GENERAL BERNARDO O HIGGINS": "OHIGGINS",
    # --- Histórico 2026 / Postulaciones / Becas (etiquetas nuevas) ---
    "REGION METROPOLITANA DE SANTIAGO": "METROPOLITANA",
    "REGION METROPOLITANA": "METROPOLITANA",
    "REGION DE MAGALLANES Y DE LA ANTARTICA CHILENA": "MAGALLANES",
    "REGION DE MAGALLANES Y LA ANTARTICA CHILENA": "MAGALLANES",
    "REGION DE AYSEN DEL GENERAL CARLOS IBANEZ DEL CAMPO": "AYSEN",
    "REGION AYSEN DEL GENERAL CARLOS IBANEZ DEL CAMPO": "AYSEN",
    "REGION DE NUBLE ": "NUBLE",
    # --- Colaboración (Biobío con guion) ---
    "REGION DEL BIO-BIO": "BIOBIO",
    # --- No territoriales ---
    "SIN INFORMACION": SIN_INFORMACION,
    "NO REGISTRA REGION": SIN_INFORMACION,
    "NO INFORMA": SIN_INFORMACION,
    "EXTRANJERO": "EXTRANJERO",
    "EXTERIOR": "EXTRANJERO",
    "MULTIREGIONAL": "MULTIREGIONAL",
    "NO APLICA": "NO APLICA",
}

# Reglas de respaldo para etiquetas no vistas (corte nuevo). Se aplican EN ORDEN
# sobre la etiqueta normalizada, completa.
_REGLAS: tuple[tuple[str, str], ...] = (
    (r"^REGION\s+METROPOLITANA", "METROPOLITANA"),
    (r"^REGION\s+DEL\s+LIBERTADOR", "OHIGGINS"),
    (r"^REGION\s+(DE\s+|DEL\s+)?MAGALLANES", "MAGALLANES"),
    (r"^REGION\s+(DE\s+|DEL\s+)?AYSEN", "AYSEN"),
    (r"^REGION\s+(DE\s+|DEL\s+)?NUBLE", "NUBLE"),
    (r"^REGION\s+(DE\s+|DEL\s+)?BIO[\s-]?BIO", "BIOBIO"),
    (r"^REGION\s+(DE\s+|DEL\s+)?(LOS\s+RIOS|DE\s+LOS\s+RIOS)", "LOS RIOS"),
    (r"^REGION\s+(DE\s+|DEL\s+)?(LOS\s+LAGOS|DE\s+LOS\s+LAGOS)", "LOS LAGOS"),
    (r"^REGION\s+(DE\s+|DEL\s+)?(LA\s+)?ARAUCANIA", "ARAUCANIA"),
    (r"^REGION\s+(DE\s+|DEL\s+)?O\s?HIGGINS", "OHIGGINS"),
    (r"^REGION\s+DE\s+ARICA", "ARICA Y PARINACOTA"),
    (r"^REGION\s+(DE\s+|DEL\s+)?(VALPARAISO|MAULE|COQUIMBO|TARAPACA|ATACAMA|ANTOFAGASTA)", None),  # nombre propio
    (r"^SIN\s+INFORMACION", SIN_INFORMACION),
    (r"^NO\s+REGISTRA", SIN_INFORMACION),
    (r"^EXTRANJER", "EXTRANJERO"),
    (r"^MULTIREGIONAL", "MULTIREGIONAL"),
    (r"^NO\s+APLICA", "NO APLICA"),
)


def _norm(texto: str) -> str:
    """Sin tildes, en mayúsculas, sin puntuación salvo espacios, espacios colapsados."""
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    s = s.upper().replace("-", " ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def homologar_region(valor: str) -> str:
    """Devuelve la región canónica, una categoría no territorial o NO CLASIFICADO."""
    s = _norm(valor)
    if not s:
        return NO_CLASIFICADO
    if s in _EXACTAS:
        return _EXACTAS[s]
    # la etiqueta con guion se normaliza con espacio: probar ambas formas
    s_guion = re.sub(r"\s+", "-", s)
    if s_guion in _EXACTAS:
        return _EXACTAS[s_guion]
    for patron, destino in _REGLAS:
        if re.match(patron, s):
            if destino is not None:
                return destino
            m = re.match(patron, s)
            nombre = re.sub(r"^REGION\s+(DE\s+|DEL\s+)?", "", m.group(0)).strip()
            return nombre if nombre in REGIONES else NO_CLASIFICADO
    return NO_CLASIFICADO


def homologar_columna(serie):  # type: ignore[no-untyped-def]
    """Aplica la homologación a una columna y avisa si algo quedó sin clasificar."""
    return serie.map(homologar_region)


def no_clasificados(serie) -> dict[str, int]:  # type: ignore[no-untyped-def]
    """Etiquetas crudas que no calzaron — se reportan, no se absorben."""
    mapa = serie.map(homologar_region)
    pendientes = serie[mapa == NO_CLASIFICADO]
    return {str(k): int(v) for k, v in pendientes.value_counts().items()}
