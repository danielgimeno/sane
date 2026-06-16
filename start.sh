#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BACKEND_PID=""
FRONTEND_PID=""

log() {
  printf '\033[1;34m[sae]\033[0m %s\n' "$*"
}

err() {
  printf '\033[1;31m[sae]\033[0m %s\n' "$*" >&2
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "No se encontró '$1'. Instálalo antes de continuar."
    exit 1
  fi
}

cleanup() {
  trap - EXIT INT TERM
  if [[ -n "$BACKEND_PID" ]] || [[ -n "$FRONTEND_PID" ]]; then
    log "Deteniendo servicios..."
    [[ -n "$BACKEND_PID" ]] && kill "$BACKEND_PID" 2>/dev/null || true
    [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

usage() {
  cat <<'EOF'
Uso: ./start.sh [modo]

Modos:
  dev   Backend + frontend Vite en desarrollo (por defecto)
  prod  Compila el frontend y sirve todo en http://localhost:8000

Variables de entorno:
  SKIP_INSTALL=1  Omite poetry install y npm install
EOF
}

MODE="${1:-dev}"

case "$MODE" in
  -h|--help|help)
    usage
    exit 0
    ;;
  dev|prod)
    ;;
  *)
    err "Modo desconocido: $MODE"
    usage
    exit 1
    ;;
esac

require_cmd poetry
require_cmd node
require_cmd npm

if [[ "${SKIP_INSTALL:-0}" != "1" ]]; then
  log "Instalando dependencias del backend..."
  poetry install

  log "Instalando dependencias del frontend..."
  (cd frontend && npm install)
else
  log "Omitiendo instalación de dependencias (SKIP_INSTALL=1)."
fi

if [[ "$MODE" == "prod" ]]; then
  log "Compilando frontend..."
  (cd frontend && npm run build)

  log "Iniciando backend en http://localhost:8000"
  poetry run sae &
  BACKEND_PID=$!

  wait "$BACKEND_PID"
  exit 0
fi

log "Iniciando backend en http://localhost:8000"
poetry run sae &
BACKEND_PID=$!

log "Iniciando frontend en http://localhost:5173"
(
  cd frontend
  exec npm run dev
) &
FRONTEND_PID=$!

log ""
log "SAE en marcha (modo desarrollo):"
log "  Frontend: http://localhost:5173"
log "  API:      http://localhost:8000"
log ""
log "Pulsa Ctrl+C para detener."

wait "$BACKEND_PID" "$FRONTEND_PID"
