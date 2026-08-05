#!/usr/bin/env bash
# FramePack Studio launcher — shared ai-data models, no package-local re-download.
#
# Policy:
#   - HF_HOME → /mnt/ai-data/models/hf_hub  (via package hf_download symlink)
#   - LoRAs   → /mnt/ai-data/models/loras
#   - Outputs → /mnt/ai-data/work/framepack/outputs
#   - Prefer --offline when hub snapshots already exist
#
# Usage (on MRGPU):
#   bash scripts/run_framepack_shared_models.sh --install-deps   # SM GUI + CLI envs
#   bash scripts/run_framepack_shared_models.sh --offline --server 0.0.0.0 --port 7865
#   Stability Matrix Packages → Launch (uses package/venv → host-local SM 3.10)
set -euo pipefail

SHARED_MODELS="${SHARED_MODELS:-/mnt/ai-data/models}"
HF_HUB="${HF_HUB:-${SHARED_MODELS}/hf_hub}"
FP_PKG="${FP_PKG:-/mnt/ai-data/stability-matrix/Data/Packages/FramePack Studio}"
# SM Assets Python (Stability Matrix package venv baseline on Linux)
SM_PY_DEFAULT="/mnt/ai-data/stability-matrix/Data/Assets/Python/cpython-3.10.18-linux-x86_64-gnu/bin/python3"
SM_PY="${FRAMEPACK_SM_PYTHON:-$SM_PY_DEFAULT}"
# Host-local venvs (never put site-packages on NFS package tree)
#   SM310 — preferred for SM GUI (same 3.10 as package/venv; package/venv → symlink here)
#   CLI   — optional 3.12 path used by older launcher installs
HOST_SM_ENV_ROOT="${FRAMEPACK_SM_HOST_ENV:-$HOME/pinokio-host-runtimes/framepack-sm310-linux-amd64}"
HOST_SM_VENV="${HOST_SM_ENV_ROOT}/env"
HOST_ENV_ROOT="${FRAMEPACK_HOST_ENV:-$HOME/pinokio-host-runtimes/framepack-linux-amd64}"
HOST_VENV="${HOST_ENV_ROOT}/env"
UV_BIN="${UV_BIN:-$HOME/.local/bin/uv}"
UV_CACHE_DIR="${UV_CACHE_DIR:-/mnt/ai-data/uv-cache/mrgpu}"
export UV_CACHE_DIR
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"
# Preferred shared work tree (NFS). Mac (uid 501) often creates 755 dirs Linux
# uid 1000 cannot write — ensure_writable falls back to $HOME.
OUT_DIR="${FRAMEPACK_OUT:-/mnt/ai-data/work/framepack/outputs}"
META_DIR="${FRAMEPACK_META:-/mnt/ai-data/work/framepack/metadata}"
RECEIPT_DIR="${FRAMEPACK_RECEIPTS:-/mnt/ai-data/work/framepack/receipts}"
FALLBACK_ROOT="${FRAMEPACK_FALLBACK_ROOT:-$HOME/work/framepack}"

INSTALL_DEPS=0
LINK_SM_VENV=1
PASSTHRU=()
for a in "$@"; do
  if [[ "$a" == "--install-deps" ]]; then
    INSTALL_DEPS=1
  elif [[ "$a" == "--no-link-sm-venv" ]]; then
    LINK_SM_VENV=0
  else
    PASSTHRU+=("$a")
  fi
done
set -- "${PASSTHRU[@]}"

ensure_writable() {
  # usage: ensure_writable VARNAME preferred_path fallback_subdir
  local _var="$1" _pref="$2" _fb_sub="$3"
  local _fb="${FALLBACK_ROOT}/${_fb_sub}"
  mkdir -p "$_pref" 2>/dev/null || true
  if [[ -d "$_pref" ]] && touch "${_pref}/.write_test_$$" 2>/dev/null; then
    rm -f "${_pref}/.write_test_$$"
    printf -v "$_var" '%s' "$_pref"
    return 0
  fi
  mkdir -p "$_fb"
  if touch "${_fb}/.write_test_$$" 2>/dev/null; then
    rm -f "${_fb}/.write_test_$$"
    echo "WARN: $_pref not writable (NFS uid/mode?) → using $_fb" >&2
    printf -v "$_var" '%s' "$_fb"
    return 0
  fi
  echo "ERROR: neither $_pref nor $_fb writable" >&2
  return 1
}

if [[ ! -d "$FP_PKG" ]]; then
  echo "FramePack package missing: $FP_PKG" >&2
  exit 1
fi

