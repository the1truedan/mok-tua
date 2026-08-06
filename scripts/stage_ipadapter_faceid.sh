#!/usr/bin/env bash
# Stage IPAdapter FaceID + SD1.5 face adapters into shared /mnt/ai-data/models/ipadapter
# Run ON gpu-host (or: ssh gpu-host 'bash -s' < scripts/stage_ipadapter_faceid.sh)
set -euo pipefail
IPAD="${IPAD:-/mnt/ai-data/models/ipadapter}"
LORAS="${LORAS:-/mnt/ai-data/models/loras}"
mkdir -p "$IPAD" "$LORAS"

download() {
  local url="$1" dest="$2"
  if [[ -f "$dest" && -s "$dest" ]]; then
    echo "OK exists $(ls -lh "$dest" | awk '{print $5,$9}')"
    return 0
  fi
  echo "GET $dest"
  wget -c -O "${dest}.partial" "$url"
  mv "${dest}.partial" "$dest"
  ls -lh "$dest"
}

BASE="https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main"
download "$BASE/ip-adapter-faceid-plusv2_sd15.bin" "$IPAD/ip-adapter-faceid-plusv2_sd15.bin"
download "$BASE/ip-adapter-faceid-plusv2_sd15_lora.safetensors" "$IPAD/ip-adapter-faceid-plusv2_sd15_lora.safetensors"
download "$BASE/ip-adapter-faceid_sd15.bin" "$IPAD/ip-adapter-faceid_sd15.bin"
download "$BASE/ip-adapter-faceid_sd15_lora.safetensors" "$IPAD/ip-adapter-faceid_sd15_lora.safetensors"

BASE2="https://huggingface.co/h94/IP-Adapter/resolve/main/models"
download "$BASE2/ip-adapter-plus-face_sd15.safetensors" "$IPAD/ip-adapter-plus-face_sd15.safetensors"
download "$BASE2/ip-adapter_sd15.safetensors" "$IPAD/ip-adapter_sd15.safetensors"
download "$BASE2/ip-adapter-plus_sd15.safetensors" "$IPAD/ip-adapter-plus_sd15.safetensors"

for f in ip-adapter-faceid-plusv2_sd15_lora.safetensors ip-adapter-faceid_sd15_lora.safetensors; do
  if [[ -f "$IPAD/$f" && ! -e "$LORAS/$f" ]]; then
    ln -sfn "$IPAD/$f" "$LORAS/$f"
    echo "linked loras/$f"
  fi
done

echo "FILECOUNT=$(find "$IPAD" -maxdepth 1 -type f \( -name '*.bin' -o -name '*.safetensors' \) | wc -l)"
ls -lh "$IPAD"/*.{bin,safetensors} 2>/dev/null || true
