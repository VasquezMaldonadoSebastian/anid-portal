# Plan de trabajo — Tablero ANID-Portal

**Fecha:** 2026-10-09 · **Versión:** 1.1 · **Estado:** APROBADO (decisiones cerradas 2026-10-09)
**Proyecto:** `Repositorio Proyectos\anid-portal` (C: en este equipo)
**Base medidas:** `docs/datos.md` (perfilado del 2026-10-09) y `docs/homologacion.md` (reglas H1-H8)

## Decisiones cerradas (2026-10-09)

| Decisión | Valor | Consecuencia |
|---|---|---|
| Destino del tablero | **Streamlit** (app local; enlace solo si se decide publicar) | Fase 3 es código Python, no HTML ni .pbix. Verificación del render por navegador contra el servidor local |
| Alcance | **Completo** (opción B) | Incluye red de colaboración, embudo de postulaciones y ficha de institución |
| Montos | **Nominales en la ficha, reales (UF/IPC) en la serie temporal** | Se construye una tabla de deflactores anuales y el modelo expone `monto_clp` y `monto_clp_real` |
| Filas con fallo 2026 | **Filtrables, apagadas por defecto**, con aviso en el pie | La base se declara "al 31-dic-2025"; el 2026 entra solo si el usuario lo activa |

---

## Objetivo

Un tablero que permita responder, sin volver a tocar los CSV, preguntas como *"cuántos proyectos y cuánto monto adjudicó la Universidad de La Frontera en La Araucanía, en FONDECYT, entre 2020 y 2025, y cómo se compara con la macrozona Sur"*, con cifras que cuadren contra el dato crudo y que se puedan regenerar cuando ANID publique el próximo corte.

## Arquitectura

```text
data/crudo (CSV de ANID)  →  src/homologacion (reglas + tests)  →  modelo curado
                                                                        │
                                                    ┌───────────────────┴───────────────────┐
                                                    ▼                                       ▼
                                        payload pre-agregado (JSON)              export XLSX interno
                                                    ▼
                                    app Streamlit (filtros + vistas)
```

**Principio rector:** el dato se limpia en código versionado y con tests, no en una planilla aparte. Es lo único que no se reconstruye solo cuando llega el corte nuevo.

## Stack

Python 3.11 · pandas 2.3.3 · openpyxl 3.1.5 · pytest · **Streamlit** (aplicación y filtros) · tabla de deflactores UF/IPC anuales (fuente a fijar en la Tarea 2.6).

## Lo que NO entra en este plan

- **Tasa de adjudicación por institución** — no existe el denominador (85.958 filas / 85.907 códigos con estado `NO ADJUDICADO`, sin institución en ninguna base). Solo por región, y separando proyectos de becas.
- **Jerarquía universidad → facultad/campus** — el dato entrega razón social, no unidades internas. Si se necesita, es un trabajo aparte con una tabla externa.
- **Datos personales** (nombres de responsables y co-investigadores): el tablero agrega por institución y región, sin nombres de personas.

---

## Fase 0 — Dejar el proyecto operable (≈1 h)

Objetivo: que cualquiera pueda reproducir el estado medido y traer el próximo corte sin depender de esta sesión.

### Tarea 0.1 — Script de refresco del corte
- **Crear:** `scripts/refrescar-corte.sh` (clona o actualiza los 8 repos en `data/crudo/`) y `scripts/manifiesto.py` (filas reales por archivo, tamaño, sha256, fecha → `data/crudo/_manifiesto.md`).
- **Verificación:** `bash scripts/refrescar-corte.sh` y `grep -c "sha256" data/crudo/_manifiesto.md` → ≥ 10.
- **Por qué:** hoy los clones no tienen registro de fecha ni hash; sin esto el próximo corte se analiza sobre una copia sin trazabilidad.

