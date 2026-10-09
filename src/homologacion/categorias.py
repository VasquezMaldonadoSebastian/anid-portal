"""H5 — Tipo de beneficiario y sexo.

Tipo de beneficiario (histórico): 6 rótulos para 3 categorías reales. Las
combinaciones (`PERSONA NATURAL O PERSONA JURIDICA` 46, `NATURAL O JURIDICA` 15,
`JURIDICA` 7) NO se reparten en silencio: van a la categoría mixta declarada
`NATURAL O JURIDICA`, que es lo que el dato dice.

Sexo: las bases usan `HOMBRE`/`MUJER` y, en Becas, además `FEMENINO` (739) y
`MASCULINO` (689). Se homologan a `MUJER`/`HOMBRE`; nada más se toca.
"""

from __future__ import annotations

import re
import unicodedata

TIPO_NATURAL = "PERSONA NATURAL"
TIPO_JURIDICA = "PERSONA JURIDICA"
TIPO_MIXTA = "NATURAL O JURIDICA"
SIN_INFORMACION = "SIN INFORMACION"
NO_CLASIFICADO = "NO CLASIFICADO"

HOMBRE = "HOMBRE"
MUJER = "MUJER"


def _norm(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    s = s.upper().replace("/", " ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def homologar_tipo_beneficiario(valor: str) -> str:
    s = _norm(valor)
    if not s or s.startswith("SIN INFORMACION"):
        return SIN_INFORMACION if s else NO_CLASIFICADO
    tiene_natural = "NATURAL" in s
    tiene_juridica = "JURIDICA" in s
    if tiene_natural and tiene_juridica:
        return TIPO_MIXTA
    if tiene_natural:
        return TIPO_NATURAL
    if tiene_juridica:
        return TIPO_JURIDICA
    return NO_CLASIFICADO


def homologar_sexo(valor: str) -> str:
    s = _norm(valor)
    if not s or s.startswith("SIN INFORMACION"):
        return SIN_INFORMACION if s else NO_CLASIFICADO
    if s in {HOMBRE, "MASCULINO", "HOMBRES"}:
        return HOMBRE
    if s in {MUJER, "FEMENINO", "MUJERES"}:
        return MUJER
    # 'NO BINARIO' (2 filas) se conserva: no se reasigna a HOMBRE/MUJER
    return s
