# MEMORIA del Proyecto — ANID-Portal

**Estado:** Fase 0 cerrada · Fase 1 (homologación) pendiente de aprobación
**Stack:** Python 3.11 · pandas 2.3.3 · openpyxl 3.1.5 (presentación por definir)
**Path:** `A:\Repositorio Proyectos\anid-portal`
**Actualizado:** 2026-10-09

## Descripción

Tablero para explorar la cartera de proyectos adjudicados por ANID (1982→2025) con filtros y agrupaciones por región, macrozona e institución, sobre los 8 repositorios públicos de la cuenta `ANID-GITHUB` (CC0-1.0). Origen: revisión de factibilidad pedida por el usuario sobre el conjunto completo de repositorios (09-oct-2026).

## Arquitectura

```text
github.com/ANID-GITHUB ──clone──> data/crudo/ ──pandas──> src/homologacion ──> modelo curado ──> payload / XLSX
   (8 repos, CC0)                   (137 MB)                (Fase 1)              (región×institución×año)
```

## Cambios

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
| 2026-10-09 | Los datos crudos **no se versionan**: viven en `data/crudo/` (gitignored) y se re-descargan con script | Repo liviano; la reproducción depende del script de refresco, que queda como requisito de la Fase 1 |
| 2026-10-09 | La tabla de homologación es **código versionado**, no una planilla aparte | Se testea y se re-aplica en cada corte; es el único activo que no se reconstruye solo |
| 2026-10-09 | Se procesa la base completa (1982→2026), no solo 2016+ | La región tiene 97-100% de cobertura por década, así que la serie larga es válida post-homologación; se descartan/extranjero quedan como categorías visibles |
| 2026-10-09 | Presentación: **por definir** (HTML pre-agregado vs Power BI) | No bloquea la Fase 1; el payload se diseña una vez que se elija el destino |

## Configuración activa

| Elemento | Valor |
|----------|-------|
| Cronjobs | — (sin automatización todavía) |
| Puertos | — |
| Datos crudos | `anid-portal\data\crudo\` (137 MB, gitignored) |
| Intérprete | `py -3.11` (el `python` del PATH es un venv ajeno al proyecto, sin pandas ni openpyxl) |
| Vault destino | `Proyectos\ANID-Portal.md` + fila en `Proyectos\_Index.md` |

## Bugs conocidos

No son bugs del proyecto sino del dato, y **deben sobrevivir al pipeline** como reglas de negocio (ver `AGENTS.md` §2):

| # | Hallazgo | Estado | Nota |
|---|----------|--------|------|
| D1 | Región con 4 convenciones de escritura, dependientes de la era | Regla R2 | Sin homologar: RM 26.334 vs 27.212 (3,2% de desvío) |
| D2 | Monto en miles de pesos con 4 rótulos + 38 filas en EUROS + 2.423 sin monto | Regla R3 | Sumar sin filtrar moneda da un total inválido |
| D3 | 443 filas con `CODIGO_PROYECTO` repetido (136 códigos) | Regla R1 | Contar códigos ≠ contar filas |
| D4 | El histórico no trae RUT de institución; el cruce con Colaboración es por nombre (94%) | Regla R4 | El RUT de Colaboración es la mejor clave disponible |
| D5 | 1.591 filas con año de fallo 2026 en una base declarada "al 31-dic-2025" | Regla R7 | Decidir si 2026 entra al tablero |
| D6 | 17,7% de las filas de Colaboración sin región (4.198 "no registra" + 1.770 "no aplica") | Por decidir | No rellenar: mostrar como categoría |
| D7 | Los CSV traen saltos de línea dentro de campos citados | Resuelto en convenciones | Parsear con pandas, nunca por líneas |

## Próximos pasos

- [ ] **Autorizar y escribir `AGENTS.md`** — el contenido completo (8 secciones con dominio real: reglas R1-R8, glosario, arquitectura, roles, flujos, troubleshooting) está redactado pero su escritura fue bloqueada por ser archivo de instrucciones para agentes: requiere aprobación explícita del usuario. Hasta entonces `AGENTS.md` conserva los placeholders del scaffold.
- [ ] **Fase 1** — `src/homologacion/`: región (24→19), moneda, subdirección (7→5), tipo de beneficiario (6→3), roles institucionales (65→canónicos). Cada regla con test.
- [ ] **Fase 2** — modelo curado: institución × región × año × instrumento, con unidad de conteo declarada por métrica y cuadre contra las cifras de `docs/datos.md`.
- [ ] **Fase 3** — payload pre-agregado + tablero; pie con fecha de descarga real del corte.
- [ ] `scripts/refrescar-corte.sh` (clonar/pull de los 8 repos + hash y fecha de cada archivo).
- [ ] Definir destino de presentación (interno del área vs publicación web) — decisión del usuario.
- [ ] `@revisar` el tablero contra las cifras base antes de mostrarlo a terceros.

## Bitácora

- **2026-10-09** — Revisión de factibilidad de los 8 repos de ANID-GITHUB: veredicto **factible con 4 homologaciones obligatorias**. Se midieron 293.629 filas / 77 MB de CSV; cruces verificados (Colaboración ⊂ Histórico 16.426/16.426; Postulaciones→Histórico 99-100% en las 4 subdirecciones de proyectos; Capital Humano 92% contra Becas; región→macrozona cuadra exacto). Se declina la tasa de adjudicación **por institución** (no existe denominador: 85.907 postulaciones no adjudicadas sin institución). Creación del proyecto con toda la evidencia.
