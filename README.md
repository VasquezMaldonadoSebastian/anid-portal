# ANID-Portal

Tablero de la cartera de **proyectos adjudicados por ANID** (ex CONICYT, 1982→2025) con filtros y agrupaciones por **región, macrozona e institución**, construido sobre los 8 repositorios públicos de la cuenta [`ANID-GITHUB`](https://github.com/ANID-GITHUB) (licencia CC0-1.0).

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

# tests (157)
py -3.11 -m pytest tests/

# reglas de homologación contra el dato real -> docs/evidencia/
py -3.11 scripts/cuadre_homologacion.py

# modelo curado: data/crudo/ -> outputs/ (~40 s) y sus 43 cifras de control
py -3.11 scripts/construir-modelo.py
py -3.11 scripts/validar-modelo.py
```

## Estructura

```text
anid-portal/
├── data/crudo/     → clones de los 8 repos (gitignored, 137 MB)
├── outputs/        → modelo curado: parquet + csv + _meta.json (gitignored, se regenera)
├── src/            → homologacion/ (Fase 1) y modelo/ (Fase 2)
├── tests/          → tests de normalización, del agregador y del contrato de medidas
├── scripts/        → setup, corte, manifiesto, modelo y validador
├── config/         → default.yaml (trackeado) + deflactores.csv (IPC, trackeado) + local.yaml (ignorado)
├── docs/           → datos.md, homologacion.md, modelo.md, modulos.md, evidencia/, plans/
└── logs/           → salida de ejecución (gitignored)
```

## Estado

| Componente | Estado |
|------------|--------|
| Revisión de fuentes (8 repos) | ✅ Cerrada — 293.629 filas medidas |
| `docs/datos.md` (perfilado) | ✅ Cerrado |
| `src/homologacion/` | ✅ Fase 1 — 8 reglas, 145 tests |
| Modelo curado | ✅ Fase 2 — 43/43 cifras de control, 157 tests |
| Tablero (Streamlit) | ⏳ Fase 3 |

## Documentación

- [`AGENTS.md`](AGENTS.md) — contexto para agentes (8 secciones): reglas de negocio R1-R9, glosario del dominio, arquitectura, roles y flujos
- [`MEMORIA.md`](MEMORIA.md) — estado vivo, decisiones, hallazgos del dato, próximos pasos
- [`docs/datos.md`](docs/datos.md) — perfilado medido de cada base y los encadenamientos verificados
- [`docs/homologacion.md`](docs/homologacion.md) — especificación de la Fase 1 (reglas y cifras de control)
- [`docs/modelo.md`](docs/modelo.md) — esquema del modelo curado: tablas, unidades de conteo, deflactores e invariantes
- [`docs/modulos.md`](docs/modulos.md) — referencia técnica por módulo
