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
#   bash /path/to/mok-tua/scripts/run_framepack_shared_models.sh [--offline] [extra studio.py args]
set -euo pipefail

SHARED_MODELS="${SHARED_MODELS:-/mnt/ai-data/models}"
HF_HUB="${HF_HUB:-${SHARED_MODELS}/hf_hub}"
FP_PKG="${FP_PKG:-/mnt/ai-data/stability-matrix/Data/Packages/FramePack Studio}"
# Host-local venv (never NFS) — matches FaceFusion/Maestro pattern
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
PASSTHRU=()
for a in "$@"; do
  if [[ "$a" == "--install-deps" ]]; then
    INSTALL_DEPS=1
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

# --- Python resolution (host venv > package venv > FRAMEPACK_PYTHON) ---
resolve_python() {
  if [[ -n "${FRAMEPACK_PYTHON:-}" && -x "${FRAMEPACK_PYTHON}" ]]; then
    echo "$FRAMEPACK_PYTHON"
    return
  fi
  if [[ -x "$HOST_VENV/bin/python" ]]; then
    echo "$HOST_VENV/bin/python"
    return
  fi
  if [[ -x "$FP_PKG/venv/bin/python" ]]; then
    echo "$FP_PKG/venv/bin/python"
    return
  fi
  if [[ -x "$FP_PKG/.venv/bin/python" ]]; then
    echo "$FP_PKG/.venv/bin/python"
    return
  fi
  echo ""
}

install_deps() {
  local py
  if [[ ! -x "$UV_BIN" ]]; then
    echo "uv not found at $UV_BIN — install: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    return 1
  fi
  if [[ ! -d "$FP_PKG/diffusers_helper" ]]; then
    echo "ERROR: $FP_PKG/diffusers_helper missing — restore package source:" >&2
    echo "  cd \"$FP_PKG\" && git restore diffusers_helper modules" >&2
    return 1
  fi
  mkdir -p "$HOST_ENV_ROOT"
  if [[ ! -x "$HOST_VENV/bin/python" ]]; then
    echo "Creating host venv: $HOST_VENV"
    "$UV_BIN" venv "$HOST_VENV" --python 3.12
  fi
  py="$HOST_VENV/bin/python"
  echo "Installing torch (CUDA) into host venv via uv..."
  "$UV_BIN" pip install --python "$py" \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
  echo "Installing requirements.txt via uv..."
  "$UV_BIN" pip install --python "$py" -r "$FP_PKG/requirements.txt"
  echo "$py" >"$HOST_ENV_ROOT/python.path"
  echo "Deps installed. Smoke:"
  PYTHONPATH="$FP_PKG${PYTHONPATH:+:$PYTHONPATH}" "$py" -c \
    "import torch,diffusers_helper,modules; print('ok', torch.__version__, torch.cuda.is_available())"
}

if [[ "$INSTALL_DEPS" == "1" ]]; then
  install_deps
fi

PY="$(resolve_python)"
if [[ -z "$PY" ]]; then
  echo "ERROR: no FramePack venv. Run once on MRGPU:" >&2
  echo "  bash $0 --install-deps" >&2
  echo "Host env target: $HOST_VENV" >&2
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
if ! "$PY" -c "import diffusers_helper" 2>/dev/null; then
  echo "ERROR: venv missing deps (diffusers_helper import path or pip packages)." >&2
  echo "  bash $0 --install-deps" >&2
  exit 1
fi

cd "$FP_PKG"
echo "Launching FramePack with SHARED_MODELS=$SHARED_MODELS HF_HOME=$HF_HOME PY=$PY"
exec "$PY" studio.py "${OFFLINE_ARGS[@]}" "$@"
