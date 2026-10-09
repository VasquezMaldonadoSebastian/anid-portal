# Perfilado de las fuentes ANID — medido el 2026-10-09

> Todo lo de este documento está **medido** sobre los archivos descargados (`data/crudo/`), no copiado de los README. Los scripts y salidas que lo producen están en `docs/evidencia/`. Reproducir con `py -3.11 docs/evidencia/profile_h2.py`, `profile_resto.py`, `profile_checks.py`, `profile_join.py`, `profile_join2.py`, `profile_rut.py`.

## 1. Inventario

| Repo | Archivos | Filas | Campos | Cobertura temporal | Corte / última actualización |
|------|----------|-------|--------|--------------------|------------------------------|
| Historico-de-Proyectos-Adjudicados | `BDH_HISTORICA.csv/.xlsx` | 49.014 | 23 | 1982-2026 | 01-sep-2026 (2º trimestre 2026); trimestral |
| Historico… | `BDH_PROYECTOS_MILENIO.csv` | 136 | 21 | 1999-2022 | — |
| Colaboracion_Institucional | `CONSOLIDADO_INSTITUCIONES.csv` | 33.731 | 9 | 2016-2025 | 23-feb-2026; anual |
| Colaboracion_Institucional | `SPI_INVESTIGADORES.csv` | 20.620 | 10 | 2016-2025 | 23-feb-2026 |
| Postulaciones | `POSTULACIONES_2016_2025.csv` | 139.517 | 15 | 2016-2025 | 27-may-2026; anual |
| Postulaciones | `POSTULACIONES_MILENIO.csv` | 1.205 | 14 | — | — |
| Becas | `BDH_BECAS SCH.csv` | 19.288 | 19 | 2015-2025 | 16-abr-2026; anual |
| Palabras_claves | `BD_Palabras_claves_{Proyectos,Becas}.csv` | 12.873 + 17.245 | 4 | hasta 2024 | 11-jun-2024 (corte dic-2023, discontinuada) |
| FONDECYT-Abstracts | 3 CSV + XLSX | — | 5 | 2016-2025 | irregular; **sin licencia** |
| Instructivo_descarga | PDF | — | — | — | 26-dic-2024 |
| Consulta-Publica-Politica-de-Acceso-Abierto | `BBDD_Consulta_PAA.csv` | 732 | 62 | 2025 | 13-may-2025; **fuera de alcance** |

**Total procesable: 293.629 filas / 77,3 MB de CSV.** El `.xlsx` espejo de cada base tiene los mismos conteos (verificado: 49.015×23, 33.732×9, 139.518×15, 19.289×19 incluyendo encabezado).

## 2. Formato (trampas que rompen pipelines)

- **Delimitador `;`** en todos los CSV. Con el delimitador por defecto, el engine C de pandas aborta: `ParserError: Expected 1 fields in line 10427, saw 2`.
- **UTF-8 con BOM** → la primera columna se lee como `\ufeffN` si no se usa `encoding='utf-8-sig'`.
- **Saltos de línea dentro de campos citados**: el histórico tiene 49.041 líneas físicas para 49.014 filas (Postulaciones: 139.630 para 139.517; Becas: 19.311 para 19.288). Nunca parsear por líneas.
- **Todo se lee como texto** y se castea: el código de proyecto es alfanumérico (`ID24I10087`, `GS-2003B-Q-36`, `SININFORMACION`) y los montos vienen con separador de miles.
- Cambios de esquema entre archivos hermanos: el histórico tiene `MONTO_ADJUDICADO` + `MONEDA`; el de Milenio tiene `MONTO_ADJUDICADO (M$)` sin moneda. Los de Milenio traen rótulos con espacios (`ANO_FALLO`, `MACRO ZONA`, `TIPO DE INSTITUCION`).

## 3. Campo territorial (Histórico)

**`REGION_EJECUCION`: 24 etiquetas crudas → 16 regiones + 3 categorías no territoriales.**

