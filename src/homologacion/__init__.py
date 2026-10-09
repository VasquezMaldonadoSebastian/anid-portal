"""Homologación del dato crudo de ANID.

Cada módulo es una regla (H1-H8 de docs/homologacion.md) y cada regla es una
función pura con test. Regla transversal: ninguna fila se descarta en silencio —
lo que no calza se marca NO CLASIFICADO y se cuenta.
"""

from .categorias import homologar_sexo, homologar_tipo_beneficiario
from .fuentes import cargar
from .institucion import clave_institucion, normalizar_nombre, normalizar_rut
from .macrozona import macrozona_de_region, verificar_macrozona
from .metricas import contar_codigos, contar_filas, contar_proyectos
from .moneda import a_pesos, es_pesos, rotulo_moneda
from .region import NO_CLASIFICADO, homologar_region
from .roles import homologar_rol
from .subdireccion import homologar_subdireccion

__all__ = [
    "NO_CLASIFICADO",
    "a_pesos",
    "cargar",
    "clave_institucion",
    "contar_codigos",
    "contar_filas",
    "contar_proyectos",
    "es_pesos",
    "homologar_region",
    "homologar_rol",
    "homologar_sexo",
    "homologar_subdireccion",
    "homologar_tipo_beneficiario",
    "macrozona_de_region",
    "normalizar_nombre",
    "normalizar_rut",
    "rotulo_moneda",
    "verificar_macrozona",
]
