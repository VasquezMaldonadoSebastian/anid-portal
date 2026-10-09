# MEMORIA del Proyecto — ANID-Portal

**Estado:** Fases 0, 1, 2 y 3 cerradas · **auditoría independiente (Fase 4) ejecutada y sus hallazgos corregidos** · pendiente: tus decisiones de publicación
**Stack:** Python 3.11 · pandas 2.3.3 · openpyxl 3.1.5 · **Streamlit 1.58** (tablero)
**Path:** `Repositorio Proyectos\anid-portal` (C: en este equipo)
**Actualizado:** 2026-10-09

## Descripción

Tablero para explorar la cartera de proyectos adjudicados por ANID (1982→2026) con filtros y agrupaciones por región, macrozona e institución, sobre los 8 repositorios públicos de la cuenta `ANID-GITHUB` (CC0-1.0). Origen: revisión de factibilidad pedida por el usuario sobre el conjunto completo de repositorios (09-oct-2026).

## Arquitectura

```text
github.com/ANID-GITHUB ──clone──> data/crudo/ ──src/homologacion──> modelo curado ──> app Streamlit
   (8 repos, CC0)                   (137 MB)        (Fase 1 ✅)         (Fase 2 ✅)      (Fase 3)
```

## Cambios

### v0.5.0 (2026-10-09) — Fase 4: auditoría independiente y correcciones
- **Tres auditores independientes** (contexto aislado, sin permiso de escritura sobre el repo) revisaron el modelo, el tablero y la documentación/publicabilidad. Del informe salieron **defectos reales, no cosméticos** — los cinco corregidos con su test o su chequeo:
  - **Monto del país mal parseado**: una celda del corte viene en notación científica (`2E+05`, código 1261710, FONDECYT Regular 2026) y el `re.sub` la dejaba en `205` → $205.000 en vez de $200.000.000. Se interpreta tal cual y se marca en la columna `monto_cientifico`; la suma nominal del país queda en **$4.978.171.451.662** (antes publicaba $4.977.971.656.662, con $199.795.000 de menos).
  - **El filtro de instrumento del tablero no filtraba nada**: `datos.filtrar()` sólo aplicaba `instrumento` si se pedía explícitamente y ninguna vista lo pedía. Las 279 opciones del selector eran decorativas.
  - **Tres totales distintos para la misma selección** (47.244 / 47.262 / 47.309): el panorama sumaba los `nunique` de cada macrozona (doble conteo de proyectos multirregión) y el ranking agrupaba por (clave, nombre), con 41 claves multi-nombre. Ahora el total se mide directo sobre la selección (`datos.medida_global`) y el ranking agrupa por clave; si el reparto no cuadra con el total, se dice en pantalla.
  - **El monto real de 2026 se mostraba como 0** en vez de «sin dato» (el `sum()` de un grupo todo-nulo devuelve 0): ahora la suma usa `min_count=1` y el nulo viaja como nulo.
  - **El aviso de multirregionalidad desaparecía justo con el filtro territorial activo**, que es cuando importa: la ficha ahora compara con un contexto sin filtro territorial y dice «ejecuta en 17 regiones y estás viendo 1».
- **Documentación alineada a lo medido**: `docs/modelo.md` decía que el año base era 2025 cuando es **2010** (los «reales» del tablero son pesos de 2010); `requirements.txt` no traía streamlit ni pyarrow; README citaba 157 tests y atribuía CC0 a los 8 repos (son 7); `docs/modulos.md` era 100% plantilla y ahora es la referencia real por módulo; `scripts/run.{bat,sh}` tenían un TODO.
- **Aptitud para publicar**: los 7 scripts de evidencia llevaban la ruta personal del scratch (`C:/Users/sebas/AppData/...`) — ahora leen de `data/crudo/` (o `$ANID_CRUDO`) y escriben junto al script.
- **El validador pasó de 43 a 45 cifras de control** (todas OK), con la fórmula de deflactión verificada contra el CSV de deflactores como fuente independiente y una nota honesta en el docstring: parte de los chequeos son invariantes internos del pipeline, no re-derivaciones del crudo.
- **La verificación del render creció de 22 a 28 comprobaciones** (cada defecto del tablero quedó con la suya: totales por vista contra `outputs/`, instrumento que filtra, 2026 sin «0 pesos reales», aviso multirregión con filtro activo) y la suite quedó en **165 tests**.