Etiquetas crudas y su peso: `REGION DE METROPOLITANA` 26.334 · `REGION DEL BIOBIO` 5.280 · `REGION DE VALPARAISO` 5.205 · `REGION DE LOS RIOS` 2.081 · `REGION DE LA ARAUCANIA` 2.076 · `REGION DEL MAULE` 1.461 · `REGION DE ANTOFAGASTA` 1.392 · `REGION METROPOLITANA DE SANTIAGO` 878 · `REGION DE COQUIMBO` 877 · `SIN INFORMACION` 697 · `REGION DE LOS LAGOS` 646 · `REGION DE ARICA Y PARINACOTA` 446 · `REGION DE MAGALLANES Y ANTARTICA CHILENA` 361 · `REGION DE TARAPACA` 319 · `REGION DE OHIGGINS` 307 · `REGION DE ATACAMA` 200 · `EXTRANJERO` 124 · `REGION DE AYSEN` 118 · `MULTIREGIONAL` 111 · `REGION DEL NUBLE` 42 · `REGION DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS` 33 · `REGION DE NUBLE` 15 · `REGION DE MAGALLANES Y DE LA ANTARTICA CHILENA` 9 · `REGION DE AYSEN DEL GENERAL CARLOS IBANEZ DEL CAMPO` 2.

**El cambio de convención es por era** (verificado): hasta 2025 el archivo usa las etiquetas antiguas; las filas con fallo 2026 usan las nuevas (`REGION METROPOLITANA DE SANTIAGO`, `REGION DE NUBLE`, `REGION DE MAGALLANES Y DE LA ANTARTICA CHILENA`, `REGION DE AYSEN DEL GENERAL CARLOS IBANEZ DEL CAMPO`). Otras bases usan una tercera (Colaboración: `REGION DEL BIO-BIO` con guion) y una cuarta (Becas y Postulaciones: `REGION DE ÑUBLE` con tilde, `REGION DE AYSEN … IBAÑEZ …`).

**Efecto de no homologar:** RM = 26.334 (cruda) vs **27.212** (homologada) → 3,2% de desvío en el filtro más usado. La cifra homologada **coincide exactamente con `MACROZONA_MINCIENCIA`=RM (27.212)**, lo que confirma que la homologación es correcta y que la macrozona es el nivel territorial confiable.

Sin dato territorial: 932 filas (1,9%) = 697 sin información + 124 extranjero + 111 multirregional. En 2016+ solo 160 filas sin región.

**Cobertura por década (región / monto presentes):** ≤1989 100% / 100% · 1990-99 97,2% / 97,2% · 2000-09 96,9% / 88,4% · 2010-15 98,0% / 94,9% · 2016-19 98,8% / 96,8% · 2020-25 99,4% / 97,0%.

## 4. Campo institucional

- **Histórico:** `INSTITUCION_PRINCIPAL` con **1.749 valores** (1.733 al normalizar texto: solo 16 grupos fusionan variantes, p. ej. `UNIVERSIDAD DEL BIO BIO` / `UNIVERSIDAD DEL BIO-BIO`). Top: U. de Chile 10.013 · PUC 7.842 · U. de Concepción 4.083 · USACH 2.410 · U. Austral 1.932 · PUCV 1.924 · UTFSM 1.639 · UFRO 1.406. Incluye el pseudo-valor `SIN INFORMACION` (311 filas).
- **Volumen:** 44 instituciones con ≥100 proyectos, 65 con ≥30, 108 con ≥10. **1.542 instituciones (88,2%) tienen ≤3 proyectos y suman 1.944 filas (4,0%)** → cola larga que un "top N" esconde.
- **Institución × región:** 127 instituciones (de 1.637 con región real) aparecen en más de una región; U. de Concepción en 15 regiones, U. de Chile en 15, PUC en 13. La jerarquía institución→región **no es 1:1**.
- **Colaboración:** `INSTITUCION1ERNIVEL` con 5.694 nombres → 5.574 normalizados → **2.476 RUT válidos** (de 2.500 valores en el campo). Colisiones contadas **sólo sobre RUT válidos**: 373 RUT con más de un nombre y 21 nombres con más de un RUT. 37 filas sin RUT. Formato: 4.591 filas no siguen `NNNNNNNN-N` (incluye el literal `SIN INFORMACION`). *(Corregido en la Fase 1: el primer conteo usaba el campo crudo y contaba como colisión el RUT vacío compartido.)*
- **Roles:** 65 valores crudos de `ROLINSTITUCION` (top: institución principal 9.940, secundaria 5.797, asociada 2.688, entidad asociada 2.412, beneficiaria principal 2.263, patrocinante 1.954) → requiere colapsar a roles canónicos.
- **Cruces:** Colaboración ⊂ Histórico por `CODIGO_PROYECTO`: **16.426 de 16.426** (100%). Del histórico 2016-2026 (21.054 códigos; 19.463 si se corta en 2025) el **78%** tiene registro de colaboración. Al comparar la institución principal del mismo proyecto entre ambas bases: **94,0% de coincidencia** (14.334 filas comparadas; el 6% restante es la divergencia que ANID declara por cambios al firmar convenio).
- **País:** 71 valores; CHILE 30.278, FRANCIA 587, ESPAÑA 484, EE.UU. 374, BRASIL 268.
- **Región de la institución asociada:** 17,7% sin región (4.198 `NO REGISTRA REGION` + 1.770 `NO APLICA`).

