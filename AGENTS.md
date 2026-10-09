# ANID-Portal — Tablero de proyectos adjudicados ANID

## 1. Metadatos del proyecto

| Campo | Valor |
|-------|-------|
| **Nombre** | ANID-Portal (carpeta `anid-portal`) |
| **Versión** | 0.1.0 |
| **Stack** | Python 3.11 + pandas 2.3.3 + openpyxl 3.1.5 (cruda, homologación, validación). Capa de presentación **por definir**: HTML estático con payload pre-agregado (público) o Power BI Desktop (interno). |
| **Repositorio** | `A:\Repositorio Proyectos\anid-portal` |
| **Fuente de datos** | 8 repositorios públicos de `github.com/ANID-GITHUB` (licencia CC0-1.0; FONDECYT-Abstracts sin licencia) |
| **Datos crudos** | `data/crudo/<repo>/` — clones con `--depth 1`; **no versionados** |
| **Dependencias** | ver `requirements.txt` (pandas, openpyxl) |
| **Inicio rápido** | `bash scripts/setup.sh` y luego `py -3.11 docs/evidencia/profile_h2.py` |
| **Plan de trabajo** | `docs/plans/2026-10-09-tablero-anid-portal.md` |
| **Estado** | Fase 0 cerrada (fuentes revisadas y medidas). Fases 1-3 pendientes de aprobación del plan. |

## 2. Contexto de dominio

### ¿Qué es?

Un tablero para explorar la cartera de proyectos adjudicados por ANID (ex CONICYT, 1982→2025) **con filtros y agrupaciones territoriales e institucionales**: región, macrozona Minciencia, institución, año de fallo, subdirección, programa, instrumento y disciplina, mostrando conteos y montos. No existe API: la fuente son archivos CSV/XLSX publicados en GitHub con periodicidad trimestral (proyectos) y anual (colaboración, postulaciones, becas). El insumo es de dominio público (CC0-1.0), así que el tablero —y su publicación— no tiene restricción de licencia; la restricción es **de método**: sin homologar, las cifras del tablero son falsas.

### Reglas de negocio (todas medidas sobre los archivos, no supuestas)

| # | Regla | Descripción |
|---|-------|-------------|
| R1 | **Unidad de conteo explícita** | Filas, códigos únicos y proyectos distintos dan totales distintos: el histórico tiene 49.014 filas pero 48.707 códigos, y 443 filas con código repetido (136 códigos, todos con contenido distinto). Toda tarjeta declara qué cuenta. |
| R2 | **Región se homologa antes de agrupar** | El mismo territorio aparece con 4 convenciones de escritura y la etiqueta cambia según la era: sin homologar, la RM da 26.334 filas y con homologación 27.212 (**3,2% de desvío**). 24 etiquetas → 16 regiones + 3 categorías no territoriales. |
| R3 | **Nunca sumar monto sin filtrar moneda** | El monto viene en miles de pesos con 4 rótulos distintos, hay 38 filas en EUROS y 2.423 filas sin monto (4,9%). El rótulo `M$` invita a leer millones: es miles de pesos. |
| R4 | **Institución sin clave única en el histórico** | El histórico no trae RUT: el cruce con Colaboración es por nombre (94% de coincidencia). Donde exista, el RUT manda; el nombre normalizado es respaldo. 411 RUT tienen más de un nombre y 117 nombres más de un RUT. |
| R5 | **Institución ≠ región (no es 1:1)** | 127 instituciones (de 1.637) aparecen en más de una región (U. de Concepción en 15). Hay que definir si el filtro territorial opera sobre el proyecto o sobre la institución. |
| R6 | **Tasa de adjudicación: solo por región, y separando proyectos de becas** | Postulaciones no trae nombre de institución y las 85.907 postulaciones no adjudicadas no tienen institución en ninguna base → **no hay denominador por institución**. Proyectos: 26,8% (68.133 postulaciones). Capital Humano va contra la base de Becas (92% de sus adjudicaciones viven ahí), no contra la de proyectos. |
| R7 | **El corte declarado se verifica contra el contenido** | Los README declaran cortes que el archivo no respeta: la base "al 31-dic-2025" contiene 1.591 filas con año de fallo 2026. Gana el artefacto, y se declara la fecha de descarga real. |
| R8 | **La cola larga no se filtra en silencio** | 1.542 instituciones (88% del total) tienen ≤3 proyectos y suman 4% de las filas. Un filtro "top N" las oculta: el tablero debe decir cuánto agregado queda fuera. |

### Glosario

