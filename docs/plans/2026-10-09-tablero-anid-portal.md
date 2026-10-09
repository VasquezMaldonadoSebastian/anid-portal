# Plan de trabajo — Tablero ANID-Portal

**Fecha:** 2026-10-09 · **Versión:** 1.0 · **Estado:** pendiente de aprobación del usuario
**Proyecto:** `A:\Repositorio Proyectos\anid-portal`
**Base medidas:** `docs/datos.md` (perfilado del 2026-10-09) y `docs/homologacion.md` (reglas H1-H8)

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
                                        tablero (HTML estático o Power BI)
```

**Principio rector:** el dato se limpia en código versionado y con tests, no en una planilla aparte. Es lo único que no se reconstruye solo cuando llega el corte nuevo.

## Stack

Python 3.11 · pandas 2.3.3 · openpyxl 3.1.5 · pytest · (Fase 3) payload JSON + HTML/D3 o Power BI Desktop.

## Lo que NO entra en este plan

- **Tasa de adjudicación por institución** — no existe el denominador (85.907 postulaciones no adjudicadas sin institución en ninguna base). Solo por región, y separando proyectos de becas.
- **Jerarquía universidad → facultad/campus** — el dato entrega razón social, no unidades internas. Si se necesita, es un trabajo aparte con una tabla externa.
- **Datos personales** (nombres de responsables y co-investigadores): no se publican ni se agregan por persona en el tablero. Si se quiere un panel de género, se hace con conteos agregados y sin nombres.

---

## Fase 0 — Dejar el proyecto operable (≈1 h)

Objetivo: que cualquiera pueda reproducir el estado medido y traer el próximo corte sin depender de esta sesión.

### Tarea 0.1 — Escribir `AGENTS.md`
- **Archivo:** `AGENTS.md` (reemplaza los placeholders del scaffold).
- **Verificación:** `grep -c "<" AGENTS.md` → sin placeholders de sección; las 8 secciones con contenido.
- **Estado:** contenido redactado; **bloqueado por autorización de escritura**.

### Tarea 0.2 — Script de refresco del corte
- **Crear:** `scripts/refrescar-corte.sh`
- **Hace:** para cada uno de los 8 repos, `gh repo clone --depth 1` si no existe o `git pull` si existe; luego escribe `data/crudo/_manifiesto.md` con: repo, archivo, filas, tamaño, sha256, fecha de descarga.
- **Verificación:**
  ```bash
  bash scripts/refrescar-corte.sh
  grep -c "Historico-de-Proyectos-Adjudicados" data/crudo/_manifiesto.md   # ≥1
  ```
- **Riesgo que cubre:** que el próximo análisis no se haga sobre una copia sin trazabilidad (hoy los clones vienen de un `--depth 1` sin registro de fecha).

### Tarea 0.3 — Test de humo de las fuentes
- **Crear:** `tests/test_fuentes.py`
- **Qué prueba:** que cada base carga con `sep=';', encoding='utf-8-sig'` y devuelve exactamente las filas de `docs/datos.md` (49.014 / 33.731 / 20.620 / 139.517 / 19.288 / 12.873 / 17.245 / 1.205 / 136).
- **Comando:** `py -3.11 -m pytest tests/test_fuentes.py -q` → 9 passed.
- **Por qué:** cualquier corte nuevo que cambie el conteo se detecta en un comando, no releyendo documentos.

### Tarea 0.4 — Reemplazar el test de humo del scaffold
- **Modificar:** `tests/test_smoke.py` (hoy es un `assert True`).
- **Verificación:** `py -3.11 -m pytest tests/ -q` sin fallos.

**Gate de Fase 0:** manifiesto generado con los 6 repos principales · 9 tests de fuentes en verde · `AGENTS.md` sin placeholders · commit.

---

## Fase 1 — Homologación (≈6-8 h) · el núcleo

Objetivo: que cada etiqueta del crudo caiga en una categoría canónica **sin perder filas en silencio**. Un módulo por regla, cada uno con tres tests: (a) transforma el caso sucio, (b) no toca el caso limpio, (c) **cuadre**: el conteo de filas de entrada = el de salida.

Patrón de implementación (se repite en cada regla; se escribe completo solo en H1 como molde):

```python
# tests/test_homologacion_region.py
def test_region_homologa_variante_de_rm():
    assert homologar_region("REGION METROPOLITANA DE SANTIAGO") == "METROPOLITANA"

