# ANID-Portal

Tablero de la cartera de **proyectos adjudicados por ANID** (ex CONICYT, 1982→2026) con filtros y agrupaciones por **región, macrozona e institución**, construido sobre los 8 repositorios públicos de la cuenta [`ANID-GITHUB`](https://github.com/ANID-GITHUB): 7 de ellos con licencia CC0-1.0 y FONDECYT-Abstracts sin licencia declarada (sus abstracts no entran al tablero).

## ¿Qué incluye?

- **Capa cruda** — los 8 repos descargados en `data/crudo/` (293.629 filas / 77 MB de CSV), sin versionar.
- **Homologación** — reglas de normalización de región, moneda, subdirección, tipo de beneficiario y roles institucionales, con tests (Fase 1 ✅).
- **Modelo curado** — `proyectos` (49.014 filas), `colaboracion`, `postulaciones`, `becas`, `dim_institucion` y 4 agregados, con unidad de conteo declarada por métrica y **43 cifras de control** en verde (Fase 2 ✅).
- **Tablero** — app Streamlit con vistas territorial, ranking, serie temporal, red de colaboración, embudo y ficha de institución (Fase 3).

## Requisitos

- Python 3.11 (usar `py -3.11`; el `python` del PATH es un venv ajeno al proyecto y no trae pandas)
- pandas 2.3.3, openpyxl 3.1.5, streamlit 1.58, pyarrow
- `gh` CLI autenticado (solo para refrescar el corte)

## Instalación rápida

```bash
cd "C:/Repositorio Proyectos/anid-portal"
bash scripts/setup.sh

# traer o actualizar el corte + manifiesto con sha256 y fecha
bash scripts/refrescar-corte.sh

# tests (165)
py -3.11 -m pytest tests/

# reglas de homologación contra el dato real -> docs/evidencia/
py -3.11 scripts/cuadre_homologacion.py

# modelo curado: data/crudo/ -> outputs/ (~40 s) y sus 43 cifras de control
py -3.11 scripts/construir-modelo.py
py -3.11 scripts/validar-modelo.py

# tablero (Streamlit)
py -3.11 -m streamlit run src/tablero/app.py

# verificación del render (ejecuta la app con AppTest y deja la evidencia)
py -3.11 scripts/verificar-render.py
```

## Despliegue (Streamlit Community Cloud)

- Repositorio `VasquezMaldonadoSebastian/anid-portal`, rama `master`, **main file** `src/tablero/app.py`.
- `outputs/*.parquet` + `outputs/_meta.json` (**4,1 MB**) se versionan a propósito: son lo único que consume el tablero (`src/tablero/datos.py`) y así la nube no tiene que regenerar el modelo (los CSV de `outputs/` y `data/crudo/` siguen fuera de git, la app no los lee).
- Al reemplazar el corte: correr `py -3.11 scripts/construir-modelo.py` y commitear los parquet nuevos.

## Estructura

```text
anid-portal/
├── data/crudo/     → clones de los 8 repos (gitignored, 137 MB)
├── outputs/        → modelo curado: parquet + csv + _meta.json (gitignored, se regenera)
├── src/            → homologacion/ (Fase 1), modelo/ (Fase 2) y tablero/ (Fase 3)
├── tests/          → tests de normalización, del agregador, del contrato de medidas y del tablero
├── scripts/        → setup, corte, manifiesto, modelo, validador y verificación del render
├── config/         → default.yaml (trackeado) + deflactores.csv (IPC, trackeado) + local.yaml (ignorado)
├── docs/           → datos.md, homologacion.md, modelo.md, modulos.md, evidencia/, plans/
├── .streamlit/     → tema del tablero (config.toml)
├── DESIGN.md       → tokens y reglas de presentación del tablero
└── logs/           → salida de ejecución (gitignored)
```

## Estado

| Componente | Estado |
|------------|--------|
| Revisión de fuentes (8 repos) | ✅ Cerrada — 293.629 filas medidas |
| `docs/datos.md` (perfilado) | ✅ Cerrado |
| `src/homologacion/` | ✅ Fase 1 — 8 reglas, 145 tests |
| Modelo curado | ✅ Fase 2 — 43/43 cifras de control |
| Tablero (Streamlit) | ✅ Fase 3 — 22/22 del render · 162 tests |
| `@revisar` independiente | ⏳ Fase 4 |

## Documentación

- [`AGENTS.md`](AGENTS.md) — contexto para agentes (8 secciones): reglas de negocio R1-R9, glosario del dominio, arquitectura, roles y flujos
- [`MEMORIA.md`](MEMORIA.md) — estado vivo, decisiones, hallazgos del dato, próximos pasos
- [`docs/datos.md`](docs/datos.md) — perfilado medido de cada base y los encadenamientos verificados
- [`docs/homologacion.md`](docs/homologacion.md) — especificación de la Fase 1 (reglas y cifras de control)
- [`docs/modelo.md`](docs/modelo.md) — esquema del modelo curado: tablas, unidades de conteo, deflactores e invariantes
- [`DESIGN.md`](DESIGN.md) — tokens y reglas de presentación del tablero
- [`docs/modulos.md`](docs/modulos.md) — referencia técnica por módulo
