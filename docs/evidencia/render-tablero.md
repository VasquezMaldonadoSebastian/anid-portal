# Verificación del render del tablero (Fase 3)

**Generado por** `scripts/verificar-render.py` (ejecuta `src/tablero/app.py` con `streamlit.testing.v1.AppTest`; el navegador de este entorno bloquea `localhost`).

**Resultado: 28 de 28 verificaciones en verde.**

| Verificación | Resultado | Detalle |
|---|---|---|
| la app corre sin excepción | OK |  |
| vista visible: Panorama territorial | OK |  |
| vista visible: Ranking institucional | OK |  |
| vista visible: Serie temporal | OK |  |
| vista visible: Ficha de institución | OK |  |
| vista visible: Red de colaboración y embudo de postulaciones | OK |  |
| las 5 pestañas principales están montadas | OK | 🗺️ Panorama territorial · 🏛️ Ranking institucional · 📈 Serie temporal · 🔎 Ficha de institución · 🕸️ Red y embudo · Red de colaboración · Embudo de postulaciones |
| aviso de unidad de conteo | OK |  |
| aviso de moneda | OK |  |
| aviso de corte | OK |  |
| mención del índice de precios | OK |  |
| unidad del monto real | OK |  |
| 2026 fuera de los totales por defecto | OK |  |
| existe la casilla de 2026 | OK |  |
| casilla de 2026 apagada al abrir | OK |  |
| filas del histórico visibles | OK |  |
| claves de institución visibles | OK |  |
| filtrar por macrozona no rompe la app | OK |  |
| el filtro acota el panorama (aparece la macrozona elegida) | OK | dataframes antes=7 después=7 |
| el ranking se acota al filtro territorial | OK |  |
| interruptor nominal/real responde | OK |  |
| al incluir 2026 el aviso cambia | OK | el pie pasa a declarar que el año entra |
| el monto real de 2026 no se muestra como 0 | OK | monto real 2026 = nan |
| el total del panorama coincide con el modelo (par código · año) | OK | app=47244 · outputs/=47244 |
| panorama y ranking dan el mismo total con la misma selección | OK | panorama=47244 · ranking=47244 |
| el filtro de instrumento acota los totales | OK | sin filtro=47244 · con REGULAR=19271 |
| el filtro de instrumento queda aplicado en el panel | OK |  |
| el aviso de multirregionalidad sobrevive al filtro territorial | OK | con la institución=True · al filtrar región=True |
