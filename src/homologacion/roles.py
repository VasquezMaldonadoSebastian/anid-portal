"""H7 — Rol institucional: 65 valores crudos a ~8 canónicos.

Los roles del campo `ROLINSTITUCION` (Colaboración) no son un vocabulario
controlado: cada concurso declaró el suyo. El orden de las reglas importa —
`INSTITUCION NACIONAL PATROCINANTE ASOCIADA` contiene dos roles y se clasifica por
el más fuerte, y todo lo que dice EXTRANJERA se marca como tal porque es la
distinción que importa en un tablero chileno.

Lo que no calce queda en `NO CLASIFICADO` y se reporta con su conteo y sus valores.
"""

from __future__ import annotations

import re
import unicodedata

BENEFICIARIA = "BENEFICIARIA / PRINCIPAL"
PATROCINANTE = "PATROCINANTE"
ASOCIADA = "ASOCIADA / PARTICIPANTE"
APORTANTE = "APORTANTE / COFINANCIAMIENTO"
EXTRANJERA = "EXTRANJERA"
POSTULANTE = "POSTULANTE"
ALBERGANTE = "ALBERGANTE / PROCEDENCIA"
OTRA = "OTRA ENTIDAD"
NO_APLICA = "NO APLICA"
NO_CLASIFICADO = "NO CLASIFICADO"

ROLES_CANONICOS = (
    BENEFICIARIA,
    PATROCINANTE,
    ASOCIADA,
    APORTANTE,
    EXTRANJERA,
    POSTULANTE,
    ALBERGANTE,
    OTRA,
    NO_APLICA,
)

# Se aplican EN ORDEN: el primero que calza gana.
_REGLAS: tuple[tuple[str, str], ...] = (
    (r"NO\s+APLICA", NO_APLICA),
    # lo extranjero primero: distingue el rol útil para un tablero chileno
    (r"EXTRANJER|DE\s+FRANCIA|CHINA|DEL\s+PERU|SUDAMERICAN|COLABORACION\s+INTERNACIONAL", EXTRANJERA),
    # responsable publica/privada: es la institución a cargo, la distinción público/privado
    # se conserva en el valor crudo (queda en el detalle), no cambia el rol
    (r"RESPONSABLE\s+(PUBLICA|PRIVADA)", BENEFICIARIA),
    # principal / beneficiaria
    (r"(PRINCIPAL|BENEFICIARIA)\b.*|.*\bBENEFICIARIA\s*$", BENEFICIARIA),
    (r"^BENEFICIARIA", BENEFICIARIA),
    (r"CENTRO\s+BENEFICIARIO", BENEFICIARIA),
    (r"^INSTITUCIONES\s+CO\s+EJECUTORAS", ASOCIADA),
    (r"PATROCINANTE", PATROCINANTE),
    (r"ASOCIAD|SECUNDARIA|COLABORADORA|PARTICIPANTE|CO\s+EJECUTOR", ASOCIADA),
    (r"APORTANTE|CO\s+FINANCIAMIENTO|INTERESADA|MANDANTE", APORTANTE),
    (r"POSTULANTE|SOLICITANTE", POSTULANTE),
    (r"ALBERGANTE|PROCEDENCIA", ALBERGANTE),
    (r"UNIVERSIDAD|EMPRESA|PYME|CENTRO|PERSONA\s+NATURAL|TERCERO", OTRA),
)


def _norm(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    s = s.upper().replace("/", " ").replace("-", " ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def homologar_rol(valor: str) -> str:
    s = _norm(valor)
    if not s:
        return NO_CLASIFICADO
    for patron, destino in _REGLAS:
        if re.search(patron, s):
            return destino
    return NO_CLASIFICADO


def no_clasificados(serie) -> dict[str, int]:  # type: ignore[no-untyped-def]
    """Valores crudos de rol que no calzaron con ninguna regla."""
    mapa = serie.map(homologar_rol)
    pendientes = serie[mapa == NO_CLASIFICADO]
    return {str(k): int(v) for k, v in pendientes.value_counts().items()}
