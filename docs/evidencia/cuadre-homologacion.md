# Cuadre de la homologación (Fase 1)

**Generado por** `scripts/cuadre_homologacion.py` · **Filas de entrada:** histórico 49.014 · becas 19.288 · colaboración 33.731 · postulaciones 139.517

## H1 — Región
- filas: 49014 · sin clasificar: 0 · etiquetas crudas: 24 → destinos: 19
- METROPOLITANA: **27212** (crudo con la etiqueta más usada: 26.334)
- NUBLE: 57 · OHIGGINS: 340 · MAGALLANES: 370 · AYSEN: 120
- sin clasificar en histórico: ninguna
- becas (REGION_DE_ORIGEN): sin clasificar 0 · valores pendientes: ninguno
- colaboración (REGIONINSTITUCION): sin clasificar 0 · valores pendientes: ninguno
- postulaciones (REGION_EJECUCION): sin clasificar 0 · valores pendientes: ninguno

## H2 — Macrozona derivada
- histórico: excepciones contra el archivo = **0** de 49014 filas
- becas: excepciones contra el archivo = **1** de 19288 filas
  - detalle: {'REGION METROPOLITANA DE SANTIAGO': 1}
- postulaciones: excepciones contra el archivo = **0** de 139517 filas
- RM: esperado 27212 · obtenido 27212 → OK
- CENTRO SUR: esperado 7138 · obtenido 7138 → OK
- CENTRO: esperado 6082 · obtenido 6082 → OK
- SUR: esperado 4803 · obtenido 4803 → OK
- NORTE: esperado 2357 · obtenido 2357 → OK
- SIN INFORMACION: esperado 697 · obtenido 697 → OK
- AUSTRAL: esperado 490 · obtenido 490 → OK
- EXTRANJERO: esperado 124 · obtenido 124 → OK
- MULTIREGIONAL: esperado 111 · obtenido 111 → OK

## H3 — Moneda y monto
- rótulos homologados: {'MILES DE PESOS': 46563, 'SIN MONEDA': 2413, 'EUROS': 38}
- sin monto (monto_clp nulo): **2463** de 49014
- en euros: 38 filas · monto_eur suma 338.702
- 2020-2025. sólo pesos con monto (11395 de 11782 filas del período): **$2.095.227 millones**
- por macrozona:
  - RM: 6093 filas · $1.160.514 millones
  - CENTRO SUR: 1894 filas · $339.928 millones
  - CENTRO: 1417 filas · $256.865 millones
  - SUR: 1206 filas · $193.685 millones
  - NORTE: 611 filas · $104.357 millones
  - AUSTRAL: 123 filas · $35.016 millones
  - MULTIREGIONAL: 25 filas · $3.720 millones
  - SIN INFORMACION: 26 filas · $1.143 millones

## H4 — Subdirección
- histórico: 7 rótulos → 6 destinos · sin clasificar 0
  - PROYECTOS DE INVESTIGACION: 33392
  - REDES ESTRATEGIA Y CONOCIMIENTO: 5951
  - INVESTIGACION APLICADA: 5667
  - NO APLICA: 2484
  - CENTROS E INVESTIGACION ASOCIATIVA: 1332
  - CAPITAL HUMANO: 188

## H5 — Tipo de beneficiario y sexo
- tipo beneficiario: 6 rótulos → 4 · {'PERSONA NATURAL': 37187, 'PERSONA JURIDICA': 11565, 'SIN INFORMACION': 201, 'NATURAL O JURIDICA': 61}
- sexo en becas: 4 rótulos → 2 · {'HOMBRE': 10269, 'MUJER': 9019}

## H6 — Institución
- histórico: 1749 nombres → 1733 normalizados
- colaboración: 5694 nombres → 5574 normalizados · RUT 2476 válidos de 2500 crudos
- RUT con más de un nombre: **373** · nombres con más de un RUT: **21**

## H7 — Rol institucional
- 65 rótulos crudos → 9 canónicos · sin clasificar: **0** filas
  - BENEFICIARIA / PRINCIPAL: 13968
  - ASOCIADA / PARTICIPANTE: 12273
  - EXTRANJERA: 2820
  - PATROCINANTE: 2367
  - APORTANTE / COFINANCIAMIENTO: 1293
  - POSTULANTE: 395
  - ALBERGANTE / PROCEDENCIA: 362
  - OTRA ENTIDAD: 233
  - NO APLICA: 20

## H8 — Unidad de conteo
- histórico: filas 49014 · códigos 48707 · pares (código, año) 48835
- códigos repetidos: 136 (con contenido distinto entre sus filas: 136)
- postulaciones: filas 139517 · códigos 139369