| Término | Definición |
|---------|------------|
| **Adjudicación** | Proyecto o beca que recibió financiamiento por resolución de adjudicación (fallo). Una fila del histórico = una iniciativa adjudicada. |
| **Corte** | Fecha hasta la cual la base reporta. Histórico: trimestral (en abril entra el trimestre enero-marzo). |
| **Subdirección** | Área de ANID que ejecuta la convocatoria. Cinco reales: Capital Humano, Proyectos de Investigación, Centros e Investigación Asociativa, Investigación Aplicada, Redes Estrategia y Conocimiento. En los datos aparecen 7 rótulos (dos son variantes con coma). |
| **Programa** | Unidad de origen del instrumento (FONDECYT, FONDEF, PCI, PAI, ASTRONOMIA, FONIS, CORFO, FONDEQUIP, PIA, REGIONAL, MILENIO, FONDAP, SREC, SCIA, SIA, PFCHA…). |
| **Instrumento** | Fondo del que provienen los recursos (Regular, IDeA I+D, VIU, FONDAP…). 279 valores en el histórico. |
| **Concurso** | Convocatoria concreta, con nombre único y año (`CONCURSO NACIONAL REGULAR 1982`). |
| **AGNO_CONCURSO / AGNO_FALLO** | Año del llamado a postulaciones / año de la resolución de adjudicación. Para series temporales se usa **fallo**. |
| **Macrozona Minciencia** | Agrupación territorial de Minciencia: RM, Norte, Centro, Centro Sur, Sur, Austral (+ Extranjero, Sin información, Multirregional). Es el nivel que cierra exacto contra las regiones homologadas. |
| **Institución principal** | Persona jurídica que responde por la ejecución y puede recibir recursos directos. Es la razón social: **no hay nivel facultad/campus** en el dato. |
| **Institución 1er nivel** (Colaboración) | Cualquier institución declarada en la postulación, con su rol, RUT, país y región. 5.694 nombres / 2.477 RUT normalizados. |
| **Rol institución** | Papel declarado (principal, secundaria, asociada, patrocinante, aportante, extranjera…). 65 valores crudos → requiere colapsar a roles canónicos. |
| **M$** | Miles de pesos. `58.191` en el campo significa $58.191.000. |
| **SPL** | Sistema de Postulación en Línea. Las postulaciones que no entraron por SPL pueden aparecer solo si fueron adjudicadas → explica los huecos de cobertura por concurso. |
| **Capital Humano / PFCHA** | Subdirección y programa de becas. Sus "códigos de proyecto" en la base de postulaciones son **códigos de beca**. |

## 3. Arquitectura del sistema

```text
  github.com/ANID-GITHUB (8 repos, CC0)
        │  gh repo clone --depth 1  (trimestral / anual)
        ▼
  data/crudo/<repo>/*.csv|xlsx            [crudo, no versionado]
        │  pandas read_csv(sep=';', encoding='utf-8-sig')
        ▼
  src/homologacion                        [FASE 1]
        │  región · macrozona · moneda · subdirección · beneficiario · institución · roles
        ▼
  modelo curado (institución × región × año × instrumento)
        │  ┌──────────────┬───────────────┐
        ▼  ▼              ▼               ▼
   validador        payload JSON      export XLSX
   (cuadre vs       pre-agregado      (uso interno)
    cifras base)    para el tablero
```

### Árbol de directorios del proyecto

```text
anid-portal\
├── README.md
├── AGENTS.md                  ← este archivo (arquitectura + reglas)
├── MEMORIA.md                 ← estado vivo del proyecto
├── data\
│   └── crudo\<repo>\          ← clones de los 8 repos (gitignored, 137 MB)
├── docs\
│   ├── datos.md               ← perfilado medido de las fuentes
│   ├── homologacion.md        ← especificación de la Fase 1 (reglas H1-H8)
│   ├── modelo.md              ← esquema del modelo curado (Fase 2)
│   ├── modulos.md             ← referencia técnica por módulo
│   ├── plans\                 ← planes de trabajo aprobados
│   └── evidencia\             ← scripts y salidas del perfilado (reproducible)
├── src\
│   ├── homologacion\          ← reglas de normalización (Fase 1)
│   └── modelo\                ← ETL y export (Fase 2)
├── tests\                     ← cuadres y tests de normalización
├── scripts\                   ← setup, ejecución y refresco del corte
├── config\                    ← default.yaml (trackeado) + local.yaml (ignorado)
├── templates\
├── assets\
└── logs\                      ← gitignored
```

### Datos vs código

El **código** vive en el repo y se versiona. Los **datos crudos** son de dominio público pero pesados (137 MB con los `.git`): no se versionan, se re-descargan con `scripts/refrescar-corte.sh`, que clona o hace `git pull` de cada repo y registra fecha de descarga, filas y sha256 de cada archivo en `data/crudo/_manifiesto.md`. Los datos crudos son **reemplazables**; lo que no se reconstruye solo es la tabla de homologación, que es código y sí se versiona.

