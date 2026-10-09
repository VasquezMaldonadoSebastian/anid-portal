# Modelo curado (Fase 2)

**Qué es:** el conjunto de tablas que consume el tablero, construidas desde `data/crudo/` con las
reglas de `src/homologacion/` (Fase 1). Todo lo que está acá se reconstruye con un comando y se
verifica contra cifras de control; nada se edita a mano.

```bash
py -3.11 scripts/deflactores.py        # configura la serie de IPC (una vez por corte, si cambia)
py -3.11 scripts/construir-modelo.py   # data/crudo/ → outputs/  (~40 s)
py -3.11 scripts/validar-modelo.py     # outputs/ → 43 cifras de control → docs/evidencia/
```

`outputs/` **no se versiona** (se regenera); la evidencia de la validación sí
(`docs/evidencia/validacion-modelo.md`) y la serie de deflactores también (`config/deflactores.csv`).
Cada tabla sale dos veces: `.parquet` (4,1 MB en total, es lo que consume la app) y `.csv` con `;`
(63,6 MB, sólo para abrir en Excel).

## Regla transversal: la unidad de conteo viaja con el número

En el histórico hay **49.014 filas**, **48.707 códigos de proyecto** y **48.835 pares
(código, año)**: 443 filas repiten el código y 136 códigos aparecen con contenido distinto. Por eso
cada tabla del modelo expone las tres unidades por separado y **ninguna tarjeta del tablero puede
mostrar un número sin decir cuál usa**:

| Columna | Qué cuenta | Regla |
|---|---|---|
| `filas` | filas del histórico | es lo que la fuente publica |
| `codigos` | códigos distintos | un código puede ocupar varias filas |
| `proyectos` | pares (código, año) distintos | unidad de proyecto del tablero |
| `monto_clp` | pesos nominales **sólo de filas con monto válido** | las sin monto suman 0 y se cuentan en `filas_sin_monto` |
| `monto_clp_real` | pesos del año base del deflactor | nulo si el año no tiene IPC (2026) |
| `filas_sin_monto` | filas sin monto en pesos | visible, no oculta |
| `filas_sin_deflactor` | filas con monto pero sin IPC del año | 2026: filtrable y apagado por defecto |

## Tablas

### `proyectos.parquet` — el hecho (49.014 filas × 24 columnas)

Una fila por registro del histórico homologado. Es el eje del tablero: todo lo territorial y el
ranking institucional salen de acá.

| Columna | Tipo | Nota |
|---|---|---|
| `codigo_proyecto` | texto | código ANID; 443 filas repiten código |
| `anno_fallo`, `anno_concurso` | entero | 1982→2026 (`anno_fallo` 2026 = filtrable, apagado) |
| `subdireccion`, `programa`, `instrumento`, `nombre_concurso` | texto | de la fuente, con subdirección homologada |
| `area_ocde`, `disciplina`, `duracion_meses`, `tipo_beneficiario`, `sexo` | — | contexto de la ficha |
| `institucion` | texto | nombre tal como llega (1.749 valores) |
| `institucion_normalizada` | texto | 1.733 valores (sólo se unifican variantes de escritura) |
| `institucion_clave` | texto | 1.707 claves: `RUT:…` si el RUT es deducible desde Colaboración, si no `NOMBRE:…` |
| `rut_deducido` | bool | la clave viene de un RUT inferido, no declarado en el histórico |
| `region`, `macrozona` | texto | homologadas (0 sin clasificar); la macrozona se deriva de la región |
| `moneda` | texto | `PESOS`, `MILES DE PESOS`, `EUROS`, `SIN MONTO` |
| `monto_clp` | real | nominal en pesos; **0 cuando no hay monto válido** |
| `monto_clp_real` | real | pesos del año base del deflactor; nulo si el año no tiene IPC |
| `deflactor` | real | multiplicador aplicado (1,0 en el año base) |
| `monto_valido` | bool | 46.551 filas válidas en pesos; 38 en euros; 2.425 sin monto |
| `monto_cientifico` | bool | 1 fila: la celda del corte que viene como `2E+05` (código 1261710) |
| `codigo_repetido` | bool | marca las 443 filas del caso D3 |

**Invariantes verificadas:** ninguna región sin clasificar (0), ninguna fila sin macrozona (0), monto
nominal del país $4.978.171.451.662 en 46.551 filas, y las cifras de región/año coinciden con el
informe (`docs/datos.md`).

**Celda en notación científica.** El corte trae **una** celda de monto escrita por Excel en notación
científica: `2E+05` (código 1261710, FONDECYT Regular, fallo 2026, rótulo `MILES DE PESOS (M$)`), igual
en el CSV y en el XLSX espejo de ANID. Se interpreta tal como está escrita —200.000 miles de pesos =
$200.000.000— y se marca en `monto_cientifico` para que se pueda contar. Un `re.sub` genérico deja
`205` y publica el monto mil veces menor: esa era la diferencia de $199.795.000 que arrastraba la suma
nominal del país.

### `colaboracion.parquet` — red institucional (33.731 filas)