## 5. Campo monetario

`MONTO_ADJUDICADO` (Histórico), 5 valores de `MONEDA`:

| Rótulo | Filas | Suma (en miles) | Mediana |
|--------|-------|-----------------|---------|
| `Miles de pesos (M$)` | 42.882 | 4.450.211.000 | 58.191 |
| `MILES DE PESOS (M$)` | 3.575 | 507.006.300 | 104.400 |
| `M$` | 94 | 20.954.400 | 227.698 |
| `EUROS` | 38 | 338.702 | 5.200 |
| *(vacío)* | 2.413 | — | — |

**Sin monto utilizable: 2.425 filas (4,9%)** = 2.413 sin rótulo de moneda + 10 con rótulo de pesos y valor vacío + 2 con el literal `NO SOLICITA A CONICYT`. Aparte, 38 filas en `EUROS` que no se convierten ni se suman. Las 94 filas rotuladas `M$` son todas FONDEF Idea I+D 2024 y **sí son pesos** (misma unidad que `Miles de pesos (M$)`, suman 20.954.400 miles). Un monto de `58.191` significa **$58.191.000**.

**Cierre de prueba (2020-2025, filas con rótulo en pesos y monto numérico, 11.395 de 11.782 filas del período):**

| Macrozona | Filas | Total |
|-----------|-------|-------|
| RM | 6.093 | $1.160.514 millones |
| Centro Sur | 1.894 | $339.928 millones |
| Centro | 1.417 | $256.865 millones |
| Sur | 1.206 | $193.685 millones |
| Norte | 611 | $104.357 millones |
| Austral | 123 | $35.016 millones |
| Multiregional | 25 | $3.720 millones |
| Sin información | 26 | $1.143 millones |
| **Total** | **11.395** | **$2.095.227 millones** |

> Estas cifras **incluyen las 94 filas `M$`** que la primera versión de este documento excluía por filtrar por el texto del rótulo ("pesos") en vez de por la unidad. La diferencia en la RM es 6.093 vs 6.058 filas y $1.160.514 vs $1.152.602 millones.

Top instituciones 2020-2025: U. de Chile 1.456 proyectos · PUC 1.398 · U. de Concepción 785 · USACH 473 · PUCV 434.

## 6. Duplicidad e identidad de fila

- Histórico: 49.014 filas / 48.707 códigos. **443 filas con código repetido (136 códigos)** y los 136 tienen contenido distinto entre sí (casos `GS-****-Q-*` de observaciones astronómicas y filas con código `SININFORMACION`).
- Postulaciones: 139.517 filas / 139.369 códigos.
- Colaboración: 33.731 filas / 16.426 proyectos (media 2,05 filas por proyecto; hasta 44 en un caso).
- Becas: `CODIGO_BECA` único (19.288/19.288).

## 7. Encadenamiento entre bases (para el modelo)

