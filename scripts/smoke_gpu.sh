#!/usr/bin/env bash
# Probe GPU Comfy from mock-tua-api (or direct).
set -euo pipefail
BASE="${MOCK_TUA_URL:-http://127.0.0.1:8799}"
GPU="${COMFY_GPU_URL:-http://<gpu-host-ip>:8188}"

echo "== GPU Comfy probe via API =="
if curl -fsS "$BASE/v1/probe/comfy" -o /tmp/mock-tua-probe.json; then
  python3 -m json.tool </tmp/mock-tua-probe.json
else
  echo "API down; direct probe $GPU"
  curl -fsS --max-time 5 "$GPU/system_stats" | head -c 400 || {
    echo "GPU unreachable. Options:"
    echo "  1) host runtime: bash ~/grokcode/scripts/comfy_gpu_host_runtime.sh start"
    echo "  2) docker (needs nvidia-ctk): docker compose -f docker-compose.gpu.yml up -d"
    exit 1
  }
fi
echo "OK smoke_gpu"
