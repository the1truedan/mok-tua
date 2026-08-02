#!/usr/bin/env bash
# F-order ROBUST custom_nodes install for mok-tua on MRGPU (shared NFS pool).
# Run ON mrgpu (or: ssh mrgpu 'bash -s' < this_script).
# Does NOT install avoid-list nodes. Pins numpy after deps.
set -euo pipefail

CN="${COMFY_CUSTOM_NODES:-/mnt/ai-data/comfyui/custom_nodes}"
VENV="${COMFY_VENV:-/mnt/ai-data/comfyui/envs/mrgpu/.venv}"
PY="${VENV}/bin/python"
LOG_DIR="${COMFY_USER:-/mnt/ai-data/comfyui/user/mrgpu}"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOG="${LOG_DIR}/robust_install_${STAMP}.log"
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG") 2>&1

echo "=== comfy_robust_install_mrgpu $STAMP ==="
echo "CN=$CN VENV=$VENV"
id
[ -d "$CN" ] || { echo "missing CN"; exit 1; }

# --- ensure pip ---
if ! "$PY" -m pip --version >/dev/null 2>&1; then
  echo "bootstrap pip"
  "$PY" -m ensurepip --upgrade 2>/dev/null || true
  curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
  "$PY" /tmp/get-pip.py
fi
"$PY" -m pip install -U pip setuptools wheel

clone_node() {
  local id="$1" url="$2"
  local dest="$CN/$id"
  if [ -d "$dest/.git" ] || [ -d "$dest" ]; then
    echo "HAVE $id — pull ff-only if git"
    if [ -d "$dest/.git" ]; then
      git -C "$dest" pull --ff-only 2>/dev/null || echo "  pull skip/fail $id"
    fi
  else
    echo "CLONE $id"
    git clone --depth 1 "$url" "$dest"
  fi
  # Manager .cnr-id writable on multi-uid NFS
  if [ -d "$dest/.git" ]; then
    chmod a+rwx "$dest/.git" 2>/dev/null || true
  fi
  if [ -f "$dest/requirements.txt" ]; then
    echo "  pip -r requirements.txt ($id)"
    "$PY" -m pip install -r "$dest/requirements.txt" || echo "  WARN pip reqs failed $id"
  fi
}

# --- F2 P0/P1 installs ---
clone_node ComfyUI-KJNodes https://github.com/kijai/ComfyUI-KJNodes.git
clone_node ComfyUI-GGUF https://github.com/city96/ComfyUI-GGUF.git
clone_node ComfyUI-Inspire-Pack https://github.com/ltdrdata/ComfyUI-Inspire-Pack.git
clone_node efficiency-nodes-comfyui https://github.com/jags111/efficiency-nodes-comfyui.git
clone_node ComfyUI-Florence2 https://github.com/kijai/ComfyUI-Florence2.git

# --- shared deps (identity / pose / video helpers) ---
echo "=== shared deps ==="
"$PY" -m pip install \
  'numpy==1.26.4' \
  'opencv-python-headless>=4.8' \
  'onnxruntime-gpu>=1.17' \
  insightface \
  onnx \
  imageio-ffmpeg \
  librosa \
  'transformers>=4.40' \
  accelerate \
  || true
"$PY" -m pip install 'numpy==1.26.4'

# --- disable avoid-list (G + known broken) ---
# MUST move outside custom_nodes — Comfy still imports *.DISABLED_* subdirs
DISABLE_ROOT="$(dirname "$CN")/custom_nodes_disabled_mok_tua"
mkdir -p "$DISABLE_ROOT"
disable_node() {
  local id="$1"
  local src="$CN/$id"
  local dst="$DISABLE_ROOT/${id}.DISABLED_MOK_TUA"
  if [ -d "$src" ] && [ ! -e "$dst" ]; then
    echo "DISABLE $id -> $dst"
    mv "$src" "$dst"
  elif [ -d "$dst" ]; then
    echo "already disabled $id"
  else
    echo "skip disable (missing) $id"
  fi
}
disable_node ComfyUI-Moore-AnimateAnyone
disable_node ComfyUI-AniPortrait
disable_node ComfyUI-BlenderAI-node
disable_node ComfyUI-BlenderAI
disable_node ComfyUI-Assistant
# RVC if present
disable_node ComfyUI-RVC
disable_node ComfyUI-Inference-Core-Nodes  # missing inference_core_nodes module

# --- dedupe custom-scripts: keep ComfyUI-Custom-Scripts ---
if [ -d "$CN/comfyui-custom-scripts" ] && [ -d "$CN/ComfyUI-Custom-Scripts" ]; then
  if [ ! -e "$DISABLE_ROOT/comfyui-custom-scripts.DISABLED_DUP" ]; then
    echo "DEDUP disable comfyui-custom-scripts"
    mv "$CN/comfyui-custom-scripts" "$DISABLE_ROOT/comfyui-custom-scripts.DISABLED_DUP"
  fi
fi
# noise module
if [ -f "$CN/install_all_uv.py" ]; then
  mv "$CN/install_all_uv.py" "$DISABLE_ROOT/install_all_uv.py" 2>/dev/null || true
fi

# --- bulk .git write for Manager ---
echo "=== chmod a+rwx on .git tops ==="
find "$CN" -maxdepth 2 -type d -name .git -exec chmod a+rwx {} \; 2>/dev/null || true

# --- light clean AppleDouble LoRA noise that breaks LoRA-Manager ---
echo "=== remove models/Lora/._* appledouble (capped) ==="
find /mnt/ai-data/models/Lora -maxdepth 1 -name '._*' -type f 2>/dev/null | head -500 | while read f; do
  rm -f "$f" 2>/dev/null || true
done

echo "=== DONE log=$LOG ==="
echo "Restart ComfyUI on mrgpu to load new nodes, then: scripts/smoke_comfy_robust.sh"