### v0.4.0 (2026-10-09) — Fase 3 cerrada: app Streamlit
- **Tablero** en `src/tablero/`: `app.py` (filtros en cascada por macrozona → región → subdirección → institución → instrumento, rango de años y casilla del año en curso), `datos.py` (carga del modelo, filtros, ficha de institución) y `vistas/` con las cinco vistas: territorial, ranking institucional, serie temporal, ficha de institución y red de colaboración + embudo de postulaciones.
- `estilo.py` (tokens, formato chileno, tarjetas con unidad visible, avisos) + `.streamlit/config.toml` + `DESIGN.md`; ninguna vista define colores ni formatos.
- **Verificación del render sin navegador**: `scripts/verificar-render.py` ejecuta la app con `streamlit.testing.v1.AppTest` (el navegador bloquea `localhost`) → `docs/evidencia/render-tablero.md` con **22/22** y `tests/test_tablero.py` (5 tests). **162 tests en verde.**
- Dos fallos propios corregidos por esa verificación: el aviso de 2026 nunca aparecía (el rango de años ya lo excluía) y la casilla de 2026 no extendía la selección.

### v0.3.0 (2026-10-09) — Fase 2 cerrada: modelo curado
- **Hecho + dimensiones + agregados** en `src/modelo/`: `proyectos` (49.014 filas × 24 columnas), `colaboracion`, `postulaciones`, `becas`, `dim_institucion` (6.094) y cuatro agregados (`agg_region`, `agg_institucion`, `agg_programa`, `tasa_region`) → `outputs/` (gitignored, se regenera).
- **Deflactores**: `config/deflactores.csv` con IPC anual de Chile del **Banco Mundial `FP.CPI.TOTL`** (base 2010, 1980→2025, citable y reproducible). Se descartó `mindicador.cl` (serie de UF incompleta).
- `scripts/{deflactores,construir-modelo,validar-modelo}.py`; el validador escribe `docs/evidencia/validacion-modelo.md` con **43 cifras de control, todas OK**.
- `docs/modelo.md`: esquema declarado, unidades de conteo, invariantes y lo que el modelo **no** responde.
- **157 tests en verde** (12 nuevos del agregador y del contrato de medidas).
- Hallazgo de entorno (Bug D15): después de un `groupby`, las etiquetas pueden quedar inaccesibles de forma intermitente; el modelo agrega con `src/modelo/agregar.py` (arrays + orden por posición) y no vuelve a buscar por nombre.

### v0.2.0 (2026-10-09) — Fases 0 y 1 cerradas
- **Fase 0:** `scripts/refrescar-corte.sh` (clona/actualiza los 8 repos) + `scripts/manifiesto.py` (filas reales, tamaño, sha256 y fecha de cada archivo → `data/crudo/_manifiesto.md`); `tests/test_fuentes.py` con los 9 conteos medidos; test de humo del scaffold reemplazado.
- **Fase 1:** `src/homologacion/` con las 8 reglas (región, macrozona, moneda, subdirección, tipo de beneficiario y sexo, institución, roles, unidad de conteo) + `fuentes.py`. **145 tests en verde.**
- `scripts/cuadre_homologacion.py` → `docs/evidencia/cuadre-homologacion.md` e `docs/evidencia/instituciones-colisiones.md`.
- Tres cifras del primer perfilado corregidas (§Cambios abajo) y `docs/homologacion.md` reescrito con los resultados medidos.
- Plan de trabajo v1.1 con las 4 decisiones del usuario cerradas.

