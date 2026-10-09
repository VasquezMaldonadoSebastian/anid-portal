# Diseño del tablero — tokens y reglas

**Dónde se toca:** todo el aspecto visual sale de `src/tablero/estilo.py` (tokens + componentes) y
de `.streamlit/config.toml` (tema de la app). **Ninguna vista define colores, tamaños ni formatos a
mano**: si algo se ve mal en las cinco vistas, se arregla en un solo archivo.

## Tokens

| Token | Valor | Uso |
|---|---|---|
| `tinta` | `#0F172A` | texto principal, títulos |
| `tinta_suave` | `#475569` | texto secundario, unidades, pies |
| `borde` | `#E2E8F0` | bordes de tarjetas y tablas |
| `fondo` | `#F8FAFC` | fondo de la app |
| `superficie` | `#FFFFFF` | tarjetas |
| `primario` | `#00539B` | azul institucional: barras principales, tema de Streamlit |
| `acento` | `#00A0DF` | segunda serie (montos reales, instrumentos) |
| `alerta` | `#B45309` | avisos de alcance (unidad, moneda, corte, año en curso) |
| `ok` | `#047857` | reservado para estados positivos |

Tipografía: pila del sistema (`Segoe UI`, `Inter`, `system-ui`). Títulos 1,6 rem · subtítulos 1,05 rem
· cuerpo 0,95 rem · texto menudo 0,8 rem. Los colores de serie son una lista fija y ordenada
(`COLOR["serie"]`): la primera serie siempre es la misma en todas las vistas.

## Componentes

- **Tarjeta de métrica** (`estilo.tarjeta`): etiqueta en mayúsculas, valor grande y **unidad debajo**.
  La unidad no es decorativa: es la regla H8/R8 del proyecto (`filas` ≠ `códigos` ≠ `proyectos`).
- **Aviso** (`estilo.aviso`): fondo ámbar con borde izquierdo. Se usa para lo que el lector tiene que
  saber para no malinterpretar una cifra: unidad de conteo, moneda nominal vs real, fecha y hash del
  corte, y las filas del año en curso que quedan fuera.
- **Tabla** (`st.dataframe` con `width="stretch"`): columnas monetarias con su unidad en el nombre
  («Monto nominal (pesos)» / «Monto real (pesos del año base)»), nunca un «Monto» a secas.

## Reglas de presentación

1. **Ningún número sin unidad**: cada tarjeta declara filas, códigos o proyectos.
2. **Ningún monto sin moneda**: nominal (pesos del año) o real (pesos del año base), siempre rotulado.
3. **Año en curso apagado**: la casilla arranca desmarcada y el pie explica cuántas filas quedan fuera.
4. **Cola larga declarada**: el ranking muestra cuántas instituciones quedaron fuera del corte visible.
5. **Formato chileno**: miles con punto y decimales con coma (`estilo.numero`); los nulos se muestran
   como «—», nunca como 0.
6. **Fuente de cada bloque**: cada vista nombra el corte y los deflactores que usa; el pie lleva la
   fecha y el sha256 del manifiesto.

## Verificación

`py -3.11 scripts/verificar-render.py` ejecuta la app con `streamlit.testing.v1.AppTest`, cambia
filtros y deja el detalle en `docs/evidencia/render-tablero.md`. `tests/test_tablero.py` fija lo
esencial en `pytest`: que corra sin excepción, que las cinco vistas estén montadas, que los avisos
obligatorios aparezcan y que el año en curso venga apagado.
