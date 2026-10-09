"""Modelo curado de ANID-Portal: hechos, dimensiones y agregados para el tablero.

Regla del paquete: ninguna métrica viaja sin su unidad de conteo (`filas`, `codigos`,
`proyectos`) y ningún monto viaja sin declarar si es nominal, real o de otro año.

    from modelo import construir_todo
    meta = construir_todo()   # escribe outputs/ y devuelve los metadatos del corte
"""

from .becas import construir_becas
from .colaboracion import construir_colaboracion
from .deflactores import Deflactores, cargar_deflactores
from .instituciones import construir_dim_institucion, mapa_nombre_a_rut
from .postulaciones import construir_postulaciones, tasa_por_region
from .proyectos import construir_proyectos

__all__ = [
    "Deflactores",
    "cargar_deflactores",
    "construir_becas",
    "construir_colaboracion",
    "construir_dim_institucion",
    "construir_postulaciones",
    "construir_proyectos",
    "mapa_nombre_a_rut",
    "tasa_por_region",
]