### v0.1.0 (2026-10-09) — Creación del proyecto
- Scaffold inicial (`nuevo-proyecto.sh --python`) + contenido de dominio real.
- Revisión completa de los 8 repositorios de la cuenta: 6 clonados y perfilados campo por campo, 2 revisados por API.
- Datos crudos copiados a `data/crudo/` (los originales vivían en un directorio temporal, que se poda a las 72 h).
- Evidencia reproducible en `docs/evidencia/`: 6 scripts de perfilado + sus salidas + los 4 diccionarios de campos extraídos de los PDF oficiales.
- `docs/datos.md` (perfilado medido) y `docs/homologacion.md` (especificación de la Fase 1).

## Decisiones

| Fecha | Decisión | Consecuencia |
|-------|----------|--------------|
| 2026-10-09 | Carpeta `anid-portal` (kebab-case) y nombre legible **ANID-Portal** en documentación y vault | Cumple la validación del scaffold; el nombre visible del proyecto no cambia |
| 2026-10-09 | Los datos crudos **no se versionan**: viven en `data/crudo/` (gitignored) y se re-descargan con script | Repo liviano; la reproducción depende del script de refresco, ya escrito en la Fase 0 |
| 2026-10-09 | La tabla de homologación es **código versionado**, no una planilla aparte | Se testea y se re-aplica en cada corte; es el único activo que no se reconstruye solo |
| 2026-10-09 | Se procesa la base completa (1982→2026), no solo 2016+ | La región tiene 97-100% de cobertura por década, así que la serie larga es válida post-homologación; sin información/extranjero quedan como categorías visibles |
| 2026-10-09 | **Destino: app Streamlit** (no HTML estático ni Power BI) | La Fase 3 es código Python; la verificación del render se hace contra el servidor local |
| 2026-10-09 | **Alcance completo**: territorial + red de colaboración + embudo de postulaciones + ficha de institución | ≈20 h de trabajo; incluye los abstracts FONDECYT |
| 2026-10-09 | **Montos**: nominales en la ficha de institución y reales (UF/IPC) en la serie temporal | Requiere tabla de deflactores anuales con fuente citada (Tarea 2.6) |
| 2026-10-09 | Las **1.591 filas con fallo 2026** quedan filtrables pero **apagadas por defecto**, con aviso en el pie | No contaminan los totales por defecto ni desaparecen del tablero |
| 2026-10-09 | **Deflactores del Banco Mundial** (`FP.CPI.TOTL`, IPC anual de Chile, base 2010) en vez de `mindicador.cl` | Serie completa 1980→2025, citable y reproducible con una URL; la UF por año llegaba incompleta |
| 2026-10-09 | El modelo **nunca busca por etiqueta después de un `groupby`** (regla R9) | El entorno rompe esa búsqueda de forma intermitente y en silencio; toda agregación pasa por `src/modelo/agregar.py` |

## Configuración activa

| Elemento | Valor |
|----------|-------|
| Cronjobs | — (sin automatización todavía) |
| Puertos | — (el que use Streamlit al levantar, por defecto 8501) |
| Datos crudos | `anid-portal\data\crudo\` (137 MB, gitignored, con `_manifiesto.md`) |
| Modelo | `anid-portal\outputs\` (gitignored, se regenera con `scripts/construir-modelo.py`) |
| Tablero | `py -3.11 -m streamlit run src/tablero/app.py` → `http://localhost:8501` (usar `--server.port` si está ocupado) |
| Deflactores | `anid-portal\config\deflactores.csv` (versionado, con fuente y fecha) |
| Intérprete | `py -3.11` (el `python` del PATH es un venv ajeno al proyecto, sin pandas ni openpyxl) |
| Vault destino | `Proyectos\ANID-Portal.md` + fila en `Proyectos\_Index.md` |
| Tests | `py -3.11 -m pytest tests/` → 165 passed (12 s) incluye los del tablero vía `AppTest` |
| Validación | `py -3.11 scripts/validar-modelo.py` → 45/45 cifras de control · `py -3.11 scripts/verificar-render.py` → 28/28 |