### Tarea 0.2 — Test de humo de las fuentes
- **Crear:** `tests/test_fuentes.py` — cada base carga con `sep=';'`, `encoding='utf-8-sig'` y devuelve exactamente las filas medidas (49.014 / 136 / 33.731 / 20.620 / 139.517 / 1.205 / 19.288 / 12.873 / 17.245).
- **Comando:** `py -3.11 -m pytest tests/test_fuentes.py -q` → 9 passed.

### Tarea 0.3 — Reemplazar el test de humo del scaffold
- **Modificar:** `tests/test_smoke.py` (hoy es un `assert True`).

**Gate de Fase 0:** manifiesto con los 8 repos · 9 tests de fuentes en verde · `AGENTS.md` sin placeholders (✅ ya escrito) · commit.

> ✅ **Cerrada el 2026-10-09.** `scripts/refrescar-corte.sh` operativo (actualiza 6 clones + trae los 2 que faltaban) y `data/crudo/_manifiesto.md` con filas, tamaño, sha256 y fecha por archivo. 9 tests de fuentes + 2 de estructura en verde.

---

## Fase 1 — Homologación (≈7 h) · el núcleo

Objetivo: que cada etiqueta del crudo caiga en una categoría canónica **sin perder filas en silencio**. Un módulo por regla, cada uno con tres tests: (a) transforma el caso sucio, (b) no toca el caso limpio, (c) **cuadre**: el conteo de filas de entrada = el de salida.

Patrón (se escribe completo en H1 y se repite en las demás):

```python
# tests/test_homologacion_region.py
def test_region_homologa_variante_de_rm():
    assert homologar_region("REGION METROPOLITANA DE SANTIAGO") == "METROPOLITANA"

def test_region_no_toca_caso_limpio():
    assert homologar_region("REGION DE VALPARAISO") == "VALPARAISO"

def test_region_no_pierde_filas():
    crudo = pd.read_csv(HISTORICO, sep=";", encoding="utf-8-sig", dtype=str)
    assert len(crudo) == 49014
    assert crudo["REGION_EJECUCION"].map(homologar_region).notna().all()
```

| Tarea | Módulo | Cifras de control (deben dar exacto) |
|---|---|---|
| 1.1 Región (H1) | `src/homologacion/region.py` | RM = **27.212** (crudo 26.334) · Ñuble = 57 · total 49.014 sin pérdidas |
| 1.2 Macrozona derivada + control (H2) | `src/homologacion/macrozona.py` | 0 excepciones contra `MACROZONA_MINCIENCIA` en histórico (49.014) y postulaciones (139.517) · 1 excepción declarada en becas (RM con macrozona `CENTRO` en el archivo) |
| 1.3 Moneda y monto (H3) | `src/homologacion/moneda.py` | 2.425 filas sin monto · 38 en euros · RM 2020-2025 = **$1.160.514 millones** (6.093 filas) · país $2.095.227 millones |
| 1.4 Subdirección (H4) | `src/homologacion/subdireccion.py` | 7 rótulos → 6 destinos, sin pérdida |
| 1.5 Beneficiario y sexo (H5) | `src/homologacion/categorias.py` | 6 → 4 categorías (mixtos declarados) · 1.428 sexo normalizado en Becas |
| 1.6 Institución (H6) | `src/homologacion/institucion.py` | Histórico 1.749 → 1.733 · Colaboración 5.694 → 5.574 · RUT válidos 2.476 · colisiones 373/21 (no 411/117) |
| 1.7 Rol institucional (H7) | `src/homologacion/roles.py` | 33.731 filas mantenidas · 65 valores crudos → 9 canónicos · 0 sin clasificar |
| 1.8 Unidad de conteo (H8) | `src/homologacion/metricas.py` | 49.014 filas / 48.707 códigos / 136 códigos repetidos |
| 1.9 Informe de cuadre | `docs/evidencia/cuadre-homologacion.md` | esperado = obtenido en todas las filas |

**Gate de Fase 1:** 0 filas perdidas en las 4 bases · todas las cifras de control reproducidas · etiqueta sin clasificar reportada (no absorbida) · `pytest` en verde · `@revisar` independiente contra `docs/datos.md`.

