#!/usr/bin/env bash
# Probe MRGPU Comfy from mock-tua-api (or direct).
set -euo pipefail
BASE="${MOCK_TUA_URL:-http://127.0.0.1:8799}"
MRGPU="${COMFY_MRGPU_URL:-http://192.168.1.5:8188}"

echo "== MRGPU Comfy probe via API =="
if curl -fsS "$BASE/v1/probe/comfy" -o /tmp/mock-tua-probe.json; then
  python3 -m json.tool </tmp/mock-tua-probe.json
else
  echo "API down; direct probe $MRGPU"
  curl -fsS --max-time 5 "$MRGPU/system_stats" | head -c 400 || {
    echo "MRGPU unreachable. Options:"
    echo "  1) host runtime: bash ~/grokcode/scripts/comfy_mrgpu_host_runtime.sh start"
    echo "  2) docker (needs nvidia-ctk): docker compose -f docker-compose.mrgpu.yml up -d"
    exit 1
  }
fi
echo "OK smoke_mrgpu"
