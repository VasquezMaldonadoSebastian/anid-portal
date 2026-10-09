"""Deflactores: llevar montos de distintos años a pesos del año base.

Fuente versionada: `config/deflactores.csv` (IPC anual de Chile del Banco Mundial,
generado por `scripts/deflactores.py`). El tablero **no** consulta la red: lee el CSV,
así que la serie es auditable y el año base queda congelado en el archivo.

Convenciones del proyecto:
- `monto_clp` = nominal, lo que dice la resolución de adjudicación.
- `monto_clp_real` = pesos del **año base** (2025), calculado como
  `monto_clp × IPC(base) / IPC(año)`.
- Un año sin índice (2026) deja el monto real en nulo y la fila marcada: **no se estima**.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO = RAIZ / "config" / "deflactores.csv"


@dataclass(frozen=True)
class Deflactores:
    """Serie de IPC anual con su año base y su fuente, lista para deflactar."""

    serie: dict[int, float]
    base: int
    fuente: str
    fecha_consulta: str

    @property
    def anios(self) -> list[int]:
        return sorted(self.serie)

    def tiene(self, anio: int | None) -> bool:
        return anio is not None and int(anio) in self.serie

    def factor(self, anio: int | float | None) -> float | None:
        """Multiplicador a pesos del año base. None si no hay índice para ese año."""
        if anio is None or pd.isna(anio):
            return None
        a = int(anio)
        if a not in self.serie or a == self.base:
            return 1.0 if a == self.base else None
        return self.serie[self.base] / self.serie[a]

    def a_pesos_constantes(
        self, monto: float | None, anio: int | float | None
    ) -> float | None:
        """Monto en pesos del año base. None si falta el monto o el índice."""
        if monto is None or pd.isna(monto):
            return None
        f = self.factor(anio)
        return None if f is None else float(monto) * f

    def aplicar(self, df: pd.DataFrame, col_monto: str = "monto_clp", col_anio: str = "anno_fallo") -> pd.DataFrame:
        """Agrega `monto_clp_real` y `deflactor` a un DataFrame de hechos."""
        out = df.copy()
        out["deflactor"] = out[col_anio].map(self.factor)
        out["monto_clp_real"] = out[col_monto] * out["deflactor"]
        return out


def cargar_deflactores(ruta: Path | None = None) -> Deflactores:
    """Lee `config/deflactores.csv`. Falla ruidosamente si no existe: sin esto no hay montos reales."""
    archivo = ruta or ARCHIVO
    if not archivo.exists():
        raise FileNotFoundError(
            f"falta {archivo} — corre scripts/deflactores.py para generarlo"
        )
    df = pd.read_csv(archivo, sep=";", dtype={"anio": int, "ipc": float, "base": int})
    base = int(df["base"].iloc[0])
    return Deflactores(
        serie=dict(zip(df["anio"], df["ipc"], strict=True)),
        base=base,
        fuente=str(df["fuente"].iloc[0]),
        fecha_consulta=str(df["fecha_consulta"].iloc[0]),
    )
