#!/usr/bin/env bash
# Run mock-tua-api on host (no Docker) — easiest hybrid path to live :8787/:8188.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/api"
export MOCK_TUA_CONFIG="${MOCK_TUA_CONFIG:-$ROOT/config}"
export WORK_FALLBACK="${WORK_FALLBACK:-$ROOT/work}"
export WORK_ROOT="${WORK_ROOT:-/Volumes/ai-data/work/story-anim}"
export HEADROOM_BASE="${HEADROOM_BASE:-http://127.0.0.1:8787/v1}"
export COMFY_MAC_URL="${COMFY_MAC_URL:-http://127.0.0.1:8188}"
export COMFY_GPU_URL="${COMFY_GPU_URL:-http://<gpu-host-ip>:8188}"
export MOCK_TUA_DRY_RUN="${MOCK_TUA_DRY_RUN:-1}"
export MOCK_TUA_QQQ="${MOCK_TUA_QQQ:-QQQ0}"
# shellcheck disable=SC1091
if [[ -f "$ROOT/.env" ]]; then set -a; source "$ROOT/.env"; set +a; fi
if [[ -f "$HOME/ai-gateway/.env" && -z "${LITELLM_MASTER_KEY:-}" ]]; then
  # shellcheck disable=SC1091
  set -a; source "$HOME/ai-gateway/.env"; set +a
fi
VENV="${ROOT}/.venv"
if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q -r requirements.txt
fi
exec "$VENV/bin/python" -m uvicorn app:app --host 127.0.0.1 --port "${MOCK_TUA_PORT:-8799}"
