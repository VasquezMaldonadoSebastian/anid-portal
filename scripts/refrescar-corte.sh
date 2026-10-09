#!/usr/bin/env bash
# refrescar-corte.sh — trae (o actualiza) los 8 repositorios de ANID-GITHUB y regenera el manifiesto.
#
# Uso:  bash scripts/refrescar-corte.sh
#
# Deja los archivos en data/crudo/<repo>/ y escribe data/crudo/_manifiesto.md con
# repo, archivo, filas reales, tamaño, sha256 y fecha de descarga.
# Los datos crudos NO se versionan (ver .gitignore).

set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DATOS="$RAIZ/data/crudo"
REPOS=(
  Historico-de-Proyectos-Adjudicados
  Colaboracion_Institucional
  Postulaciones
  Becas
  Palabras_claves
  FONDECYT-Abstracts
  Instructivo_descarga
  Consulta-Publica-Politica-de-Acceso-Abierto
)

# Los programas nativos (git, gh) no reciben rutas tipo MSYS: hay que pasarles ruta Windows.
winpath() {
  if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi
}

mkdir -p "$DATOS"
cd "$DATOS"

for repo in "${REPOS[@]}"; do
  if [ -d "$repo/.git" ]; then
    printf -- '--- %s: actualizando\n' "$repo"
    ( cd "$repo" && git pull --depth 1 --quiet 2>&1 | tail -2 ) || printf '    (sin cambios o sin red)\n'
  else
    printf -- '--- %s: clonando\n' "$repo"
    gh repo clone "ANID-GITHUB/$repo" "$(winpath "$DATOS/$repo")" -- --depth 1 --quiet \
      || printf '    (fallo el clone de %s)\n' "$repo"
  fi
done

echo "--- generando manifiesto"
# py es un programa nativo: necesita ruta Windows, no la ruta MSYS de $RAIZ
py -3.11 "$(winpath "$RAIZ/scripts/manifiesto.py")"
echo "Listo. Manifiesto en data/crudo/_manifiesto.md"
