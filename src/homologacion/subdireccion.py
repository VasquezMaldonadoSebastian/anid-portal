"""H4 — Subdirección: 7 rótulos crudos a las 5 reales (+ NO APLICA).

`REDES ESTRATEGIA Y CONOCIMIENTO` y `REDES, ESTRATEGIA Y CONOCIMIENTO` son la misma
área escrita de dos formas (la coma aparece desde 2020 y en Postulaciones es la
forma canónica). `NO APLICA` (2.484 filas, todo pre-2010) se mantiene como
categoría propia: no se reasigna a ninguna subdirección.
"""

from __future__ import annotations

import re
import unicodedata

SUBDIRECCIONES = (
    "CAPITAL HUMANO",
    "PROYECTOS DE INVESTIGACION",
    "CENTROS E INVESTIGACION ASOCIATIVA",
    "INVESTIGACION APLICADA",
    "REDES ESTRATEGIA Y CONOCIMIENTO",
)
NO_APLICA = "NO APLICA"
NO_CLASIFICADO = "NO CLASIFICADO"


def _norm(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    s = s.upper().replace(",", " ").replace("-", " ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


_EXACTAS = {
    _norm(v): v for v in SUBDIRECCIONES
}
_EXACTAS.update(
    {
        _norm("CAPITAL HUMANO"): "CAPITAL HUMANO",
        "SUBDIRECCION DE CENTROS E INVESTIGACION ASOCIATIVA": "CENTROS E INVESTIGACION ASOCIATIVA",
        NO_APLICA: NO_APLICA,
        "SIN INFORMACION": NO_CLASIFICADO,
    }
)

_REGLAS: tuple[tuple[str, str], ...] = (
    (r"^CAPITAL\s+HUMANO", "CAPITAL HUMANO"),
    (r"^PROYECTOS\s+DE\s+INVESTIGACION", "PROYECTOS DE INVESTIGACION"),
    (r"^CENTROS\s+E\s+INVESTIGACION", "CENTROS E INVESTIGACION ASOCIATIVA"),
    (r"^INVESTIGACION\s+APLICADA", "INVESTIGACION APLICADA"),
    (r"^REDES.*CONOCIMIENTO", "REDES ESTRATEGIA Y CONOCIMIENTO"),
)


def homologar_subdireccion(valor: str) -> str:
    s = _norm(valor)
    if not s:
        return NO_CLASIFICADO
    if s in _EXACTAS:
        return _EXACTAS[s]
    for patron, destino in _REGLAS:
        if re.match(patron, s):
            return destino
    return NO_CLASIFICADO
