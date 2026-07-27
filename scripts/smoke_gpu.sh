#!/usr/bin/env bash
# Probe gpu-host Comfy from mock-tua-api (or direct).
set -euo pipefail
BASE="${MOCK_TUA_URL:-http://127.0.0.1:8799}"
gpu-host="${COMFY_gpu-host_URL:-http://REDACTED-LAN-IP:8188}"

echo "== gpu-host Comfy probe via API =="
if curl -fsS "$BASE/v1/probe/comfy" -o /tmp/mock-tua-probe.json; then
  python3 -m json.tool </tmp/mock-tua-probe.json
else
  echo "API down; direct probe $gpu-host"
  curl -fsS --max-time 5 "$gpu-host/system_stats" | head -c 400 || {
    echo "gpu-host unreachable. Options:"
    echo "  1) host runtime: bash ~/grokcode/scripts/comfy_gpu-host_host_runtime.sh start"
    echo "  2) docker (needs nvidia-ctk): docker compose -f docker-compose.gpu-host.yml up -d"
    exit 1
  }
fi
echo "OK smoke_gpu-host"
