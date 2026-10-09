# Fase 1 — Homologación (especificación y resultado)

> Objetivo: que cada etiqueta del dato crudo caiga en una categoría canónica, **sin perder filas en silencio**. Cada regla es una función pura con test y con una **cifra de control** (el conteo que debe dar después de homologar).
>
> Regla transversal: toda fila que no calce con ninguna regla no se descarta — se asigna a `NO CLASIFICADO` y se reporta su conteo. Un normalizador que baja el total de filas es un bug.
>
> **Estado:** aplicada y verificada el 2026-10-09. Módulos en `src/homologacion/`, 145 tests en verde, cuadre completo en `docs/evidencia/cuadre-homologacion.md`.

## H1 — Región (24 etiquetas → 16 regiones + 4 categorías no territoriales)

Salida canónica (16): `ARICA Y PARINACOTA` · `TARAPACA` · `ANTOFAGASTA` · `ATACAMA` · `COQUIMBO` · `VALPARAISO` · `METROPOLITANA` · `OHIGGINS` · `MAULE` · `NUBLE` · `BIOBIO` · `ARAUCANIA` · `LOS RIOS` · `LOS LAGOS` · `AYSEN` · `MAGALLANES`.
No territoriales (4): `SIN INFORMACION` · `EXTRANJERO` · `MULTIREGIONAL` · `NO APLICA` (esta última solo existe en Becas y Colaboración).

**Implementación** (`src/homologacion/region.py`): diccionario de etiquetas **observadas** (30 entradas, las que existen en las 4 bases) + reglas de respaldo por patrón para un corte nuevo. No se inventan equivalencias: lo que no está en el diccionario ni calza con un patrón devuelve `NO CLASIFICADO` y `no_clasificados()` lo reporta con su conteo.

Normalización previa: sin tildes, mayúsculas, guiones a espacio, sin puntuación, espacios colapsados. Ese paso es el que resuelve `BIO-BIO`/`BIO BIO`, `ÑUBLE`/`NUBLE` y `O'HIGGINS`.

| Cifra de control | Valor | Obtenido |
|---|---|---|
| RM homologada (Histórico) | **27.212** (cruda: 26.334 + 878) | ✅ 27.212 |
| Ñuble homologada (Histórico) | 57 (42 + 15) | ✅ 57 |
| Filas del histórico | 49.014, sin pérdidas | ✅ 49.014 |
| Etiquetas sin clasificar | 0 en las 4 bases | ✅ 0 (Histórico, Becas, Colaboración, Postulaciones) |

> Trampa documentada: `"REGION DE ÑUBLE"` **no** contiene la cadena `"NUBLE"`. Todo filtro sobre texto crudo tiene que ser insensible a la tilde o hay que filtrar sobre la columna homologada.

## H2 — Macrozona (derivada y verificada)

Regla: **derivar la macrozona desde la región homologada** y usarla como control cruzado, no como fuente. El mapeo se midió contra `MACROZONA_MINCIENCIA` con un crosstab región × macrozona (49.014 filas, **0 regiones caen en más de una macrozona**), y tiene dos diferencias con la agrupación que uno supondría:

| Macrozona | Regiones |
|---|---|
| `NORTE` | Arica y Parinacota, Tarapacá, Antofagasta, Atacama |
| `CENTRO` | **Coquimbo**, Valparaíso |
| `RM` | Metropolitana (macrozona propia, no parte de `CENTRO`) |
| `CENTRO SUR` | **O'Higgins**, Maule, Ñuble, Biobío |
| `SUR` | La Araucanía, Los Ríos, Los Lagos |
| `AUSTRAL` | Aysén, Magallanes |
| no territoriales | `EXTRANJERO`, `MULTIREGIONAL`, `SIN INFORMACION`, `NO APLICA` |

Sumas de control (histórico, exactas): RM 27.212 · Centro Sur 7.138 · Centro 6.082 · Sur 4.803 · Norte 2.357 · Sin información 697 · Austral 490 · Extranjero 124 · Multiregional 111.

| Verificación | Resultado |
|---|---|
| Histórico: derivada = archivo | **0 excepciones** de 49.014 |
| Postulaciones: derivada = archivo | **0 excepciones** de 139.517 |
| Becas: derivada = archivo | **1 excepción**: una fila con región Metropolitana y macrozona `CENTRO` en el archivo de ANID (se conserva la derivación y la discrepancia se documenta) |

## H3 — Moneda y monto

Salida: `monto_clp` (float, en pesos) + `monto_eur` + `moneda_homologada` + `monto_valido` (bool).
- Rótulos `Miles de pesos (M$)`, `MILES DE PESOS (M$)`, `Miles de pesos` **y `M$`** → miles de pesos × 1.000 (46.563 filas).
- `EUROS` → `monto_eur` aparte; **nunca** se suma con pesos (38 filas).
- Vacío o literal no numérico (`NO SOLICITA A CONICYT`) → `monto_valido = False`, monto nulo. **No se imputa.**
- Parseo: quita puntos de miles, convierte coma decimal.

| Cifra de control | Valor | Obtenido |
|---|---|---|
| Filas con rótulo en pesos | 46.563 | ✅ 46.563 |
| Filas sin rótulo de moneda | 2.413 | ✅ 2.413 |
| Filas en euros | 38 | ✅ 38 |
| Filas sin monto en pesos | **2.425** (2.413 + 10 vacías + 2 literales) | ✅ 2.425 |
| RM 2020-2025 | **$1.160.514 millones**, 6.093 filas | ✅ exacto |
| País 2020-2025 | $2.095.227 millones, 11.395 de 11.782 filas | ✅ exacto |