| Origen | Destino | Regla | Cobertura medida |
|--------|---------|-------|------------------|
| Postulaciones (4 subdirecciones de proyectos) | Histórico | `CODIGO_PROYECTO` | 99-100% |
| Postulaciones CAPITAL HUMANO | Becas | `CODIGO_PROYECTO` = `CODIGO_BECA` | 92% |
| Colaboración | Histórico | `CODIGO_PROYECTO` | 100% |
| SPI investigadores | Histórico | `CODIGO_PROYECTO` | 8.837 proyectos SPI (FONDECYT Regular) |
| FONDECYT-Abstracts | Histórico | `codigo_proyecto` (minúsculas) | 3 concursos 2016-2025 |
| Palabras claves | Histórico / Becas | `CODIGO_PROYECTO` / `CODIGO_BECA` | corte 2023; desde 2024 viene dentro de cada base |

**Tasa de adjudicación (Postulaciones 2016-2025):** ADJUDICADO 36.782 filas / 36.731 códigos, de las cuales solo 18.350 (50%) están en el histórico porque Capital Humano adjudica becas. Excluyendo Capital Humano: 68.133 postulaciones de proyectos, 18.233 adjudicadas → **26,8%**.

| Región (solo proyectos) | Postulaciones | Adjudicadas | Tasa |
|---|---|---|---|
| Metropolitana | 34.352 | 9.594 | 27,9% |
| Valparaíso | 7.908 | 2.168 | 27,4% |
| Biobío | 7.775 | 1.970 | 25,3% |
| La Araucanía | 3.847 | 1.007 | 26,2% |
| Maule | 2.869 | 695 | 24,2% |
| Los Ríos | 2.494 | 681 | 27,3% |
| Antofagasta | 2.173 | 519 | 23,9% |
| Coquimbo | 965 | 263 | 27,3% |
| Los Lagos | 933 | 226 | 24,2% |
| Sin información | 933 | 138 | 14,8% |
| Arica y Parinacota | 777 | 191 | 24,6% |
| O'Higgins | 710 | 221 | 31,1% |
| Magallanes | 561 | 144 | 25,7% |
| Atacama | 540 | 95 | 17,6% |
| Tarapacá | 474 | 121 | 25,5% |
| Multirregional | 402 | 105 | 26,1% |
| Aysén | 192 | 56 | 29,2% |
| Ñuble | 186 | 35 | 18,8% |
| Extranjero | 42 | 4 | 9,5% |

**Límite duro:** no existe denominador **por institución** (Postulaciones no trae nombre de institución — solo `TIPO_INSTITUCION` — y las **85.958 filas** con estado `NO ADJUDICADO` (**85.907 códigos**) no tienen institución en ninguna base).

## 8. Discrepancias documento ↔ artefacto

| Documento dice | El archivo muestra |
|----------------|--------------------|
| "Base al 31 de diciembre de 2025" | 1.591 filas con `AGNO_FALLO`=2026 (FONDECYT Regular 680, Iniciación 433, Postdoctorado 256, Idea I+D 102, Startup Ciencia 85, ALMA 15; 1.369 de Proyectos de Investigación, 187 de Investigación Aplicada, 35 de Redes) |
| 5 subdirecciones | 7 rótulos: `REDES ESTRATEGIA Y CONOCIMIENTO` (5.899) y `REDES, ESTRATEGIA Y CONOCIMIENTO` (52, solo 2020+) son la misma; `NO APLICA` (2.484, todo pre-2010) |
| Colaboración 2016-2024 | trae adjudicaciones 2016-**2025** (4.442 en 2025) |
| README del histórico cita `BDH_Proyectos_Notas.pdf` | el archivo real es `BDH_HISTORICA_Notas.pdf` |
| `TIPO_BENEFICIARIO` | 6 valores: `PERSONA NATURAL` 37.187, `PERSONA JURIDICA` 11.558, `SIN INFORMACION` 201, `PERSONA NATURAL O PERSONA JURIDICA` 46, `NATURAL O JURIDICA` 15, `JURIDICA` 7 |
| `SEXO` | 3 valores en Histórico (`SIN INFORMACION` 611); en Becas 4: `HOMBRE`/`MUJER`/`FEMENINO` 739/`MASCULINO` 689 |