> ✅ **Cerrada el 2026-10-09.** 145 tests en verde. 0 filas perdidas y 0 etiquetas sin clasificar en región (las 4 bases), subdirección, beneficiario/sexo y roles. Cuadre completo en `docs/evidencia/cuadre-homologacion.md` + tabla de decisiones de `docs/evidencia/instituciones-colisiones.md`. Tres cifras del primer perfilado quedaron corregidas (`docs/datos.md` §10). Pendiente el `@revisar` independiente: se hará junto con el de la Fase 3, contra los entregables del tablero (criterio del usuario).

---

## Fase 2 — Modelo curado (≈5 h)

| Tarea | Entregable | Verificación |
|---|---|---|
| 2.1 Esquema | `docs/modelo.md` (hechos, dimensiones, granularidad, unidad de conteo por métrica) | esquema declarado antes de codificar |
| 2.2 ETL proyectos | `src/modelo/proyectos.py` | 49.014 filas de entrada → hecho con la diferencia explicada |
| 2.3 Red de colaboración | `src/modelo/colaboracion.py` | proyecto × institución × rol homologado, con región y país |
| 2.4 Embudo de postulaciones | `src/modelo/postulaciones.py` | tasa global de proyectos = **26,8%** (68.133) y tabla por región reproducida |
| 2.5 Becas | `src/modelo/becas.py` | 19.288 filas, institución y región de origen homologadas |
| 2.6 Deflactores UF/IPC | `src/modelo/deflactores.py` + `config/deflactores.csv` | serie anual usada, con fuente y fecha citadas; montos reales = nominal / factor del año |
| 2.7 Export y validación | `src/modelo/exportar.py` → `outputs/*.parquet` + validador | validador re-cuenta y compara contra `docs/datos.md`: 100% en verde |

**Gate de Fase 2:** validador en verde · tamaño del payload medido y reportado · esquema documentado.

> ✅ **Cerrada el 2026-10-09.** `docs/modelo.md` declara el esquema (tablas, granularidad, unidades de conteo, invariantes y lo que el modelo no responde). El hecho queda en 49.014 filas × 24 columnas y salen 4 agregados (`agg_region` 1.820 · `agg_institucion` 7.678 · `agg_programa` 1.119 · `tasa_region` 174) más la dimensión de 6.094 instituciones. Deflactores del **Banco Mundial** (`FP.CPI.TOTL`, base 2010) en `config/deflactores.csv`; se usó IPC en vez de UF porque la serie de UF de `mindicador.cl` llegaba incompleta. `scripts/validar-modelo.py` reproduce **43 de 43 cifras de control** (`docs/evidencia/validacion-modelo.md`), incluidas las tres corregidas del informe (2.425 filas sin monto · $1.160.514 millones RM 2020-2025 · 373/21 colisiones). 157 tests en verde. Payload medido: `outputs/` = **4,1 MB en parquet** (lo que consume la app) y 63,6 MB si se cuentan los CSV de espejo para Excel; `_meta.json` lleva el conteo por tabla. Apareció un fallo intermitente del entorno al agregar (regla R9 de `AGENTS.md`): toda agregación pasa por `src/modelo/agregar.py`.

---

## Fase 3 — Tablero Streamlit (≈8 h)