> Corrección respecto de la primera versión de `docs/datos.md`: el primer cierre (11.301 filas, $1.152.602 millones en la RM) filtraba por el **texto** del rótulo y dejaba fuera las 94 filas `M$`, que son la misma unidad.

## H4 — Subdirección (7 rótulos → 5 + NO APLICA)

`REDES ESTRATEGIA Y CONOCIMIENTO` + `REDES, ESTRATEGIA Y CONOCIMIENTO` → una sola (5.951 filas). `NO APLICA` (2.484, todo pre-2010) se mantiene como categoría propia, no se reasigna. En Postulaciones la etiqueta canónica es la variante **con coma**.

Resultado: 0 sin clasificar · Proyectos de Investigación 33.392 · Redes 5.951 · Investigación Aplicada 5.667 · No aplica 2.484 · Centros 1.332 · Capital Humano 188 (suma 49.014).

## H5 — Tipo de beneficiario y sexo (resuelto)

`TIPO_BENEFICIARIO` (6 rótulos → 4): `PERSONA NATURAL` 37.187 · `PERSONA JURIDICA` 11.565 · `SIN INFORMACION` 201 · **`NATURAL O JURIDICA` 61** (categoría mixta declarada; incluye las 46 `PERSONA NATURAL O PERSONA JURIDICA`, las 15 `NATURAL O JURIDICA` y las 7 `JURIDICA`). No se reparten en silencio.

`SEXO` en Becas (4 rótulos → 2): `FEMENINO` 739 → `MUJER`, `MASCULINO` 689 → `HOMBRE`; quedan 10.269 hombres y 9.019 mujeres. Cualquier otro valor (p. ej. `NO BINARIO`) se conserva sin reasignar.

## H6 — Institución

Sin RUT en el Histórico. Estrategia en dos pasos:
1. **Normalizar nombre** (sin tildes, sin puntuación, mayúsculas, guiones a espacio, espacios colapsados) → 1.749 → 1.733 en el Histórico; 5.694 → 5.574 en Colaboración. **No se quitan palabras** de la razón social: solo tipografía.
2. Cuando exista RUT, **el RUT manda**: 2.476 RUT válidos de 2.500 valores del campo. La clave canónica es `RUT:NNNNNNNN-K` y, sin RUT, `NOMBRE:<normalizado>`.
3. Colisiones (reportadas como tabla de decisiones en `docs/evidencia/instituciones-colisiones.md`, no resueltas automáticamente): **373 RUT con más de un nombre** y **21 nombres con más de un RUT**. Se cuentan solo sobre RUT válidos — el primer perfilado daba 411/117 porque trataba el RUT vacío como identificador compartido.
4. Dimensiones que **no existen en el dato** y no se inventan: `tipo_institución` (universidad / centro / empresa / IPSFL / Estado) y `institución_matriz` para agrupar filiales.

## H7 — Rol institucional (65 → 9 + NO CLASIFICADO)

Canónicos: `BENEFICIARIA / PRINCIPAL` (13.968) · `ASOCIADA / PARTICIPANTE` (12.273) · `EXTRANJERA` (2.820) · `PATROCINANTE` (2.367) · `APORTANTE / COFINANCIAMIENTO` (1.293) · `POSTULANTE` (395) · `ALBERGANTE / PROCEDENCIA` (362) · `OTRA ENTIDAD` (233) · `NO APLICA` (20). Suma 33.731, **0 sin clasificar**.

Orden de las reglas (importa): `NO APLICA` → **extranjera** (si dice EXTRANJERA/CHINA/FRANCIA, manda: es la distinción útil en un tablero chileno) → responsable pública/privada y beneficiaria/principal → patrocinante → asociada → aportante → postulante → albergante → otra entidad. Los roles con dos nombres (`INSTITUCION NACIONAL PATROCINANTE ASOCIADA`) se clasifican por el más fuerte. La tabla queda versionada en `src/homologacion/roles.py`: es la única pieza que no se reconstruye desde el dato.

## H8 — Unidad de conteo

El modelo expone tres métricas separadas y las etiqueta en el tablero: `filas` (49.014), `codigos_unicos` (48.707) y `proyectos` = pares (código, año) (48.835). Toda tarjeta declara cuál usa. Los **136 códigos repetidos** (443 filas) tienen todos contenido distinto entre sus filas y aparecen explicados en el detalle del tablero.

## Entregables y verificación de la fase

1. `src/homologacion/*.py` — un módulo por regla (`region`, `macrozona`, `moneda`, `subdireccion`, `categorias`, `institucion`, `roles`, `metricas`) + `fuentes.py` (lectura única).
2. `tests/` — por regla: (a) caso que transforma, (b) caso que no se toca, (c) **cuadre de totales**. 145 tests.
3. `scripts/cuadre_homologacion.py` → `docs/evidencia/cuadre-homologacion.md` (cada cifra de control con lo obtenido) e `docs/evidencia/instituciones-colisiones.md`.
4. `@revisar` independiente contra `docs/datos.md` antes de pasar a la Fase 2.

**Criterio de cierre:** 0 filas perdidas, todas las cifras de control reproducidas, toda etiqueta nueva reportada (no absorbida). ✅ Cumplido el 2026-10-09.
