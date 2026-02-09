#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-18000}"
WEB_HOST="${WEB_HOST:-127.0.0.1}"
WEB_PORT="${WEB_PORT:-14173}"
SOURCE_ID="${SOURCE_ID:-source-smoke}"
PAYLOAD_FILE="${PAYLOAD_FILE:-$ROOT_DIR/design/tokens/figma/theme-config.json}"
API_LOG="${API_LOG:-/tmp/qadms_smoke_api.log}"
WEB_LOG="${WEB_LOG:-/tmp/qadms_smoke_web.log}"

if [ -x "$ROOT_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

port_in_use() {
  local host="$1"
  local port="$2"
  "$PYTHON_BIN" - "$host" "$port" <<'PY'
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

wait_for_url() {
  local url="$1"
  local attempts="${2:-30}"
  local sleep_s="${3:-0.2}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$sleep_s"
  done
  return 1
}

if ! "$PYTHON_BIN" -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  cat <<MSG
Missing dependencies for smoke test.
Install them with:
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r apps/api/requirements.txt
MSG
  exit 1
fi

if [ ! -f "$PAYLOAD_FILE" ]; then
  echo "Payload file not found: $PAYLOAD_FILE"
  exit 1
fi

if [ "$(port_in_use "$API_HOST" "$API_PORT")" = "1" ]; then
  echo "API port $API_HOST:$API_PORT is already in use. Override API_PORT and retry."
  exit 1
fi

if [ "$(port_in_use "$WEB_HOST" "$WEB_PORT")" = "1" ]; then
  echo "Web port $WEB_HOST:$WEB_PORT is already in use. Override WEB_PORT and retry."
  exit 1
fi

cd "$ROOT_DIR"

"$PYTHON_BIN" -m uvicorn apps.api.src.main:app --host "$API_HOST" --port "$API_PORT" >"$API_LOG" 2>&1 &
API_PID=$!
"$PYTHON_BIN" -m http.server "$WEB_PORT" --bind "$WEB_HOST" --directory apps/web >"$WEB_LOG" 2>&1 &
WEB_PID=$!

cleanup() {
  kill "$API_PID" "$WEB_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

wait_for_url "http://$API_HOST:$API_PORT/health" 50 0.2 || {
  echo "API failed health check startup. See $API_LOG"
  exit 1
}

wait_for_url "http://$WEB_HOST:$WEB_PORT" 50 0.2 || {
  echo "Web server failed startup. See $WEB_LOG"
  exit 1
}

HEALTH_JSON="$(curl -fsS "http://$API_HOST:$API_PORT/health")"
IMPORT_JSON="$(curl -fsS -X POST "http://$API_HOST:$API_PORT/api/v1/sources/$SOURCE_ID/tokens/import/figma" \
  -H 'content-type: application/json' \
  --data-binary "@$PAYLOAD_FILE")"
AUDIT_JSON="$(curl -fsS -X POST "http://$API_HOST:$API_PORT/api/v1/sources/$SOURCE_ID/audits/rules" \
  -H 'content-type: application/json' \
  --data-binary "@$PAYLOAD_FILE")"
REPORT_JSON="$(curl -fsS -X POST "http://$API_HOST:$API_PORT/api/v1/sources/$SOURCE_ID/audits/report" \
  -H 'content-type: application/json' \
  --data-binary "@$PAYLOAD_FILE")"
WEB_HTML="$(curl -fsS "http://$WEB_HOST:$WEB_PORT")"

"$PYTHON_BIN" - <<'PY' "$HEALTH_JSON" "$IMPORT_JSON" "$AUDIT_JSON" "$REPORT_JSON" "$SOURCE_ID"
import json
import sys

health = json.loads(sys.argv[1])
import_resp = json.loads(sys.argv[2])
audit_resp = json.loads(sys.argv[3])
report_resp = json.loads(sys.argv[4])
source_id = sys.argv[5]

if health.get("status") != "ok":
    raise SystemExit("Health response is not ok")

if import_resp.get("source_id") != source_id:
    raise SystemExit("Import source_id mismatch")

validation = import_resp.get("validation", {})
if validation.get("valid") is not True:
    raise SystemExit("Import validation.valid is not true")

version = import_resp.get("token_version", {})
if version.get("source") != "figma_export":
    raise SystemExit("token_version.source mismatch")

counts = version.get("token_counts", {})
if counts.get("color", 0) < 1:
    raise SystemExit("Expected at least one color token")

if audit_resp.get("source_id") != source_id:
    raise SystemExit("Audit source_id mismatch")

summary = audit_resp.get("summary", {})
if "total_violations" not in summary:
    raise SystemExit("Audit summary missing total_violations")

if not isinstance(audit_resp.get("violations", []), list):
    raise SystemExit("Audit violations must be a list")

if report_resp.get("source_id") != source_id:
    raise SystemExit("Report source_id mismatch")

if "generated_at" not in report_resp:
    raise SystemExit("Report missing generated_at")

if report_resp.get("summary") != audit_resp.get("summary"):
    raise SystemExit("Report summary should match audit summary for same payload")

if report_resp.get("violations") != audit_resp.get("violations"):
    raise SystemExit("Report violations should match audit violations for same payload")
PY

if ! grep -q "QADMS Token Import Console" <<<"$WEB_HTML"; then
  echo "Web UI content check failed"
  exit 1
fi

cat <<MSG
Smoke test passed.
- API:  http://$API_HOST:$API_PORT/health
- Web:  http://$WEB_HOST:$WEB_PORT
- Payload: $PAYLOAD_FILE
- Logs: $API_LOG, $WEB_LOG
MSG