## Bugs conocidos

No son bugs del proyecto sino del dato, y **deben sobrevivir al pipeline** como reglas de negocio (ver `AGENTS.md` §2):

| # | Hallazgo | Estado | Nota |
|---|----------|--------|------|
| D1 | Región con 4 convenciones de escritura, dependientes de la era | Regla R2 ✅ | Sin homologar: RM 26.334 vs 27.212 (3,2%). Resuelto: 0 sin clasificar en las 4 bases |
| D2 | Monto en miles de pesos con 4 rótulos (`M$` incluido) + 38 filas en EUROS + 2.425 sin monto | Regla R3 ✅ | Sumar sin filtrar moneda da un total inválido. **Corregido**: 2.423 → 2.425 y RM 2020-2025 $1.152.602 → **$1.160.514 millones** (el primer filtro excluía las 94 filas `M$`) |
| D3 | 443 filas con `CODIGO_PROYECTO` repetido (136 códigos, todos con contenido distinto) | Regla R1 ✅ | Contar códigos ≠ contar filas: 49.014 / 48.707 / 48.835 |
| D4 | El histórico no trae RUT de institución; el cruce con Colaboración es por nombre (94%) | Regla R4 ✅ | Colisiones reales: 373 RUT con más de un nombre y 21 nombres con más de un RUT (**no** 411/117: se cuentan sobre RUT válidos) |
| D5 | 1.591 filas con año de fallo 2026 en una base declarada "al 31-dic-2025" | Regla R7 ✅ | Decidido: filtrables y apagadas por defecto, con aviso |
| D6 | 17,7% de las filas de Colaboración sin región (4.198 "no registra" + 1.770 "no aplica") | Por decidir | No rellenar: mostrar como categoría |
| D7 | Los CSV traen saltos de línea dentro de campos citados | Resuelto en convenciones ✅ | Parsear con pandas, nunca por líneas |
| D8 | La macrozona **no** es la agrupación que uno supondría | Regla R2b ✅ | Coquimbo → `CENTRO`, O'Higgins → `CENTRO SUR`, RM es macrozona propia. Derivada de la región: 0 excepciones en histórico y postulaciones; 1 en becas (fila con RM y macrozona `CENTRO` en el archivo de ANID) |
| D9 | `"REGION DE ÑUBLE"` no contiene la cadena `"NUBLE"` | Regla R2 ✅ | Todo filtro sobre texto crudo debe ser insensible a la tilde o usar la columna homologada |
| D10 | Los valores de `ROLINSTITUCION` no son vocabulario controlado (65 rótulos) | Regla R6 ✅ | 9 canónicos, 0 sin clasificar en 33.731 filas. `RESPONSABLE/PUBLICA` y `/PRIVADA` son el mismo rol |
| D11 | 2 filas del histórico tienen el literal `NO SOLICITA A CONICYT` en el monto | Regla R3 ✅ | `monto_valido = False`; no se imputa |
| D12 | `Abstract_Iniciación_2016_2025.csv` no es UTF-8 (es latin-1) | Resuelto en convenciones ✅ | Leer con respaldo `(utf-8-sig, utf-8, latin-1)`; los otros dos abstracts sí son UTF-8, no se puede generalizar |
| D13 | Existe una **décima base**: la consulta pública de la Política de Acceso Abierto (732 respuestas × 62 columnas) | Fuera de alcance ✅ | No es dato de proyectos; no entra al modelo. Declarada en `docs/datos.md` §10 por si se quiere medir opinión |
| D14 | Los CSV y sus XLSX espejo duplican el conteo si se suman | Resuelto en el manifiesto ✅ | El manifiesto cuenta sólo los CSV (306.390 filas) y compara ambos formatos para detectar desincronización |
| D15 | Con pandas 2.3.3 + numpy 2.4.6 (Python 3.11, Windows) las etiquetas de un `groupby(...).reset_index()` pueden quedar inaccesibles **de forma intermitente**: `"c" in df.columns` da `True` y `df["c"]`/`sort_values(["c"])` dan `KeyError` | Regla R9 ✅ | Reprodecido con pandas puro y datos sintéticos, sin código del proyecto; va y viene entre procesos → los resultados pueden cambiar en silencio. Mitigado: toda agregación pasa por `src/modelo/agregar.py` (arrays + orden por posición) |
| D16 | 102.735 de las 139.517 filas de postulaciones no están adjudicadas y **ninguna trae institución** | Decidido ✅ | La tasa de adjudicación es por región, sólo sobre proyectos (68.133 → 18.233, +26,76%); no se publica tasa por institución |
| D17 | Una celda del corte viene en notación científica (`2E+05`, código 1261710, FONDECYT Regular 2026), igual en el CSV y en el XLSX espejo | Corregido ✅ | Se interpreta tal cual ($200.000.000) y se marca en `monto_cientifico`. Sin eso el monto se publicaba mil veces menor: la suma del país estaba $199.795.000 bajo la real |
| D18 | `docs/modelo.md` declaraba «el año base es 2025» cuando el archivo de deflactores usa **2010** | Corregido ✅ | Los montos reales son pesos de 2010 y la suma real de 2025 no coincide con su nominal (factor 0,539). El pipeline era consistente; el error era de documentación y desorientaba cada cifra real |
| D19 | El selector «Instrumento» del tablero no filtraba nada (no-op silencioso) | Corregido ✅ | `datos.filtrar()` no incluía `instrumento` entre las columnas por defecto. Cubierto por una verificación de render que compara el total antes y después |
| D20 | Tres totales distintos para la misma selección (47.244 / 47.262 / 47.309) y el ranking contaba 1.680 claves donde hay 1.638 | Corregido ✅ | El panorama sumaba los `nunique` de cada macrozona y el ranking agrupaba por (clave, nombre). Ahora el total se mide directo (`medida_global`) y el reparto por grupo se declara aparte si no cuadra |
| D21 | El monto real de 2026 se mostraba como **0** en la serie | Corregido ✅ | El `sum()` de un grupo con todos los valores nulos devuelve 0; la agregación ahora usa `min_count=1` y el nulo llega al tablero como «—» |

