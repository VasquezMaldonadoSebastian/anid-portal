# Referencia técnica por módulo

> Detalle de implementación. `AGENTS.md` mantiene arquitectura y reglas; `docs/datos.md`,
> `docs/homologacion.md` y `docs/modelo.md` mantienen el porqué de los datos y del modelo. Este archivo
> mantiene el "dónde está cada cosa".

## `src/homologacion/` — reglas de homologación (Fase 1)

Funciones puras, sin estado, cada una con su cifra de control en `docs/homologacion.md` y sus tests en
`tests/`.

| Módulo | Propósito | Funciones clave |
|---|---|---|
| `fuentes.py` | catálogo de las 9 bases procesables: ruta del crudo, licencia, periodicidad y unidad de conteo | `FUENTES`, `cargar(nombre)` |
| `region.py` | 24 rótulos crudos → 16 regiones + 3 categorías (`SIN INFORMACION`, `EXTRANJERO`, `NO APLICA`) | `homologar_region()` |
| `macrozona.py` | macrozona **derivada** de la región (no copiada): Coquimbo→CENTRO, O'Higgins→CENTRO SUR, RM propia | `macrozona_de_region()` |
| `moneda.py` | rótulos de moneda y montos: miles de pesos → pesos, euros aparte, notación científica de Excel | `rotulo_moneda()`, `a_pesos()`, `a_euros()`, `es_notacion_cientifica()`, `normalizar_montos()` |
| `subdireccion.py` | subdirecciones de ANID a los valores canónicos del informe | `homologar_subdireccion()` |
| `categorias.py` | sexo y tipo de beneficiario | `homologar_sexo()`, `homologar_tipo_beneficiario()` |
| `institucion.py` | nombre normalizado y RUT: 1.749 nombres → 1.733 normalizados → 1.707 claves | `normalizar_nombre()`, `normalizar_rut()`, `resolver_clave()` |
| `roles.py` | 65 rótulos de rol en Colaboración → 9 roles canónicos | `homologar_rol()` |
| `metricas.py` | unidades de conteo (`filas`, `codigos`, `proyectos`) y su definición | `MEDIDAS`, `UNIDADES`, `definicion()` |

Regla que atraviesa la capa: **ninguna métrica viaja sin su unidad de conteo** y ningún monto sin su
moneda.

## `src/modelo/` — modelo curado (Fase 2)

| Módulo | Propósito | Funciones clave |
|---|---|---|
| `deflactores.py` | IPC anual de Chile (Banco Mundial `FP.CPI.TOTL`, **base 2010**) y la deflactión | `cargar_deflactores()`, `Deflactores.aplicar()`, `Deflactores.factor()` |
| `proyectos.py` | el hecho: una fila por registro del histórico, 24 columnas homologadas y deflactadas | `construir_proyectos()` |
| `instituciones.py` | clave de institución (RUT si se deduce, nombre normalizado si no) y dimensión | `resolver_clave()`, `construir_dim_institucion()` |
| `colaboracion.py` | red institucional: 33.731 filas, 16.426 proyectos, roles y RUT | `construir_colaboracion()` |
| `postulaciones.py` | embudo: 139.517 filas, adjudicado/no adjudicado y tasa por región | `construir_postulaciones()`, `tasa_global()`, `tasa_por_region()` |
| `becas.py` | becas 2015-2025 (19.288 filas), sin nombres: la fuente trae personas y el modelo no las versiona | `construir_becas()` |
| `agregar.py` | **agregación por arrays** (`np.lexsort` + `iloc`), nunca búsqueda por etiqueta tras un `groupby` | `agrupar()`, `ordenar_por()` |
| `exportar.py` | escribe las 9 tablas en parquet + csv y el `_meta.json` con las medidas del hecho | `construir_todo()`, `_agregar()`, `MEDIDAS` |

`agregar.py` existe por una trampa medida en este entorno (pandas 2.3.3 + numpy 2.4.6): ver la regla
R9 de `AGENTS.md` y `docs/modelo.md`.

## `src/tablero/` — tablero Streamlit (Fase 3)

| Módulo | Propósito |
|---|---|
| `app.py` | filtros en cascada del panel, las 5 pestañas y los avisos permanentes del pie |
| `datos.py` | carga `outputs/` (nunca los CSV crudos), filtra, mide la selección y arma la ficha |
| `estilo.py` | tokens únicos de color, tipografía, unidades y componentes (tarjeta, aviso) |
| `vistas/territorial.py` | panorama por macrozona y región, con la unidad de conteo elegible |
| `vistas/institucional.py` | ranking con la cola larga declarada y concentración del top visible |
| `vistas/serie.py` | serie anual con interruptor nominal / real |
| `vistas/ficha.py` | una institución: montos nominales, años, instrumentos y regiones |
| `vistas/red.py` | red de colaboración y embudo de postulaciones con la tasa por región |

## `scripts/` — puerta de entrada

| Script | Qué hace |
|---|---|
| `refrescar-corte.sh` | trae o actualiza el corte a `data/crudo/` y regenera el manifiesto |
| `manifiesto.py` | cuenta filas de cada base (13 CSV) y deja `docs/evidencia/manifiesto-corte.md` |
| `cuadre_homologacion.py` | mide las reglas de homologación contra el dato real |
| `deflactores.py` | baja el IPC del Banco Mundial a `config/deflactores.csv` |
| `construir-modelo.py` | `data/crudo/` → `outputs/` |
| `validar-modelo.py` | 45 cifras de control → `docs/evidencia/validacion-modelo.md` |
| `verificar-render.py` | ejecuta la app con `AppTest` y verifica el render → `docs/evidencia/render-tablero.md` |

## `tests/`

`pytest tests/` corre la suite completa (162 tests). Cubre homologación (7 archivos), el modelo y su
agregación por arrays, las fuentes y un smoke test del tablero. Los tests son la red de seguridad de las
reglas: si una regla cambia, cambia su test.