### Tareas
- **3.1** `src/tablero/app.py` — esqueleto de la app: carga del payload, barra lateral de filtros (región, macrozona, institución, año, subdirección, programa, instrumento), y estado inicial con 2026 apagado.
- **3.2** Filtros en cascada coherentes: al elegir región, el ranking de instituciones se acota; al elegir institución, se declara si tiene proyectos en más de una región (R5).
- **3.3** Vista 1 — Panorama territorial: proyectos y montos por macrozona y región, con selector de métrica (filas / códigos / proyectos).
- **3.4** Vista 2 — Ranking institucional: top N + fila "otras (N instituciones)" con su conteo, para no ocultar la cola larga (R8).
- **3.5** Vista 3 — Serie temporal: por año, instrumento y subdirección, con interruptor nominal/real (UF/IPC) y advertencia de moneda.
- **3.6** Vista 4 — Ficha de institución: proyectos, monto total nominal, instrumentos principales, regiones en que aparece, evolución anual.
- **3.7** Vista 5 — Red de colaboración y embudo de postulaciones (alcance completo): co-participación por institución y tasa de adjudicación **solo por región**.
- **3.8** Avisos permanentes: unidad de conteo en cada tarjeta, fecha real del corte y hash en el pie, nota de 2026, nota de moneda.
- **3.9** Diseño por tokens: `DESIGN.md` + `tokens.css`-equivalente en `.streamlit/config.toml` y paleta definida en un solo módulo (`src/tablero/estilo.py`); cero colores incrustados en las vistas.
- **3.10** Verificación del render: levantar la app, cargarla en el navegador y comprobar por DOM que las vistas y las cifras aparecen (no basta con que el proceso arranque).

**Gate de Fase 3:** las cifras del tablero cuadran contra `outputs/` · toda tarjeta declara su unidad de conteo · la cola larga visible o declarada · render verificado · `@revisar` antes de mostrarlo a terceros.

---

## Fase 4 — Cierre y entrega (≈2 h)

- **4.1** Auditoría `@revisar` contra `docs/datos.md` (informe al chat, no al repo).
- **4.2** `README` del tablero (cómo se levanta) + `MEMORIA.md` con el estado final.
- **4.3** Decisión del usuario: publicar o quedarse en local. Licencia CC0 permite ambas.
- **4.4** Nombrar la sesión y dejar el punto de retorno en `MEMORIA.md`.

---

## Riesgos y cómo se cubren

| # | Riesgo | Impacto | Mitigación |
|---|--------|---------|------------|
| 1 | ANID publica un corte nuevo a mitad de trabajo | cifras mezcladas de dos cortes | cada fase fija el sha256 del archivo de entrada (`_manifiesto.md`) y lo re-verifica al cerrar |
| 2 | Etiqueta de región nueva en el próximo corte | filas que desaparecen del agrupamiento | el normalizador devuelve `NO CLASIFICADO` y el test de cuadre falla: se ve, no se absorbe |
| 3 | Colisiones de nombres de institución (373 RUT con >1 nombre y 21 nombres con >1 RUT) | rankings con la misma institución partida | tabla de decisiones del usuario + clave por RUT cuando existe |
| 4 | Deflactores: fuente y actualización | serie real mal calculada | Tarea 2.6 fija la fuente, la guarda en `config/deflactores.csv` y cita la fecha; el factor se versiona |
| 5 | Cola larga invisible en un "top 10" | 88% de las instituciones queda fuera sin que se note | fila "otras (N instituciones)" con su conteo en cada ranking |
| 6 | Streamlit no instalado en el intérprete de trabajo | la app no arranca | ✅ verificado: `streamlit 1.58` presente en `py -3.11` (junto con `pyarrow`) |
| 7 | Datos personales (nombres de investigadores) | problema de privacidad si se publica | el tablero agrega por institución y región; sin nombres de personas |
| 8 | El entorno (pandas 2.3.3 + numpy 2.4.6) deja etiquetas inaccesibles después de un `groupby`, **de forma intermitente** | agregados silenciosamente distintos entre corridas | toda agregación del proyecto pasa por `src/modelo/agregar.py` (arrays + orden por posición); la Fase 3 debe usar ese módulo y **no** `sort_values(by=…)` sobre un agregado recién hecho |

---

## Alcance: opción elegida

**B — Completo** (red de colaboración, embudo de postulaciones, ficha de institución y abstracts FONDECYT). Estimación ≈ 20 h de trabajo efectivo.

---

## Nota sobre el orden

La homologación no es un trámite previo: es el producto. Si se salta, el tablero muestra la RM con 26.334 proyectos en vez de 27.212 y nadie lo nota hasta que alguien compara con la macrozona. Por eso la Fase 1 va antes de cualquier gráfica.