## 4. Convenciones y estándares

- **Idioma:** español en documentación y entregables; inglés en código e identificadores.
- **Lectura de los CSV:** siempre `pd.read_csv(path, sep=';', encoding='utf-8-sig', dtype=str)`. Los archivos son **delimitados por punto y coma**, con BOM y **saltos de línea dentro de campos citados** (49.041 líneas físicas para 49.014 filas): nunca parsear por líneas ni con `awk`/`cut`, y no confiar en el delimitador por defecto (el engine C de pandas aborta con `ParserError: Expected 1 fields`).
- **Todo dato se lee como texto** (`dtype=str`) y se castea explícitamente: el código de proyecto es alfanumérico y los montos traen separador de miles.
- **Montos:** se normalizan a pesos con su moneda declarada; nunca se suman monedas distintas. Los vacíos se cuentan aparte, no se rellenan.
- **Normalizadores:** cada regla de homologación es una función pura con test (caso que normaliza, caso que debe quedar igual y test de cuadre de filas). Sin test no entra.
- **Tests:** `py -3.11 -m pytest tests/ -q`. Todo validador de conteo se compara contra las cifras base de `docs/datos.md`.
- **Verificación:** ninguna cifra se publica sin haberla medido en el artefacto en ese momento. Documento desactualizado = se corrige el documento, no se repite la cifra.
- **Errores:** no silenciar. Se loguea la fila y el motivo y se reporta el conteo de filas no clasificadas — una homologación que descarta filas en silencio es un bug.
- **Privacidad:** el tablero agrega por institución y región; **no** publica nombres de responsables ni de co-investigadores.
- **Nombres de archivo:** kebab-case, sin tildes, ñ ni espacios.
- **Git:** commit local siempre; `push` **solo con OK explícito** del usuario.

## 5. Roles / personas

### Rol 1 — Líder 🧭 · trigger: `@lider <acción>`
- **Expertise:** alcance del tablero, decisión de qué se publica, priorización de fases.
- **Responsabilidades:** descompone en tareas de 2-5 min con path y salida esperada; aprueba el plan antes de implementar; decide entre uso interno y publicación.
- **Límites:** no escribe código de producción ni toca `data/`. **Excepciones:** puede escribir el plan, los stubs y la documentación.
- **Ejemplo:** `@lider descompón la Fase 1` → tabla de tareas con archivo, regla y cifra de control.

### Rol 2 — Implementador 🔧 · trigger: `@implementar <tarea>`
- **Expertise:** pandas, normalización de texto, cuadres, generación de payload.
- **Responsabilidades:** ejecuta la tarea, corre los tests y reporta la salida real (conteos antes/después de cada homologación).
- **Límites:** no cambia el alcance, no relanza el refresco del corte completo sin OK, no inventa valores para filas sin dato. **Excepciones:** puede proponer un cambio de plan si hay bloqueo, y descartar una fila solo dejándola contada como no clasificada.
- **Ejemplo:** `@implementar homologación de región` → función + test + tabla "24 etiquetas crudas → 19 destinos con su conteo".

### Rol 3 — Revisor 🔍 · trigger: `@revisar <entregable>`
- **Expertise:** método estadístico, coherencia territorial, privacidad.
- **Responsabilidades:** audita contra las cifras base de `docs/datos.md` y contra los PDF de notas oficiales de cada repo; emite informe con severidad.
- **Límites:** no modifica archivos del proyecto auditado; **solo informe al usuario**. **Excepciones:** puede escribir su informe en `docs/evidencia/`.
- **Ejemplo:** `@revisar tablero` → hallazgos numerados con la cifra esperada, la obtenida y la regla de conteo.

### Matriz de colaboración (C = frecuente, I = ocasional)

| ↓ habla con → | Líder | Implementador | Revisor |
|---------------|-------|---------------|---------|
| **Líder** | — | C | I |
| **Implementador** | I | — | C |
| **Revisor** | I | I | — |

## 6. Flujos de trabajo

### Flujo A — Refresco del corte (trimestral)
1. `bash scripts/refrescar-corte.sh` → clona o actualiza los 8 repos en `data/crudo/` y escribe `_manifiesto.md` (fecha, filas, sha256).
2. Correr el perfilador (`docs/evidencia/profile_*.py`) y comparar contra `docs/datos.md`.
3. Diferenciar lo nuevo: filas agregadas, etiquetas de región nuevas, valores nuevos de moneda.
4. Regenerar el modelo curado y el payload.
5. Publicar con la **fecha de descarga real** en el pie del tablero.

**Checklist de aprobación:** archivos descargados y hasheados · perfilado sin desvíos nuevos · toda etiqueta nueva clasificada o reportada como no clasificada · cifras base de `docs/datos.md` actualizadas · fecha de descarga visible en el tablero.

