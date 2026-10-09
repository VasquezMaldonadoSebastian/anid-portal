# Validación del modelo curado (Fase 2)

**Generado por** `scripts/validar-modelo.py` · **Corte:** 2026-10-09 12:39 (hora Chile) · **Deflactores:** Banco Mundial FP.CPI.TOTL (CHL) (base 2010, consulta 2026-10-09)

**Resultado: 43 de 43 cifras de control reproducidas.**

| Cifra de control | Esperado | Obtenido | Veredicto |
|---|---|---|---|
| proyectos: filas | 49.014 | 49.014 | OK |
| proyectos: códigos únicos | 48.707 | 48.707 | OK |
| proyectos: pares (código. año) | 48.835 | 48.835 | OK |
| región sin clasificar | 0 | 0 | OK |
| filas con macrozona asignada | 49.014 | 49.014 | OK |
| RM homologada | 27.212 | 27.212 | OK |
| Ñuble homologada | 57 | 57 | OK |
| filas con monto en pesos válido | 46.551 | 46.551 | OK |
| filas sin monto en pesos | 2.425 | 2.425 | OK |
| filas en euros | 38 | 38 | OK |
| RM 2020-2025: filas | 6.093 | 6.093 | OK |
| RM 2020-2025: pesos | 1.160.514.000.000 | 1.160.513.671.985.0 | OK |
| país 2020-2025: filas | 11.395 | 11.395 | OK |
| país 2020-2025: pesos | 2.095.227.000.000 | 2.095.227.390.102.0 | OK |
| montos reales calculados (años con IPC) | 44.973 | 44.973 | OK |
| montos reales nulos en 2026 | 0 | 0 | OK |
| monto real en pesos del año base | 105.095.123.000.0 | 105.095.123.000.0 | OK |
| colaboración: filas | 33.731 | 33.731 | OK |
| colaboración: proyectos | 16.426 | 16.426 | OK |
| colaboración: roles sin clasificar | 0 | 0 | OK |
| colaboración: RUT válidos | 2.476 | 2.476 | OK |
| postulaciones: filas | 139.517 | 139.517 | OK |
| postulaciones de proyectos (sin Capital Humano) | 68.133 | 68.133 | OK |
| adjudicadas de proyectos | 18.233 | 18.233 | OK |
| tasa de adjudicación (%) | 26.8 | 26.8 | OK |
| becas: filas | 19.288 | 19.288 | OK |
| becas: hombres | 10.269 | 10.269 | OK |
| becas: mujeres | 9.019 | 9.019 | OK |
| hecho: nombres de institución distintos | 1.749 | 1.749 | OK |
| hecho: nombres normalizados distintos | 1.733 | 1.733 | OK |
| hecho: claves de institución distintas | 1.707 | 1.707 | OK |
| invariante: ningún nombre repartido entre dos claves | 0 | 0 | OK |
| dim institución: claves del hecho presentes en la dimensión | 0 | 0 | OK |
| dim institución: nombres homónimos repartidos en claves distintas | 21 | 21 | OK |
| colaboración: RUT con más de un nombre | 373 | 373 | OK |
| colaboración: nombres con más de un RUT (ambiguos. no se adivinan) | 21 | 21 | OK |
| dim institución: claves de proyectos presentes en la dimensión | 0 | 0 | OK |
| agg_region: filas suman el hecho | 49.014 | 49.014 | OK |
| agg_region: monto suma el hecho | 4.977.971.656.662.0 | 4.977.971.656.662.0 | OK |
| agg_region: filas sin monto suman 2.425 pesos + 38 euros | 2.463 | 2.463 | OK |
| agg_region: filas sin deflactor (2026 con monto) | 1.578 | 1.578 | OK |
| agg_institucion: filas suman el hecho | 49.014 | 49.014 | OK |
| agg_institucion: monto suma el hecho | 4.977.971.656.662.0 | 4.977.971.656.662.0 | OK |

## Tamaño de las tablas entregadas

| Tabla | Filas |
|---|---|
| `proyectos` | 49.014 |
| `colaboracion` | 33.731 |
| `postulaciones` | 139.517 |
| `becas` | 19.288 |
| `dim_institucion` | 6.094 |
| `tasa_region` | 174 |
| `agg_region` | 1.820 |
| `agg_institucion` | 7.678 |
| `agg_programa` | 1.119 |

## Metadatos del corte que alimenta el pie del tablero

```json
{
  "generado": "2026-10-09 13:13 (hora Chile)",
  "corte": {
    "fecha": "2026-10-09 12:39 (hora Chile)",
    "sha256_manifiesto": "addab19a43c9b6d1c84ade6eb4cb53921dd0d7336da6f2b0f7d07c29009f86c4"
  },
  "deflactores": {
    "fuente": "Banco Mundial FP.CPI.TOTL (CHL)",
    "fecha_consulta": "2026-10-09",
    "base": 2010,
    "anios": [
      1980,
      2025
    ]
  },
  "filas": {
    "proyectos": 49014,
    "colaboracion": 33731,
    "postulaciones": 139517,
    "becas": 19288,
    "dim_institucion": 6094,
    "tasa_region": 174,
    "agg_region": 1820,
    "agg_institucion": 7678,
    "agg_programa": 1119
  },
  "tasa_adjudicacion_proyectos": {
    "postulaciones": 68133,
    "adjudicadas": 18233,
    "tasa": 26.76
  },
  "notas": [
    "monto_clp es nominal; monto_clp_real está en pesos del año base de los deflactores.",
    "2026 no tiene IPC anual cerrado: sus montos reales son nulos (el año va apagado por defecto).",
    "filas ≠ codigos ≠ proyectos: cada tarjeta del tablero declara cuál usa."
  ]
}
```