ensure_writable OUT_DIR "$OUT_DIR" "outputs"
ensure_writable META_DIR "$META_DIR" "metadata"
ensure_writable RECEIPT_DIR "$RECEIPT_DIR" "receipts"
# HF hub is shared read-heavy; mkdir if missing but do not fail launch if not writable
mkdir -p "$HF_HUB" 2>/dev/null || true

# Ensure package HF_HOME path is the shared hub (studio.py hardcodes ./hf_download)
if [[ -L "$FP_PKG/hf_download" ]] || [[ ! -e "$FP_PKG/hf_download" ]]; then
  ln -sfn "$HF_HUB" "$FP_PKG/hf_download"
elif [[ -d "$FP_PKG/hf_download" && ! -L "$FP_PKG/hf_download" ]]; then
  echo "WARN: $FP_PKG/hf_download is a real directory — move/merge into $HF_HUB then replace with symlink" >&2
fi

# Settings overlay (LoRA + outputs on shared tree)
mkdir -p "$FP_PKG/.framepack"
cat > "$FP_PKG/.framepack/settings.json" <<JSON
{
  "lora_dir": "${SHARED_MODELS}/loras",
  "output_dir": "${OUT_DIR}",
  "metadata_dir": "${META_DIR}",
  "shared_models_root": "${SHARED_MODELS}",
  "hf_home": "${HF_HUB}",
  "prohibit_package_local_redownload": true
}
JSON

export HF_HOME="$HF_HUB"
export HUGGINGFACE_HUB_CACHE="${HF_HUB}/hub"
export TRANSFORMERS_CACHE="${HF_HUB}/transformers"
export DIFFUSERS_CACHE="${HF_HUB}/diffusers"
# Comfy/SM already own checkpoints under SHARED_MODELS; do not point HF into random homes
export HF_HUB_DISABLE_TELEMETRY=1

OFFLINE_ARGS=()
# Auto-offline if any hunyuan hub snapshot looks present
if [[ -d "$HF_HUB/hub" ]] && ls -d "$HF_HUB/hub"/models--*hunyuan* >/dev/null 2>&1; then
  export HF_HUB_OFFLINE=1
  OFFLINE_ARGS+=(--offline)
  echo "Shared Hunyuan hub snapshot detected → HF_HUB_OFFLINE=1 --offline"
fi
# User can force online with FRAMEPACK_ALLOW_DOWNLOAD=1
if [[ "${FRAMEPACK_ALLOW_DOWNLOAD:-0}" == "1" ]]; then
  unset HF_HUB_OFFLINE || true
  OFFLINE_ARGS=()
  echo "FRAMEPACK_ALLOW_DOWNLOAD=1 → online hub allowed (still writes into shared HF_HUB)"
fi

# Honor explicit --offline from caller
for a in "$@"; do
  if [[ "$a" == "--offline" ]]; then
    export HF_HUB_OFFLINE=1
  fi
done

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
RECEIPT="$RECEIPT_DIR/framepack_launch_${STAMP}.json"
python3 - <<PY || echo "WARN: receipt write skipped" >&2
import json, os, time, sys
from pathlib import Path
rec = {
  "schema": "framepack_shared_launch.v1",
  "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "fp_pkg": "$FP_PKG",
  "shared_models": "$SHARED_MODELS",
  "hf_home": "$HF_HUB",
  "hf_hub_offline": os.environ.get("HF_HUB_OFFLINE"),
  "allow_download": os.environ.get("FRAMEPACK_ALLOW_DOWNLOAD", "0"),
  "output_dir": "$OUT_DIR",
  "metadata_dir": "$META_DIR",
  "receipt_dir": "$RECEIPT_DIR",
  "symlink_hf_download": str(Path("$FP_PKG/hf_download").resolve()) if Path("$FP_PKG/hf_download").exists() else None,
  "policy": "dedupe via /mnt/ai-data/models; prohibit package-local re-download",
}
path = Path("$RECEIPT")
try:
    path.write_text(json.dumps(rec, indent=2))
    print("receipt", path)
except OSError as e:
    print("WARN: could not write receipt:", e, file=sys.stderr)
    sys.exit(1)
PY

# --- Python resolution (prefer import-ready envs; SM 3.10 first for GUI parity) ---
_python_ready() {
  local py="$1"
  [[ -x "$py" ]] || return 1
  PYTHONPATH="$FP_PKG${PYTHONPATH:+:$PYTHONPATH}" "$py" -c "import einops,torch" 2>/dev/null
}