## 9. Licencias

`CC0-1.0` (dominio público, sin condiciones) en **7 repos**: Historico-de-Proyectos-Adjudicados, Colaboracion_Institucional, Postulaciones, Becas, Palabras_claves, Instructivo_descarga y Consulta-Publica-Politica-de-Acceso-Abierto. **FONDECYT-Abstracts no declara licencia** → si se usan sus abstracts, citar la fuente y no redistribuir el texto.

## 10. Correcciones posteriores a la Fase 1 (2026-10-09)

El código de `src/homologacion/` re-midió este perfilado. Tres cifras de la primera versión estaban cortas y quedaron corregidas arriba; el detalle y la razón:

| Cifra | Primera versión | Medida con el código | Por qué cambió |
|---|---|---|---|
| Filas sin monto | 2.423 | **2.425** | faltaban las 2 filas del literal `NO SOLICITA A CONICYT` y los 10 rótulos en pesos con valor vacío |
| RM 2020-2025 | $1.152.602 millones (6.058 filas) | **$1.160.514 millones** (6.093 filas) | las 94 filas `M$` son pesos y el primer filtro las excluía por buscar el texto "pesos" |
| Colisiones de institución | 411 / 117 | **373 / 21** | se cuentan sobre RUT válidos: el conteo anterior trataba el RUT vacío como un identificador compartido |

**Macrozona derivada (nuevo, verificado):** la derivación desde la región homologada coincide con `MACROZONA_MINCIENCIA` en **49.014 de 49.014** filas del histórico y **139.517 de 139.517** de postulaciones; en becas hay **1 excepción** (una fila con región Metropolitana y macrozona `CENTRO` en el archivo de ANID). El mapeo medido tiene dos diferencias con la agrupación que uno supondría: **Coquimbo va en `CENTRO`** (no en Norte) y **O'Higgins en `CENTRO SUR`** (no en Centro); la Región Metropolitana es macrozona propia (`RM`). Las 9 sumas por macrozona cuadran exactas contra el archivo.

**Roles institucionales (resuelto):** los 65 valores crudos se colapsan a 9 canónicos + `NO CLASIFICADO`, con **0 filas sin clasificar** en las 33.731 de Colaboración. `RESPONSABLE/PUBLICA` y `RESPONSABLE/PRIVADA` son el mismo rol (institución a cargo) y la distinción público/privado se conserva en el valor crudo.

**Codificación (nuevo, hallado por el manifiesto):** `FONDECYT-Abstracts/Abstract_Iniciación_2016_2025.csv` **no está en UTF-8** — está en latin-1 (falla con `byte 0xf3` en la posición 101). Los otros dos abstracts sí son UTF-8. Leer con cadena de respaldo `(utf-8-sig, utf-8, latin-1)` y anotar cuál funcionó; el manifiesto ahora muestra la codificación en la fila del archivo cuando no es la esperada.

**Inventario del corte (medido por `scripts/manifiesto.py`):** 13 CSV con **306.390 filas** + 12 XLSX espejo con el mismo contenido (no se suman: duplicarían cada base). Las 9 bases del perfilado son 293.629 filas; los 12.029 restantes son los 3 archivos de abstracts. La comparación automática CSV ↔ XLSX da **sin discrepancias**: si un formato se actualizara y el otro no, el manifiesto lo grita.

**Décima base, medida y fuera de alcance:** el repo `Consulta-Publica-Politica-de-Acceso-Abierto` trae `BBDD_Consulta_PAA..csv` — 732 respuestas × 62 columnas de la consulta pública de la Política de Acceso Abierto (nivel de acuerdo con objetivos y obligaciones, región, macrozona, institución, sexo, rango etario, sector). **No es dato de proyectos** y no entra al modelo del tablero; queda declarada porque existe y está medible. `Instructivo_descarga` solo aporta un PDF de instrucciones, cero datos.
