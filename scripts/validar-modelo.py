"""Valida el modelo contra las cifras de control de `docs/datos.md`.

Uso: py -3.11 scripts/validar-modelo.py

Escribe `docs/evidencia/validacion-modelo.md` con cada cifra: esperada, obtenida y veredicto.
Un DESVÍO no se corrige bajando el listón: se investiga. Las cifras esperadas viven acá para que
el validador falle cuando el dato cambie de verdad.

Qué certifica y qué no: hay dos familias de chequeos y conviene no confundirlas.

  - **Independientes**: comparan una lectura de `outputs/` contra una constante medida antes sobre
    los archivos crudos (conteos de filas, RM homologada, colisiones de RUT, sumas de monto...), o
    contra una fuente externa leída directo del disco (`ipc_crudo`, que lee `config/deflactores.csv`
    sin pasar por el objeto del modelo). Si el pipeline cambia, estos fallan.
  - **Internos**: verifican invariantes entre tablas del propio pipeline (aggregados vs hecho,
    dimensión vs hecho). Detectan bugs de agregación, no de extracción: si el hecho estuviera mal
    medido, fallarían igual los dos lados del chequeo.

Un «43/43» certifica que el modelo es coherente consigo mismo y con las cifras de control; la
verificación de las cifras contra el crudo es la auditoría independiente del corte.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from modelo.deflactores import cargar_deflactores  # noqa: E402
from modelo.exportar import construir_todo  # noqa: E402

DESTINO = RAIZ / "docs" / "evidencia" / "validacion-modelo.md"
DEFLACTORES_CSV = RAIZ / "config" / "deflactores.csv"


def ipc_crudo(anio: int) -> float:
    """IPC del año leído DIRECTO del CSV de deflactores, sin pasar por el objeto del modelo.

    Es la fuente independiente con la que se verifica la fórmula de deflactión.
    """
    tabla = pd.read_csv(DEFLACTORES_CSV, sep=";")
    encontrado = tabla.loc[tabla["anio"].eq(anio), "ipc"]
    if encontrado.empty:
        raise ValueError(f"el CSV de deflactores no trae el año {anio}")
    return float(encontrado.iloc[0])


class Chequeo:
    def __init__(self, nombre: str, esperado, obtenido, tolerancia: float = 0.0) -> None:
        self.nombre = nombre
        self.esperado = esperado
        self.obtenido = obtenido
        self.tolerancia = tolerancia

    @property
    def ok(self) -> bool:
        if isinstance(self.esperado, (int, float)) and isinstance(self.obtenido, (int, float)):
            return abs(float(self.esperado) - float(self.obtenido)) <= self.tolerancia
        return self.esperado == self.obtenido

    def __str__(self) -> str:
        marca = "OK" if self.ok else "**DESVÍO**"
        return f"| {self.nombre} | {self.esperado:,} | {self.obtenido:,} | {marca} |".replace(
            ",", "."
        ) if isinstance(self.esperado, (int, float)) else (
            f"| {self.nombre} | {self.esperado} | {self.obtenido} | {marca} |"
        )


def main() -> int:
    meta = construir_todo()
    deflactores = cargar_deflactores()
    salida = RAIZ / "outputs"
    pr = pd.read_parquet(salida / "proyectos.parquet")
    co = pd.read_parquet(salida / "colaboracion.parquet")
    po = pd.read_parquet(salida / "postulaciones.parquet")
    bc = pd.read_parquet(salida / "becas.parquet")
    dim = pd.read_parquet(salida / "dim_institucion.parquet")
    ar = pd.read_parquet(salida / "agg_region.parquet")
    ai = pd.read_parquet(salida / "agg_institucion.parquet")

    anio = pr["anno_fallo"]
    pesos = pr["monto_valido"]
    periodo = pesos & anio.between(2020, 2025)
    rm_periodo = periodo & pr["region"].eq("METROPOLITANA")
    proy_po = po[~po["es_capital_humano"]]

    # colisiones de institución (H5/H6), contadas sobre RUT válidos como en el informe
    co_con_rut = co[co["rut"].notna()]
    rut_con_varios_nombres = int(
        (co_con_rut.groupby("rut")["institucion_normalizada"].nunique() > 1).sum()
    )
    nombre_con_varios_rut = int(
        (co_con_rut.groupby("institucion_normalizada")["rut"].nunique() > 1).sum()
    )
    claves_por_nombre = pr.groupby("institucion")["institucion_clave"].nunique()

    chequeos = [
        # H8 unidad de conteo
        Chequeo("proyectos: filas", 49_014, len(pr)),
        Chequeo("proyectos: códigos únicos", 48_707, pr["codigo_proyecto"].nunique()),
        Chequeo(
            "proyectos: pares (código, año)",
            48_835,
            pr[["codigo_proyecto", "anno_fallo"]].drop_duplicates().shape[0],
        ),
        # H1/H2 territorio
        Chequeo("región sin clasificar", 0, int(pr["region"].eq("NO CLASIFICADO").sum())),
        Chequeo("filas con macrozona asignada", 49_014, int(pr["macrozona"].notna().sum())),
        Chequeo("RM homologada", 27_212, int(pr["region"].eq("METROPOLITANA").sum())),
        Chequeo("Ñuble homologada", 57, int(pr["region"].eq("NUBLE").sum())),
        # H3 moneda y monto
        Chequeo("filas con monto en pesos válido", 46_551, int(pesos.sum())),
        # 2.413 sin rótulo + 12 con rótulo de pesos y valor inutilizable (10 vacíos + 2 literales)
        Chequeo(
            "filas sin monto en pesos",
            2_425,
            int((~pesos & ~pr["moneda"].eq("EUROS")).sum()),
        ),
        Chequeo("filas en euros", 38, int(pr["moneda"].eq("EUROS").sum())),
        Chequeo("RM 2020-2025: filas", 6_093, int(rm_periodo.sum())),
        Chequeo(
            "RM 2020-2025: pesos",
            1_160_514_000_000,
            float(pr.loc[rm_periodo, "monto_clp"].sum()),
            tolerancia=1_000_000,
        ),
        Chequeo("país 2020-2025: filas", 11_395, int(periodo.sum())),
        Chequeo(
            "país 2020-2025: pesos",
            2_095_227_000_000,
            float(pr.loc[periodo, "monto_clp"].sum()),
            tolerancia=1_000_000,
        ),
        # deflactores: todo monto con año cerrado tiene su monto real; 2026 no lo tiene
        Chequeo(
            "montos reales calculados (años con IPC)",
            int((pesos & anio.le(2025)).sum()),
            int(pr.loc[pesos & anio.le(2025), "monto_clp_real"].notna().sum()),
        ),
        Chequeo(
            "montos reales nulos en 2026",
            0,
            int(pr.loc[pesos & anio.eq(2026), "monto_clp_real"].notna().sum()),
        ),
        Chequeo(
            "monto nominal del país (pesos)", 4_978_171_451_662, float(pr.loc[pesos, "monto_clp"].sum())
        ),
        Chequeo(
            # una celda del corte viene como '2E+05': se interpreta tal cual y se cuenta, para que
            # una futura aparición no vuelva a pasar como monto válido en silencio
            "filas con monto en notación científica",
            1,
            int(pr["monto_cientifico"].sum()),
        ),
        Chequeo(
            # verificación de la fórmula con la fuente independiente (el CSV de deflactores)
            "monto real 2025 = nominal 2025 × IPC(2010)/IPC(2025)",
            float(pr.loc[pesos & anio.eq(2025), "monto_clp"].sum())
            * (ipc_crudo(2010) / ipc_crudo(2025)),
            float(pr.loc[pesos & anio.eq(2025), "monto_clp_real"].sum()),
            tolerancia=1.0,
        ),
        # colaboración
        Chequeo("colaboración: filas", 33_731, len(co)),
        Chequeo("colaboración: proyectos", 16_426, co["codigo_proyecto"].nunique()),
        Chequeo("colaboración: roles sin clasificar", 0, int(co["rol"].eq("NO CLASIFICADO").sum())),
        Chequeo("colaboración: RUT válidos", 2_476, co["rut"].nunique()),
        # postulaciones
        Chequeo("postulaciones: filas", 139_517, len(po)),
        Chequeo("postulaciones de proyectos (sin Capital Humano)", 68_133, len(proy_po)),
        Chequeo("adjudicadas de proyectos", 18_233, int(proy_po["adjudicado"].sum())),
        Chequeo(
            "tasa de adjudicación (%)",
            26.8,
            round(100 * proy_po["adjudicado"].sum() / len(proy_po), 1),
            tolerancia=0.05,
        ),
        # becas
        Chequeo("becas: filas", 19_288, len(bc)),
        Chequeo("becas: hombres", 10_269, int(bc["sexo"].eq("HOMBRE").sum())),
        Chequeo("becas: mujeres", 9_019, int(bc["sexo"].eq("MUJER").sum())),
        # dimensión institución (H5/H6): nombres, claves e invariantes
        Chequeo("hecho: nombres de institución distintos", 1_749, int(pr["institucion"].nunique())),
        Chequeo(
            "hecho: nombres normalizados distintos",
            1_733,
            int(pr["institucion_normalizada"].nunique()),
        ),
        Chequeo("hecho: claves de institución distintas", 1_707, int(pr["institucion_clave"].nunique())),
        # la invariante que sostiene el ranking: un nombre nunca cae en dos claves
        Chequeo(
            "invariante: ningún nombre repartido entre dos claves",
            0,
            int((claves_por_nombre > 1).sum()),
        ),
        Chequeo(
            "dim institución: claves del hecho presentes en la dimensión",
            0,
            int((~pr["institucion_clave"].isin(dim["institucion_clave"])).sum()),
        ),
        Chequeo(
            "dim institución: nombres homónimos repartidos en claves distintas",
            21,
            int(dim["nombre_normalizado"].duplicated().sum()),
        ),
        # colisiones, contadas sobre RUT válidos (ver docs/evidencia/instituciones-colisiones.md)
        Chequeo("colaboración: RUT con más de un nombre", 373, rut_con_varios_nombres),
        Chequeo(
            "colaboración: nombres con más de un RUT (ambiguos, no se adivinan)",
            21,
            nombre_con_varios_rut,
        ),
        Chequeo(
            "dim institución: claves de proyectos presentes en la dimensión",
            0,
            int((~pr["institucion_clave"].isin(dim["institucion_clave"])).sum()),
        ),
        # agregados
        Chequeo("agg_region: filas suman el hecho", 49_014, int(ar["filas"].sum())),
        Chequeo(
            "agg_region: monto suma el hecho",
            float(pr.loc[pesos, "monto_clp"].sum()),
            float(ar["monto_clp"].sum()),
            tolerancia=1,
        ),
        Chequeo(
            "agg_region: filas sin monto suman 2.425 pesos + 38 euros",
            2_463,
            int(ar["filas_sin_monto"].sum()),
        ),
        Chequeo(
            "agg_region: filas sin deflactor (2026 con monto)",
            int((pesos & anio.eq(2026)).sum()),
            int(ar["filas_sin_deflactor"].sum()),
        ),
        Chequeo("agg_institucion: filas suman el hecho", 49_014, int(ai["filas"].sum())),
        Chequeo(
            "agg_institucion: monto suma el hecho",
            float(pr.loc[pesos, "monto_clp"].sum()),
            float(ai["monto_clp"].sum()),
            tolerancia=1,
        ),
    ]

    verdes = sum(c.ok for c in chequeos)
    cabecera = [
        "# Validación del modelo curado (Fase 2)",
        "",
        f"**Generado por** `scripts/validar-modelo.py` · **Corte:** {meta['corte']['fecha']} · "
        f"**Deflactores:** {meta['deflactores']['fuente']} (base {meta['deflactores']['base']}, "
        f"consulta {meta['deflactores']['fecha_consulta']})",
        "",
        f"**Resultado: {verdes} de {len(chequeos)} cifras de control reproducidas.**",
        "",
        "| Cifra de control | Esperado | Obtenido | Veredicto |",
        "|---|---|---|---|",
    ]
    cuerpo = [str(c) for c in chequeos]
    filas_agregados = [
        "",
        "## Tamaño de las tablas entregadas",
        "",
        "| Tabla | Filas |",
        "|---|---|",
    ]
    for nombre, n in meta["filas"].items():
        filas_agregados.append(f"| `{nombre}` | {n:,} |".replace(",", "."))
    filas_agregados += [
        "",
        "## Metadatos del corte que alimenta el pie del tablero",
        "",
        "```json",
        json.dumps(meta, ensure_ascii=False, indent=2),
        "```",
    ]

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text("\n".join(cabecera + cuerpo + filas_agregados) + "\n", encoding="utf-8")

    for c in chequeos:
        print(f"{'OK ' if c.ok else 'DESVÍO'} {c.nombre}: esperado {c.esperado} · obtenido {c.obtenido}")
    print(f"\n{verdes}/{len(chequeos)} · escrito {DESTINO}")
    return 0 if verdes == len(chequeos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
