#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
WEB_HOST="${WEB_HOST:-127.0.0.1}"
WEB_PORT="${WEB_PORT:-4173}"

port_in_use() {
  local host="$1"
  local port="$2"
  python3 - "$host" "$port" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(0.2)
try:
    busy = s.connect_ex((host, port)) == 0
finally:
    s.close()
print("1" if busy else "0")
PY
}

if ! python3 -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  cat <<MSG
Missing dependencies for API server.
Install them with:
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r apps/api/requirements.txt
MSG
  exit 1
fi

if [ "$(port_in_use "$API_HOST" "$API_PORT")" = "1" ]; then
  echo "API port $API_HOST:$API_PORT is already in use. Set API_PORT to another port and retry."
  exit 1
fi

if [ "$(port_in_use "$WEB_HOST" "$WEB_PORT")" = "1" ]; then
  echo "Web port $WEB_HOST:$WEB_PORT is already in use. Set WEB_PORT to another port and retry."
  exit 1
fi

cd "$ROOT_DIR"

API_CMD=(python3 -m uvicorn apps.api.src.main:app --host "$API_HOST" --port "$API_PORT")
WEB_CMD=(python3 -m http.server "$WEB_PORT" --bind "$WEB_HOST" --directory apps/web)

"${API_CMD[@]}" >/tmp/qadms_api.log 2>&1 &
API_PID=$!
"${WEB_CMD[@]}" >/tmp/qadms_web.log 2>&1 &
WEB_PID=$!

cleanup() {
  kill "$API_PID" "$WEB_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

cat <<MSG
QADMS local stack started.
- API: http://$API_HOST:$API_PORT/health
- Web: http://$WEB_HOST:$WEB_PORT
Logs:
- /tmp/qadms_api.log
- /tmp/qadms_web.log
Press Ctrl+C to stop both services.
MSG

wait "$API_PID" "$WEB_PID"