## Próximos pasos

- [x] **`AGENTS.md` escrito** (2026-10-09) — 8 secciones con dominio real.
- [x] **Fase 0** — refresco del corte + manifiesto con sha256 + 9 tests de fuentes.
- [x] **Fase 1** — `src/homologacion/` con las 8 reglas, 145 tests, cuadre en `docs/evidencia/`.
- [x] **Fase 2** — modelo curado: `docs/modelo.md`, hecho de proyectos, red de colaboración, embudo de postulaciones, becas, deflactores IPC y validador con 43 cifras de control (todas OK).
- [x] **Fase 3** — app Streamlit: 5 vistas, filtros en cascada, avisos permanentes y render verificado (**22/22** en su cierre, **28/28** tras la auditoría, con `AppTest`; el navegador del entorno bloquea `localhost`).
- [x] **Fase 4 (auditoría)** — tres auditores independientes contra el modelo, el tablero y la documentación; **sus cinco defectos reales están corregidos** y cada uno quedó con test o chequeo (ver v0.5.0).
- [ ] **Pendiente de decisión tuya:** publicar el tablero (y dónde), licencia del **código** (los datos son CC0), cambiar el correo del autor en la configuración de git antes de un push, si entran los abstracts FONDECYT (sin licencia) y cómo resolver las 373/21 colisiones institucionales.
- [ ] **Bloqueado por aprobación:** 5 correcciones en `AGENTS.md` (tabla de metadatos, reglas R3 y R4, glosario y el diagrama) — la aprobación de escritura expiró sin respuesta. Detalle en el informe al usuario.