16.426 proyectos, 5.574 nombres de institución, 2.476 RUT válidos, 9 roles canónicos. `rol_original`
conserva el rótulo de la fuente para auditar la homologación. Trae país (71) y región de la
institución, no la del proyecto: **no** se usa para territorial.

### `postulaciones.parquet` — embudo (139.517 filas)

68.133 postulaciones de proyectos (sin Capital Humano) y 18.233 adjudicadas → **26,76%** de tasa.
`estado` es el texto de la fuente y `adjudicado` el booleano homologado. Es la única base con
denominador completo, pero **no identifica institución**: la tasa es por región, nunca por
institución.

### `becas.parquet` — Capital Humano (19.288 filas)

2015→2025, con región de origen (no de ejecución), sexo y tipo de beneficiario homologados. Cubre el
92% de las adjudicaciones de Capital Humano, por eso se declara aparte y no se suma con el hecho.

### `dim_institucion.parquet` — dimensión (6.094 filas)

`institucion_clave` → `nombre_visible`, `rut`, `pais`, `region`, `macrozona`, `n_regiones`, y dos
banderas (`en_historico` 1.707 · `en_colaboracion` 5.022) con sus conteos. **21 nombres homónimos**
quedan repartidos en claves distintas: la dimensión no los fusiona, los deja distinguibles por RUT.

### Agregados: `agg_region`, `agg_institucion`, `agg_programa`, `tasa_region`

Pre-agregados para que el tablero filtre sin recalcular el hecho en cada interacción.

| Tabla | Filas | Claves |
|---|---|---|
| `agg_region.parquet` | 1.820 | región × macrozona × año × subdirección |
| `agg_institucion.parquet` | 7.678 | institución × año × región × subdirección (+ `institucion` visible) |
| `agg_programa.parquet` | 1.119 | año × subdirección × programa × instrumento |
| `tasa_region.parquet` | 174 | región × macrozona × año |

Las tres primeras llevan las siete medidas del cuadro de unidades; la cuarta lleva
`postulaciones`, `adjudicadas` y `tasa` (porcentaje). Los agregados **no** reemplazan al hecho: la
ficha de institución y cualquier tabla con detalle se calculan sobre `proyectos.parquet`.

### `_meta.json` — trazabilidad

Fecha del corte, sha256 del manifiesto, fuente y base de los deflactores, conteo de cada tabla, tasa
global y tres notas fijas (nominal vs real, 2026 sin IPC, y que filas ≠ códigos ≠ proyectos).

## Deflactores

`config/deflactores.csv`: IPC anual de Chile, **Banco Mundial `FP.CPI.TOTL`**, base **2010 = 100**,
1980→2025, consultado el 2026-10-09 (URL de la fuente en el propio archivo). Se descartó
`mindicador.cl` porque su serie de UF por año llegaba incompleta.

```text
monto_clp_real = monto_clp × IPC(año base) / IPC(año del fallo)
```

El **año base es 2010** (`base` del archivo de deflactores, con IPC 2010 = 100) y queda congelado: si
se cambia, hay que reconstruir el modelo y volver a validar. Consecuencia que hay que leer bien: los
montos «reales» del tablero están en **pesos de 2010**, no de 2025, así que la suma real de 2025 no
coincide con su suma nominal (el factor entre ambas es IPC(2010)/IPC(2025) = 0,539). Cada tarjeta
declara su base para que no se confundan. **2026 no tiene IPC anual cerrado**, así que sus 1.578 filas
con monto quedan con `monto_clp_real` nulo y contadas en `filas_sin_deflactor` — la serie temporal las
excluye y el pie del tablero lo avisa.

## Trampa del entorno que el modelo evita a propósito

En este equipo (pandas 2.3.3 + numpy 2.4.6 sobre Python 3.11, Windows) aparece **de forma
intermitente** un fallo reproducible con pandas puro y datos sintéticos: después de un
`groupby(...).agg(...).reset_index()`, `"col" in agg.columns` responde `True` mientras
`agg["col"]` o `sort_values(["col"])` levantan `KeyError`. Va y viene entre procesos con el mismo
código y los mismos datos, así que puede producir resultados silenciosamente distintos.

Por eso **todo el modelo agrega con `src/modelo/agregar.py`**, que extrae las claves del índice como
arrays, construye el resultado como un DataFrame nuevo con nombres propios y ordena por posición
(`np.lexsort` + `iloc`). `AGENTS.md` §2 lo deja como regla: después de un `groupby`, no se busca por
etiqueta. `tests/test_modelo_agregar.py` fija el comportamiento del agregador.

## Qué no responde este modelo

- **Tasa de adjudicación por institución:** no existe denominador. La base de postulaciones no
  identifica institución (85.958 de sus filas están `NO ADJUDICADO` — 85.907 códigos — y 16.648
  `FUERA DE BASE`, ninguna con institución), así que la tasa se calcula por región y sólo sobre
  proyectos.
- **Montos por institución como serie larga:** el histórico no declara RUT, así que la clave de 1.707
  instituciones es una reconstrucción por nombre + RUT deducido; las 21 colisiones homónimas se
  reportan, no se resuelven.
- **Becas sumadas al hecho:** son universos distintos (personas vs proyectos) y comparten 92% con
  Capital Humano; se muestran en su propia vista.