resolve_python() {
  if [[ -n "${FRAMEPACK_PYTHON:-}" && -x "${FRAMEPACK_PYTHON}" ]]; then
    echo "$FRAMEPACK_PYTHON"
    return
  fi
  # SM GUI path: package/venv (often symlink → host SM 3.10)
  if _python_ready "$FP_PKG/venv/bin/python"; then
    echo "$FP_PKG/venv/bin/python"
    return
  fi
  if _python_ready "$HOST_SM_VENV/bin/python"; then
    echo "$HOST_SM_VENV/bin/python"
    return
  fi
  if _python_ready "$HOST_VENV/bin/python"; then
    echo "$HOST_VENV/bin/python"
    return
  fi
  if _python_ready "$FP_PKG/.venv/bin/python"; then
    echo "$FP_PKG/.venv/bin/python"
    return
  fi
  echo ""
}

link_sm_package_venv() {
  # Stability Matrix Launch uses package/venv. Keep site-packages host-local.
  if [[ "$LINK_SM_VENV" != "1" ]]; then
    return 0
  fi
  if [[ ! -x "$HOST_SM_VENV/bin/python" ]]; then
    echo "WARN: SM host venv missing ($HOST_SM_VENV) — skip package/venv link" >&2
    return 0
  fi
  if [[ -L "$FP_PKG/venv" ]]; then
    ln -sfn "$HOST_SM_VENV" "$FP_PKG/venv"
    echo "package/venv → $HOST_SM_VENV (symlink refreshed)"
    return 0
  fi
  if [[ -d "$FP_PKG/venv" ]]; then
    # Empty SM-created venv is ~pip only; back it up once
    if [[ ! -e "$FP_PKG/venv.sm-empty.bak" ]]; then
      echo "Backing up package venv → venv.sm-empty.bak"
      mv "$FP_PKG/venv" "$FP_PKG/venv.sm-empty.bak"
    else
      rm -rf "$FP_PKG/venv"
    fi
  fi
  ln -sfn "$HOST_SM_VENV" "$FP_PKG/venv"
  echo "package/venv → $HOST_SM_VENV (SM GUI Launch uses this)"
}

install_into_venv() {
  local py="$1" label="$2"
  echo "=== install deps → $label ($py) ==="
  "$UV_BIN" pip install --python "$py" \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
  "$UV_BIN" pip install --python "$py" -r "$FP_PKG/requirements.txt"
  PYTHONPATH="$FP_PKG${PYTHONPATH:+:$PYTHONPATH}" "$py" -c \
    "import einops,torch,diffusers_helper,modules; print('ok', 'einops', einops.__version__, 'torch', torch.__version__, 'cuda', torch.cuda.is_available())"
}

install_deps() {
  if [[ ! -x "$UV_BIN" ]]; then
    echo "uv not found at $UV_BIN — install: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    return 1
  fi
  if [[ ! -d "$FP_PKG/diffusers_helper" ]]; then
    echo "ERROR: $FP_PKG/diffusers_helper missing — restore package source:" >&2
    echo "  cd \"$FP_PKG\" && git restore diffusers_helper modules" >&2
    return 1
  fi

  # Primary: SM 3.10 host-local (Stability Matrix Packages → Launch)
  mkdir -p "$HOST_SM_ENV_ROOT"
  if [[ ! -x "$HOST_SM_VENV/bin/python" ]]; then
    if [[ -x "$SM_PY" ]]; then
      echo "Creating SM-compatible host venv (3.10): $HOST_SM_VENV"
      "$UV_BIN" venv "$HOST_SM_VENV" --python "$SM_PY"
    else
      echo "WARN: SM python not found at $SM_PY — falling back to 3.10 from uv" >&2
      "$UV_BIN" venv "$HOST_SM_VENV" --python 3.10
    fi
  fi
  install_into_venv "$HOST_SM_VENV/bin/python" "SM310-host"
  echo "$HOST_SM_VENV/bin/python" >"$HOST_SM_ENV_ROOT/python.path"
  link_sm_package_venv

  # Optional CLI 3.12 env (kept if already present; create only if FRAMEPACK_ALSO_CLI_ENV=1)
  if [[ "${FRAMEPACK_ALSO_CLI_ENV:-0}" == "1" ]]; then
    mkdir -p "$HOST_ENV_ROOT"
    if [[ ! -x "$HOST_VENV/bin/python" ]]; then
      "$UV_BIN" venv "$HOST_VENV" --python 3.12
    fi
    install_into_venv "$HOST_VENV/bin/python" "CLI-3.12-host"
    echo "$HOST_VENV/bin/python" >"$HOST_ENV_ROOT/python.path"
  fi

  echo "Deps ready for SM GUI + launcher."
  echo "  SM host: $HOST_SM_VENV"
  echo "  package/venv: $(readlink -f "$FP_PKG/venv" 2>/dev/null || echo missing)"
  echo "Re-launch FramePack Studio from Stability Matrix Packages UI, or:"
  echo "  bash $0 --offline --server 0.0.0.0 --port 7865"
}