## Bitácora

- **2026-10-09 (noche, 3)** — **Auditoría independiente (Fase 4)** con tres auditores de contexto aislado y sin permiso de escritura: uno re-midió las cifras contra el crudo (el modelo resistió: 40+ cifras exactas y los deflactores verificados 46/46 contra la API del Banco Mundial en vivo), otro audió el tablero como producto y el tercero la documentación y la aptitud para publicar. Encontraron **cinco defectos reales** que mis propias verificaciones no veían: la celda `2E+05` mal parseada ($199.795.000 de menos en la suma del país), el filtro de instrumento que no filtraba, tres totales distintos para la misma selección, el monto real de 2026 mostrado como 0 y el aviso de multirregionalidad que se apagaba con el filtro territorial. Todos corregidos, con test o chequeo de render que los fija. Además: `docs/modelo.md` declaraba un año base equivocado (2025 en vez de 2010), `requirements.txt` no dejaba el tablero operativo, README atribuía CC0 a los 8 repos (son 7) y los scripts de evidencia llevaban la ruta personal del scratch. El validador subió a **45/45**. Quedan bloqueadas por aprobación 5 correcciones en `AGENTS.md`.
- **2026-10-09 (noche, 2)** — Cierre de la Fase 3: app Streamlit con las cinco vistas y filtros en cascada, tokens en un solo módulo y `DESIGN.md`. La verificación del render quedó en `AppTest` (22/22 + 5 tests) porque el navegador del entorno bloquea direcciones locales — y esa verificación **encontró dos fallos propios**: el aviso de 2026 del pie era inalcanzable y la casilla no extendía la selección. Ambos corregidos y cubiertos por tests. Falta el `@revisar` independiente (Fase 4) y la decisión de publicar.
- **2026-10-09 (noche)** — Cierre de la Fase 2. Se construyó el modelo curado: hecho de 49.014 filas con las tres unidades de conteo explícitas, red de colaboración, embudo de postulaciones (26,76% de tasa sobre proyectos), becas, dimensión de 6.094 instituciones y cuatro agregados. Deflactores del Banco Mundial (IPC base 2010) en lugar de `mindicador.cl`. El validador reproduce **43/43 cifras de control**, incluida la corrección del informe (2.425 filas sin monto · $1.160.514 millones RM 2020-2025 · 373/21 colisiones). Apareció y se acotó un fallo **intermitente del entorno** (pandas 2.3.3 + numpy 2.4.6) que deja etiquetas inaccesibles después de un `groupby`; el modelo entero agrega por arrays para no depender de eso (D15).
- **2026-10-09 (tarde)** — Cierre de Fases 0 y 1. Se escribió el refresco del corte y el manifiesto con sha256; se implementaron las 8 reglas de homologación con 145 tests en verde. Hallazgos nuevos: la macrozona derivada (D8, con las dos diferencias respecto de la agrupación intuitiva), la trampa de la tilde en Ñuble (D9) y los roles institucionales sin vocabulario controlado (D10). Se decidió con el usuario: **Streamlit**, alcance completo, montos nominales + reales, 2026 apagado por defecto. Tres cifras del primer perfilado quedaron corregidas (D2 y D4) — el detalle está en `docs/datos.md` §10.
- **2026-10-09** — Revisión de factibilidad de los 8 repos de ANID-GITHUB: veredicto **factible con 4 homologaciones obligatorias**. Se midieron 293.629 filas / 77 MB de CSV; cruces verificados (Colaboración ⊂ Histórico 16.426/16.426; Postulaciones→Histórico 99-100% en las 4 subdirecciones de proyectos; Capital Humano 92% contra Becas; región→macrozona cuadra exacto). Se declina la tasa de adjudicación **por institución** (no existe denominador: 85.958 filas / 85.907 códigos `NO ADJUDICADO` sin institución). Creación del proyecto con toda la evidencia.
