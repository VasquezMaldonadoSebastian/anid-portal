#!/usr/bin/env bash
# Instalación inicial (una vez por máquina)
set -euo pipefail
cd "$(dirname "$0")/.."

cp -n config/default.yaml config/local.yaml 2>/dev/null || true
echo "Config local lista en config/local.yaml (completar rutas)."

if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt
fi
echo "Setup OK."
