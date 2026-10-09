# ANID-Portal

Tablero de la cartera de **proyectos adjudicados por ANID** (ex CONICYT, 1982→2025) con filtros y agrupaciones por **región, macrozona e institución**, construido sobre los 8 repositorios públicos de la cuenta [`ANID-GITHUB`](https://github.com/ANID-GITHUB) (licencia CC0-1.0).

## ¿Qué incluye?

- **Capa cruda** — los 8 repos descargados en `data/crudo/` (293.629 filas / 77 MB de CSV), sin versionar.
- **Homologación** — reglas de normalización de región, moneda, subdirección, tipo de beneficiario y roles institucionales, con tests (Fase 1).
- **Modelo curado** — institución × región × año × instrumento, con unidad de conteo declarada por métrica y cuadre automático contra las cifras base.
- **Tablero** — payload pre-agregado + vista con filtros territoriales e institucionales.

## Requisitos

- Python 3.11 (usar `py -3.11`; el `python` del PATH es un venv ajeno al proyecto y no trae pandas)
- pandas 2.3.3, openpyxl 3.1.5
- `gh` CLI autenticado (solo para refrescar el corte)

## Instalación rápida

```bash
cd "A:/Repositorio Proyectos/anid-portal"
bash scripts/setup.sh
py -3.11 docs/evidencia/profile_h2.py     # perfil del histórico (datos ya descargados)
```

## Estructura

```text
anid-portal/
├── data/crudo/     → clones de los 8 repos (gitignored, 137 MB)
├── src/            → homologación y modelo (Fase 1)
├── tests/          → tests de normalización y cuadre
├── scripts/        → setup, ejecución y refresco del corte
├── config/         → default.yaml (trackeado) + local.yaml (ignorado)
├── docs/           → datos.md, homologacion.md, modulos.md, evidencia/
└── logs/           → salida de ejecución (gitignored)
```

## Estado

| Componente | Estado |
|------------|--------|
| Revisión de fuentes (8 repos) | ✅ Cerrada — 293.629 filas medidas |
| `docs/datos.md` (perfilado) | ✅ Cerrado |
| `src/homologacion/` | ⏳ Fase 1 — pendiente de aprobación |
| Modelo curado | ⏳ Fase 2 |
| Tablero | ⏳ Fase 3 — destino por definir (interno vs web) |

## Documentación

- [`AGENTS.md`](AGENTS.md) — contexto para agentes (8 secciones): reglas de negocio R1-R8, glosario del dominio, arquitectura, roles y flujos
- [`MEMORIA.md`](MEMORIA.md) — estado vivo, decisiones, hallazgos del dato, próximos pasos
- [`docs/datos.md`](docs/datos.md) — perfilado medido de cada base y los encadenamientos verificados
- [`docs/homologacion.md`](docs/homologacion.md) — especificación de la Fase 1 (reglas y cifras de control)
- [`docs/modulos.md`](docs/modulos.md) — referencia técnica por módulo