### Flujo B — Hotfix: una cifra del tablero no cuadra
1. Reproducir: aislar el filtro mínimo (región + año + institución) y volcar las filas que entran.
2. Verificar la unidad de conteo antes de culpar al dato (R1).
3. Medir el desvío y atribuirlo a su causa: etiqueta sin homologar, moneda mezclada, código repetido o fila sin dato.
4. Fix en el normalizador + test de regresión con el caso exacto.
5. Re-verificar los totales generales y dejar la cifra corregida en `MEMORIA.md`.

**Checklist de aprobación:** desvío medido antes y después · test de regresión agregado · totales generales re-verificados · si la cifra ya se había entregado, retirarla explícitamente.

### Flujo C — Optimización del tablero
1. Medir línea base: tamaño del payload, filas barridas por interacción, tiempo de carga.
2. Un cambio a la vez (pre-agregar, colapsar categorías, índice por año).
3. Volver a medir y comparar contra la línea base.

**Checklist de aprobación:** métrica antes/después con números reales · el tablero sigue mostrando los mismos totales (cuadre contra el modelo).

## 7. Referencias y recursos

- **Fuentes (8 repos de `github.com/ANID-GITHUB`):**

| Repo | Contenido | Filas | Periodicidad |
|------|-----------|-------|--------------|
| `Historico-de-Proyectos-Adjudicados` | Proyectos adjudicados 1982-2026 + Milenio | 49.014 (+136) | trimestral |
| `Colaboracion_Institucional` | Instituciones asociadas 2016-2025 + co-investigadores SPI | 33.731 (+20.620) | anual |
| `Postulaciones` | Postulaciones 2016-2025 + Milenio | 139.517 (+1.205) | anual |
| `Becas` | Becas adjudicadas 2015-2025 | 19.288 | anual |
| `Palabras_claves` | Palabras clave (corte dic-2023, discontinuada) | 29.118 | congelada |
| `FONDECYT-Abstracts` | Abstract por proyecto (Regular, Iniciación, Postdoctorado) | 3 CSV | irregular |
| `Instructivo_descarga` | Paso a paso de descarga | — | — |
| `Consulta-Publica-Politica-de-Acceso-Abierto` | Respuestas de consulta pública | — | — |

- **Diccionarios de campos:** los PDF de notas de cada repo (`BDH_HISTORICA_Notas.pdf`, `BASES DE COLABORACION.pdf`, `Postulaciones_ANID.pdf`, `BDH_BECAS_NOTAS.pdf`) son la fuente autoritativa. Texto extraído en `docs/evidencia/dict_*.txt`.
- **Comandos frecuentes (probados):**
  ```bash
  py -3.11 -c "import pandas as pd; h=pd.read_csv('data/crudo/Historico-de-Proyectos-Adjudicados/BDH_HISTORICA.csv',sep=';',encoding='utf-8-sig',dtype=str); print(h.shape)"
  py -3.11 docs/evidencia/profile_h2.py     # perfil del histórico + regiones + instituciones
  py -3.11 docs/evidencia/profile_resto.py  # perfil de las demás bases + cruces
  py -3.11 -m pytest tests/ -q
  ```
- **Troubleshooting:**

| Problema | Causa | Fix |
|----------|-------|-----|
| `ParserError: Expected 1 fields in line N, saw 2` | el CSV es `;`-delimitado y el engine C usa coma | `sep=';'` (+ `encoding='utf-8-sig'`) |
| La primera columna se llama `\ufeffN` | BOM UTF-8 | `encoding='utf-8-sig'` |
| Una región aparece dos veces en el mismo año | la etiqueta cambió de convención según la era (R2) | homologar; RM = 26.334 (cruda) vs 27.212 (correcta) |
| El total de montos es absurdo | se sumaron miles de pesos con euros, o `M$` se leyó como millones | filtrar por moneda y normalizar (R3) |
| El conteo de proyectos no cuadra con la suma de filas | 443 filas con código repetido (R1) | declarar la unidad de conteo |
| El perfilado corre con el Python equivocado | `python` del PATH es un venv ajeno al proyecto (sin pandas) | usar `py -3.11` |

## 8. Evolución y mantenimiento

- **Changelog:** ver `MEMORIA.md`.
- **Responsable de este archivo:** el agente que cierre cada fase; el usuario aprueba.
- **Cadencia de revisión:** al cerrar cada fase y en cada refresco de corte (trimestral). El diccionario de datos se re-lee cuando ANID publique un PDF de notas actualizado.
- **Regla:** el detalle de implementación va en `docs/modulos.md`, el perfilado medido en `docs/datos.md` y las reglas de homologación en `docs/homologacion.md`. Este archivo se mantiene en arquitectura + reglas.