if [[ "$INSTALL_DEPS" == "1" ]]; then
  install_deps
  # --install-deps alone: stop unless user also passed launch args
  if [[ $# -eq 0 ]]; then
    exit 0
  fi
fi

# Refresh SM link if host env exists (GUI path)
if [[ -x "$HOST_SM_VENV/bin/python" ]]; then
  link_sm_package_venv || true
fi

PY="$(resolve_python)"
if [[ -z "$PY" ]]; then
  echo "ERROR: no FramePack venv. Run once on MRGPU:" >&2
  echo "  bash $0 --install-deps" >&2
  echo "SM host env: $HOST_SM_VENV" >&2
  exit 1
fi

# Package modules are on-disk (not pip) — must be on PYTHONPATH
export PYTHONPATH="$FP_PKG${PYTHONPATH:+:$PYTHONPATH}"

# Preflight: package source + import
if [[ ! -d "$FP_PKG/diffusers_helper" ]]; then
  echo "ERROR: diffusers_helper missing under $FP_PKG (incomplete SM package)." >&2
  echo "  cd \"$FP_PKG\" && git restore diffusers_helper modules" >&2
  exit 1
fi
if ! PYTHONPATH="$FP_PKG${PYTHONPATH:+:$PYTHONPATH}" "$PY" -c "import einops,torch,diffusers_helper" 2>/dev/null; then
  echo "ERROR: venv missing deps (einops/torch/diffusers_helper)." >&2
  echo "  SM GUI uses package/venv — often empty until --install-deps links host SM 3.10 env." >&2
  echo "  bash $0 --install-deps" >&2
  exit 1
fi

cd "$FP_PKG"

# Parse bind/port from passthru for shared runtime registry (dual lifecycle).
FP_BIND="${FRAMEPACK_BIND:-0.0.0.0}"
FP_PORT="${FRAMEPACK_PORT:-7864}"
_args=("$@")
for ((i=0; i<${#_args[@]}; i++)); do
  if [[ "${_args[$i]}" == "--server" && $((i+1)) -lt ${#_args[@]} ]]; then
    FP_BIND="${_args[$((i+1))]}"
  fi
  if [[ "${_args[$i]}" == "--port" && $((i+1)) -lt ${#_args[@]} ]]; then
    FP_PORT="${_args[$((i+1))]}"
  fi
done

RUNTIME_DIR="${MOCK_TUA_RUNTIME_DIR:-/mnt/ai-data/work/mok-tua/runtime}"
mkdir -p "$RUNTIME_DIR" 2>/dev/null || true
RUNTIME_JSON="$RUNTIME_DIR/framepack_studio.json"
# Registry before exec (pid = this process group leader; mok-tua also records spawn pid).
CMD_JSON=$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' _ "$PY" studio.py "${OFFLINE_ARGS[@]}" "$@")
export RUNTIME_JSON FP_BIND FP_PORT FP_PKG SHARED_MODELS HF_HOME CMD_JSON
python3 - <<'PY' 2>/dev/null || true
import json, os, time
from pathlib import Path
path = Path(os.environ["RUNTIME_JSON"])
port = os.environ.get("FP_PORT") or "7864"
try:
    port_i = int(port)
except ValueError:
    port_i = None
rec = {
  "schema": "mok_tua_runtime.v1",
  "id": "framepack_studio",
  "owner": os.environ.get("FRAMEPACK_OWNER", "mok_tua"),
  "pid": os.getpid(),
  "host_role": "gpu-host",
  "bind": os.environ.get("FP_BIND", "0.0.0.0"),
  "port": port_i,
  "open": f"http://gpu-host:{port}/",
  "cmd": json.loads(os.environ.get("CMD_JSON") or "[]"),
  "fp_pkg": os.environ.get("FP_PKG"),
  "shared_models": os.environ.get("SHARED_MODELS"),
  "hf_home": os.environ.get("HF_HOME"),
  "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "source": "run_framepack_shared_models.sh",
}
try:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, indent=2) + "\n")
    print("runtime", path)
except OSError as e:
    import sys
    print("WARN runtime registry:", e, file=sys.stderr)
PY

echo "Launching FramePack with SHARED_MODELS=$SHARED_MODELS HF_HOME=$HF_HOME PY=$PY"
echo "LAN open: http://gpu-host:${FP_PORT}/  (bind ${FP_BIND})"
# mok-tua spawn records parent bash pid + process group for stop.
exec "$PY" studio.py "${OFFLINE_ARGS[@]}" "$@"
