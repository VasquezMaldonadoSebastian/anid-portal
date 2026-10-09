# Manifiesto del corte crudo

**Fecha de descarga:** 2026-10-09 12:39 (hora Chile)
**Directorio:** `data/crudo/`

El CSV y el XLSX de cada base son **el mismo contenido en dos formatos** (verificado: mismos
conteos), así que el total de filas se cuenta **sólo sobre los CSV** — sumar ambos duplicaría
cada base. Los XLSX quedan listados como espejo, con su propio conteo, para detectar que un
formato se actualice y el otro no.

| Repo | Archivo | Formato | Filas | Tamaño (MB) | sha256 (primeros 16) |
|------|---------|---------|-------|-------------|----------------------|
| `Becas` | `BDH_BECAS SCH.csv` | csv | 19288 | 7.1 | `31160ee12aa97e21` |
| `Becas` | `BDH_BECAS SCH.xlsx` | xlsx | 19288 | 2.5 | `e72eaecb61bac90a` |
| `Colaboracion_Institucional` | `CONSOLIDADO_INSTITUCIONES.csv` | csv | 33731 | 6.3 | `cf3e5ffb3627320c` |
| `Colaboracion_Institucional` | `CONSOLIDADO_INSTITUCIONES.xlsx` | xlsx | 33731 | 1.5 | `5114a59ec9a11ed1` |
| `Colaboracion_Institucional` | `SPI_INVESTIGADORES.csv` | csv | 20620 | 3.8 | `a16c1d42310cf822` |
| `Colaboracion_Institucional` | `SPI_INVESTIGADORES.xlsx` | xlsx | 20620 | 1.1 | `78c3bdf206e4e3b3` |
| `Consulta-Publica-Politica-de-Acceso-Abierto` | `BBDD_Consulta_PAA..csv` | csv | 732 | 1.1 | `1dba9907c517170f` |
| `FONDECYT-Abstracts` | `Abstract_Iniciación_2016_2025.csv` (latin-1) | csv | 3499 | 0.6 | `50129998e8cd02c4` |
| `FONDECYT-Abstracts` | `Abstract_Iniciación_2016_2025.xlsx` | xlsx | 3499 | 0.2 | `91a5bf60145fe64f` |
| `FONDECYT-Abstracts` | `Abstract_Postdoctorado_2016_2025.csv` | csv | 2684 | 0.4 | `b5f7a3e10064468e` |
| `FONDECYT-Abstracts` | `Abstract_Postdoctorado_2016_2025.xlsx` | xlsx | 2684 | 0.1 | `0c16f8c876a36c29` |
| `FONDECYT-Abstracts` | `Abstract_Regular_2016_2025.csv` | csv | 5846 | 0.7 | `da29b81f283f3fcf` |
| `FONDECYT-Abstracts` | `Abstract_Regular_2016_2025.xlsx` | xlsx | 5846 | 0.3 | `7253d68e737bfa6a` |
| `Historico-de-Proyectos-Adjudicados` | `BDH_HISTORICA.csv` | csv | 49014 | 22.7 | `f7e1659b058d5101` |
| `Historico-de-Proyectos-Adjudicados` | `BDH_HISTORICA.xlsx` | xlsx | 49014 | 8.8 | `3966b23a6720b8f6` |
| `Historico-de-Proyectos-Adjudicados` | `BDH_PROYECTOS_MILENIO.csv` | csv | 136 | 0.1 | `14235d26873d8fa7` |
| `Historico-de-Proyectos-Adjudicados` | `BDH_PROYECTOS_MILENIO.xlsx` | xlsx | 136 | 0.1 | `c0c05223a4c7b943` |
| `Palabras_claves` | `BD_Palabras_claves_Becas.csv` | csv | 17245 | 2.3 | `037051b7ec694e5f` |
| `Palabras_claves` | `BD_Palabras_claves_Becas.xlsx` | xlsx | 17245 | 0.7 | `0e66b979cdb2096e` |
| `Palabras_claves` | `BD_Palabras_claves_Proyectos.csv` | csv | 12873 | 1.7 | `3cef921749313da0` |
| `Palabras_claves` | `BD_Palabras_claves_Proyectos.xlsx` | xlsx | 12873 | 0.7 | `e15825d18dcad648` |
| `Postulaciones` | `POSTULACIONES_2016_2025.csv` | csv | 139517 | 33.3 | `1d104d4c4b29cf89` |
| `Postulaciones` | `POSTULACIONES_2016_2025.xlsx` | xlsx | 139517 | 9.4 | `527e124ce1f12398` |
| `Postulaciones` | `POSTULACIONES_MILENIO.csv` | csv | 1205 | 0.3 | `6c18acb253353f56` |
| `Postulaciones` | `POSTULACIONES_MILENIO.xlsx` | xlsx | 1205 | 0.1 | `0abcbf472e9d2cdf` |

**CSV (base canónica):** 13 archivos · **306.390 filas**
**XLSX (espejo. no se suma):** 12 archivos · 305.658 filas

**Sin discrepancias entre CSV y XLSX.**

> Cifras de referencia por archivo en `docs/datos.md`. Si un conteo de este manifiesto
> difiere del documentado, gana este manifiesto y `docs/datos.md` debe corregirse.