def test_region_no_toca_caso_limpio():
    assert homologar_region("REGION DE VALPARAISO") == "VALPARAISO"

def test_region_no_pierde_filas():
    crudo = pd.read_csv(HISTORICO, sep=";", encoding="utf-8-sig", dtype=str)
    assert len(crudo.assign(r=crudo["REGION_EJECUCION"].map(homologar_region))) == 49014
```

### Tarea 1.1 — Región (H1)
- **Crear:** `src/homologacion/region.py`, `tests/test_homologacion_region.py`
- **Función:** `homologar_region(valor) -> str` con las 24 etiquetas mapeadas a 16 regiones + `SIN INFORMACION` / `EXTRANJERO` / `MULTIREGIONAL`.
- **Cifras de control (deben dar exacto):**
  - RM = **27.212** (crudo 26.334)
  - Ñuble (Histórico) = **57** (42 + 15)
  - Total de filas = **49.014**, sin pérdidas
  - La macrozona derivada debe reproducir `MACROZONA_MINCIENCIA` en **todas** las filas (0 excepciones)
- **Aplicar también a** Postulaciones, Becas y Colaboración (cada una usa otra convención: `BIO-BIO`, `ÑUBLE` con tilde).

### Tarea 1.2 — Macrozona derivada + control cruzado (H2)
- **Crear:** `src/homologacion/macrozona.py`
- **Función:** `macrozona_de_region(region) -> str`; más `verificar_macrozona(df) -> DataFrame` que devuelve las filas donde la macrozona derivada difiere de la del archivo.
- **Verificación:** el DataFrame de excepciones debe estar **vacío** en las 49.014 filas del histórico y en las 19.288 de becas.

### Tarea 1.3 — Moneda y monto (H3)
- **Crear:** `src/homologacion/moneda.py`, `tests/test_homologacion_moneda.py`
- **Funciones:** `es_pesos(rotulo)`, `a_pesos(valor, rotulo)`, `marcar_monto_valido(df)`
- **Casos:** los 4 rótulos de miles de pesos → ×1.000; `EUROS` → columna aparte, nunca sumada; vacío y `NO SOLICITA A CONICYT` → `monto_valido=False`.
- **Cifras de control:** 2.423 filas sin monto · 38 filas en euros · RM 2020-2025 = **$1.152.602 millones** (11.301 filas de 11.782).

### Tarea 1.4 — Subdirección (H4)
- **Crear:** `src/homologacion/subdireccion.py`
- **Casos:** `REDES, ESTRATEGIA Y CONOCIMIENTO` y `REDES ESTRATEGIA Y CONOCIMIENTO` → una sola; `NO APLICA` se mantiene.
- **Cifra de control:** 7 rótulos crudos → 6 destinos; conteo por destino sin pérdida.

### Tarea 1.5 — Tipo de beneficiario y sexo (H5) · **decisión del usuario**
- **Crear:** `src/homologacion/categorias.py`
- **Casos:** `NATURAL O JURIDICA` (15) y `PERSONA NATURAL O PERSONA JURIDICA` (46) → hay que decidir si van a una categoría mixta propia o a `SIN INFORMACION`; `FEMENINO` (739) y `MASCULINO` (689) en Becas → `MUJER`/`HOMBRE`.
- **Bloqueo:** la decisión de los mixtos la toma el usuario (no se resuelve en silencio).

### Tarea 1.6 — Institución (H6)
- **Crear:** `src/homologacion/institucion.py`
- **Funciones:** `normalizar_nombre(texto)` (sin tildes, sin puntuación, espacios colapsados) y `clave_institucion(nombre, rut)` (el RUT manda cuando existe).
- **Salidas además de la función:** `docs/evidencia/instituciones-colisiones.md` con los 411 RUT con más de un nombre y los 117 nombres con más de un RUT, para decisión del usuario.
- **Cifras de control:** Histórico 1.749 → 1.733 · Colaboración 5.694 → 5.574 · RUT 2.501 → 2.477.

### Tarea 1.7 — Rol institucional (H7)
- **Crear:** `src/homologacion/roles.py` + tabla de equivalencias versionada (65 valores crudos → ~8 canónicos).
- **Cifra de control:** el conteo total de filas se mantiene en 33.731; cada valor crudo queda mapeado (los no clasificados se listan, no se absorben).

### Tarea 1.8 — Unidad de conteo (H8)
- **Crear:** `src/homologacion/metricas.py`
- **Funciones:** `contar_filas(df)`, `contar_codigos(df)`, `contar_proyectos(df)` (código + año) — las tres que el tablero va a mostrar por separado.
- **Cifra de control:** Histórico 49.014 / 48.707 / 48.7xx (proyectos) con los 136 códigos repetidos documentados.

### Tarea 1.9 — Informe de cuadre
- **Crear:** `docs/evidencia/cuadre-homologacion.md` — tabla con cada cifra de control de `docs/homologacion.md`, su valor esperado y el obtenido.
- **Verificación:** todas las filas del informe en "obtenido = esperado".

**Gate de Fase 1:** 0 filas perdidas en las 4 bases · todas las cifras de control reproducidas · toda etiqueta sin clasificar reportada (no absorbida) · `pytest` en verde · `@revisar` independiente contra `docs/datos.md`.

---

## Fase 2 — Modelo curado (≈4 h)

Objetivo: una tabla lista para graficar, con las dimensiones que el usuario pidió y los conteos ya resueltos.

### Tarea 2.1 — Esquema
- **Crear:** `docs/modelo.md` con el esquema declarado: hechos y dimensiones, granularidad de cada uno, unidad de conteo de cada métrica.
- **Regla:** una fila del hecho = un proyecto adjudicado (código + año), con institución, región, macrozona, subdirección, programa, instrumento, disciplina, monto normalizado.

### Tarea 2.2 — ETL del histórico
- **Crear:** `src/modelo/proyectos.py`
- **Verificación:** 49.014 filas de entrada → 49.014 filas de hecho (o las que resulten de definir la granularidad, con la diferencia explicada).

### Tarea 2.3 — Red de colaboración
- **Crear:** `src/modelo/colaboracion.py`
- **Salida:** tabla proyecto × institución × rol homologado, con región y país de cada institución.

### Tarea 2.4 — Embudo de postulaciones
- **Crear:** `src/modelo/postulaciones.py`
- **Regla:** separar proyectos de Capital Humano; unir Adjudicado con Becas para las becas.
- **Verificación:** tasa global de proyectos = **26,8%** (68.133 postulaciones) y la tabla por región de `docs/datos.md` §7 reproducida.

### Tarea 2.5 — Export y validación
- **Crear:** `src/modelo/exportar.py` → `outputs/modelo.parquet` + `outputs/hechos.csv`
- **Verificación:** validador que re-cuenta desde el modelo y compara contra las cifras duras de `docs/datos.md` (una función por cifra).

**Gate de Fase 2:** validador 100% en verde · tamaño del payload medido y reportado · esquema documentado.

---

## Fase 3 — Tablero (≈6-10 h) · depende de una decisión del usuario

### Decisión previa obligatoria

| Opción | Cuándo conviene | Qué implica |
|--------|-----------------|-------------|
| **A. HTML estático + payload pre-agregado** | publicación web, enlace compartible, cero costo, cero servidor | payload JSON de pocos KB (no filas crudas); filtros región/macrozona/institución/año/instrumento y 3-4 vistas; verificación de render obligatoria |
| **B. Power BI Desktop** | uso interno del área, ya tienen Power BI/DADI | el modelo se entrega como CSV/parquet + el .pbix lo arma el área; menos control sobre la verificación del render |

Sin esta decisión la Fase 3 no arranca; las Fases 1 y 2 no dependen de ella.

### Tareas (aplican a la opción elegida)
- **3.1** Diseño visual por tokens si es web: `DESIGN.md` + `tokens.css` (cero valores hex incrustados en el código) y una paleta sobria para un público institucional/analítico.
- **3.2** Payload: `src/tablero/payload.py` → JSON pre-agregado por las dimensiones filtrables + un agregado "otros" para no ocultar la cola larga (1.542 instituciones con ≤3 proyectos).
- **3.3** Vistas mínimas: (1) panorama por macrozona/región, (2) ranking institucional con el total que queda fuera del top, (3) serie por año e instrumento, (4) ficha de institución (región, instrumento, evolución).
- **3.4** Reglas visibles en el tablero: unidad de conteo declarada en cada tarjeta, fecha real del corte en el pie, montos con su advertencia de moneda.
- **3.5** Verificación de render (si es web): asserts de DOM + captura, según el flujo ya conocido del proyecto.

**Gate de Fase 3:** las cifras del tablero cuadran contra `outputs/modelo` · toda tarjeta declara su unidad de conteo · la cola larga visible o declarada · `@revisar` antes de mostrarlo a terceros.

---

## Fase 4 — Cierre y entrega (≈2 h)

- **4.1** Auditoría `@revisar` contra `docs/datos.md` (informe al chat, no al repo).
- **4.2** `README` del tablero + `MEMORIA.md` con el estado final.
- **4.3** Decisión del usuario: publicar o quedarse en interno. Licencia CC0 permite ambas.
- **4.4** Nombrar la sesión y dejar el punto de retorno en `MEMORIA.md`.

---

## Riesgos y cómo se cubren

| # | Riesgo | Impacto | Mitigación |
|---|--------|---------|------------|
| 1 | ANID publica un corte nuevo a mitad de trabajo | cifras mezcladas de dos cortes | cada fase fija el hash del archivo de entrada (`_manifiesto.md`) y lo re-verifica al cerrar |
| 2 | Etiqueta de región nueva en el próximo corte | filas que desaparecen del agrupamiento | el normalizador devuelve `NO CLASIFICADO` y el test de cuadre falla: se ve, no se absorbe |
| 3 | Colisiones de nombres de institución (411 RUT con >1 nombre) | rankings con la misma institución partida | tabla de decisiones del usuario + clave por RUT cuando existe |
| 4 | Montos comparados entre años (nominal vs real) | conclusión falsa de "más plata" cuando es inflación | **decisión pendiente**: si el tablero compara montos en el tiempo, deflactar (UF/IPC) y declararlo |
| 5 | Cola larga invisible en un "top 10" | 88% de las instituciones queda fuera sin que se note | fila "otras" con su conteo en cada ranking |
| 6 | Que el 2026 entre o no al tablero | totales que no cuadran con lo publicado por ANID | **decisión pendiente** del usuario; el filtro de año lo resuelve sin re-trabajo |
| 7 | Datos personales (nombres de investigadores) | problema de privacidad si se publica | el tablero agrega por institución y región; sin nombres de personas |

---

## Decisiones que necesito de ti

1. **Destino**: HTML web o Power BI (bloquea solo la Fase 3).
2. **Montos**: ¿nominales o deflactados? (afecta Fase 2 y 3).
3. **2026**: las 1.591 filas con fallo 2026, ¿entran o quedan fuera? La base se declara "al 31-dic-2025".
4. **Categorías mixtas**: los 61 registros `NATURAL O JURIDICA` / `PERSONA NATURAL O PERSONA JURIDICA` y los 1.428 `FEMENINO`/`MASCULINO` de Becas: ¿colapsar a la categoría canónica o mantenerlos visibles?

---

## Alcance por opciones

| Opción | Qué incluye | Tiempo estimado |
|--------|-------------|-----------------|
| **A — Núcleo territorial** | Fases 0, 1 y 2 completas + Fase 3 con las vistas 1, 2 y 3 (sin ficha de institución) | ≈11-13 h |
| **B — Completo** | Todo lo anterior + red de colaboración (Tarea 2.3), embudo de postulaciones en el tablero, ficha de institución y abstracts FONDECYT | ≈16-18 h |
| **C — Solo cimientos** | Fases 0 y 1: el dato queda homologado y verificado, listo para cualquier salida | ≈7-9 h |

Recomendación: **A**. Entrega el valor que buscabas (filtros por región e institución con cifras que cuadran) sin arrastrar la complejidad de la red de colaboración, que se puede sumar después sobre el mismo modelo sin rehacer nada.

---

## Nota sobre el orden

La homologación no es un trámite previo: es el producto. Si se salta, el tablero muestra la RM con 26.334 proyectos en vez de 27.212 y nadie lo nota hasta que alguien compara con la macrozona. Por eso la Fase 1 va antes de cualquier gráfica.
