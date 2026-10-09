#!/usr/bin/env bash
# Uso diario
set -euo pipefail
cd "$(dirname "$0")/.."

py -3.11 -m pytest tests/
if [ ! -f outputs/proyectos.parquet ]; then
  echo "Falta el modelo curado: construyéndolo..."
  py -3.11 scripts/construir-modelo.py
fi
py -3.11 -m streamlit run src/tablero/app.py
