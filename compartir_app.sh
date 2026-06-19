#!/bin/sh
set -eu

APP_PY="/Users/javiermanuelrodriguezrodriguez/Documents/Folleto Assumpta/app.py"
BASE_DIR="/Users/javiermanuelrodriguezrodriguez/Documents/Folleto Assumpta"
PYTHON="/Users/javiermanuelrodriguezrodriguez/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
PORT="${ASSUMPTA_PORT:-5010}"
ACTIVE_URL_FILE="${BASE_DIR}/active_tunnel_url.txt"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "No se encontro cloudflared."
  echo "Instalelo primero o pida a Codex que lo instale para crear una URL temporal."
  exit 1
fi

echo "Iniciando Assumpta en modo compartido..."
ASSUMPTA_HOST=0.0.0.0 ASSUMPTA_PORT="$PORT" "$PYTHON" "$APP_PY" &
APP_PID=$!

cleanup() {
  rm -f "$ACTIVE_URL_FILE"
  kill "$APP_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

echo "Creando URL temporal publica..."
echo "Usuario: pasuntorre"
echo "Contrasena: pasuntorre26.."
cloudflared tunnel --url "http://localhost:${PORT}" 2>&1 | while IFS= read -r line; do
  echo "$line"
  url=$(printf "%s" "$line" | sed -n 's/.*\(https:\/\/[^ ]*trycloudflare\.com\).*/\1/p')
  if [ -n "$url" ]; then
    printf "%s\n" "$url" > "$ACTIVE_URL_FILE"
    echo "URL activa guardada en la app: $url"
  fi
done
