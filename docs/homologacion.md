# Fase 1 — Homologación (especificación)

> Objetivo: que cada etiqueta del dato crudo caiga en una categoría canónica, **sin perder filas en silencio**. Cada regla es una función pura con test y con una **cifra de control** (el conteo que debe dar después de homologar). Las cifras de control ya están medidas y están en `docs/datos.md`.
>
> Regla transversal: toda fila que no calce con ninguna regla no se descarta — se asigna a `NO CLASIFICADO` y se reporta su conteo. Un normalizador que baja el total de filas es un bug.

## H1 — Región (24 etiquetas → 16 + 3)

Salida canónica (16): `ARICA Y PARINACOTA` · `TARAPACA` · `ANTOFAGASTA` · `ATACAMA` · `COQUIMBO` · `VALPARAISO` · `METROPOLITANA` · `OHIGGINS` · `MAULE` · `NUBLE` · `BIOBIO` · `ARAUCANIA` · `LOS RIOS` · `LOS LAGOS` · `AYSEN` · `MAGALLANES`.
Categorías no territoriales (3): `SIN INFORMACION` · `EXTRANJERO` · `MULTIREGIONAL`.

Reglas: quitar tildes y puntuación, colapsar espacios, quitar el prefijo `REGION (DE|DEL|LA|EL)`, quitar sufijos honoríficos (`DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS` y `DE OHIGGINS` → `OHIGGINS`; `DE MAGALLANES Y (DE LA )?ANTARTICA CHILENA` → `MAGALLANES`; `DE AYSEN DEL GENERAL CARLOS IBANEZ DEL CAMPO` y `AYSEN` → `AYSEN`; `DEL NUBLE`/`DE NUBLE`/`DE ÑUBLE` → `NUBLE`; `BIO-BIO`/`BIO BIO` → `BIOBIO`; `METROPOLITANA (DE SANTIAGO)?` → `METROPOLITANA`).

**Aplicar en las 4 bases** (Histórico, Postulaciones, Becas, Colaboración) porque cada una usa una convención distinta.

| Cifra de control | Valor |
|---|---|
| RM homologada (Histórico) | **27.212** (cruda: 26.334) |
| Igualdad con `MACROZONA_MINCIENCIA`=RM | **27.212** (debe coincidir exacto) |
| Ñuble homologada (Histórico) | 57 (42+15); Postulaciones trae `REGION DE ÑUBLE` 623 |
| Filas totales (Histórico) | 49.014, sin pérdidas |

## H2 — Macrozona

Ya viene limpia (9 valores: `RM`, `NORTE`, `CENTRO`, `CENTRO SUR`, `SUR`, `AUSTRAL`, `EXTRANJERO`, `SIN INFORMACION`, `MULTIREGIONAL`; en Becas además `NO APLICA`). Regla: **derivar la macrozona desde la región homologada** y usarla como control cruzado, no como fuente. Si una región homologada produce una macrozona distinta a la del archivo, se reporta la excepción (debe ser 0).

## H3 — Moneda y monto

Salida: `monto_clp` (entero) + `moneda_origen` + `monto_valido` (bool).
- Rótulos `Miles de pesos (M$)`, `MILES DE PESOS (M$)`, `M$`, `Miles de pesos` → **miles de pesos** × 1.000.
- `EUROS` → se conserva como `monto_eur` aparte; **nunca** se suma con pesos. 38 filas.
- Vacío (2.413) o literal no numérico (`NO SOLICITA A CONICYT`, 2 filas) → `monto_valido = False`, monto nulo. No se imputa.
- El pipeline elimina puntos de miles y convierte coma decimal.

| Cifra de control | Valor |
|---|---|
| Filas sin monto | 2.423 (4,9%) |
| Filas en euros | 38 |
| RM 2020-2025 (solo pesos con monto) | $1.152.602 millones |
| Filas usadas en ese cierre | 11.301 de 11.782 |

## H4 — Subdirección (7 rótulos → 5 + NO APLICA)

`REDES ESTRATEGIA Y CONOCIMIENTO` + `REDES, ESTRATEGIA Y CONOCIMIENTO` → una sola. `NO APLICA` (2.484, todo pre-2010) se mantiene como categoría propia, no se reasigna. En Postulaciones la etiqueta canónica es la variante **con coma**.

## H5 — Tipo de beneficiario (6 → 3)

`PERSONA NATURAL` · `PERSONA JURIDICA` · `SIN INFORMACION`. Fusionar `NATURAL O JURIDICA`/`JURIDICA` y `PERSONA NATURAL O PERSONA JURIDICA` (combinaciones, 61 filas) en su categoría mixta declarada o en `SIN INFORMACION` — **decidir con el usuario**, no en silencio. Igual criterio en `SEXO` de Becas (`FEMENINO`/`MASCULINO` → `MUJER`/`HOMBRE`, 1.428 filas).

## H6 — Institución

Sin RUT en el Histórico. Estrategia en dos pasos:
1. Normalizar nombre (sin tildes, sin puntuación, mayúsculas, espacios colapsados) → 1.749 → 1.733 en el Histórico; 5.694 → 5.574 en Colaboración.
2. Cuando exista RUT (Colaboración), **el RUT manda**: 2.477 normalizados. Reportar los 411 RUT con más de un nombre y los 117 nombres con más de un RUT como tabla de decisiones (no se resuelven automáticamente).
3. Dimensiones adicionales a construir: `tipo_institución` (universidad / centro / empresa / IPSFL / Estado) — **no viene en el Histórico**, hay que derivarla; y `institución_matriz` (U. de Chile, PUC, USACH…) para agrupar filiales — **no existe en el dato**.

## H7 — Rol institucional (65 → ~8)

Colapsar a: `PRINCIPAL/BENEFICIARIA` · `PATROCINANTE` · `SECUNDARIA/ASOCIADA` · `APORTANTE/COFINANCIAMIENTO` · `COLABORADORA/PARTICIPANTE` · `EXTRANJERA` · `MANDANTE/POSTULANTE` · `NO APLICA`. La tabla completa de equivalencias se escribe en `src/homologacion/roles.py` y queda versionada (es la única pieza que no se reconstruye desde el dato).

## H8 — Unidad de conteo

El modelo expone tres métricas separadas y las etiqueta en el tablero: `filas`, `codigos_unicos`, `proyectos` (código + año). Toda tarjeta declara cuál usa. Los 136 códigos repetidos del Histórico deben aparecer explicados en el detalle del tablero.

## Entregables y verificación de la fase

1. `src/homologacion/*.py` — un módulo por regla (región, moneda, subdirección, beneficiario, institución, roles).
2. `tests/` — por regla: (a) caso que transforma, (b) caso que queda igual, (c) **cuadre de totales**: el conteo de filas de entrada es igual al de salida.
3. `docs/evidencia/cuadre-homologacion.md` — tabla con cada cifra de control de este documento y la obtenida.
4. `@revisar` independiente contra `docs/datos.md` antes de pasar a la Fase 2.

**Criterio de cierre:** 0 filas perdidas, todas las cifras de control reproducidas, toda etiqueta nueva reportada (no absorbida).
