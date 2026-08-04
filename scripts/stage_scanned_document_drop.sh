#!/usr/bin/env bash
# Stage scanner drops without parsing, deleting, or publishing them.
set -euo pipefail

ROOT="${MOK_TUA_DOCUMENT_WORK_ROOT:-${PWD}/work/document-intake}"
SOURCE="${1:-}"
if [[ -z "${SOURCE}" || ! -d "${SOURCE}" ]]; then
  echo "usage: $0 SCANNER_DROP_DIRECTORY" >&2
  exit 2
fi

mkdir -p "${ROOT}"/{incoming,normalized,pdf,forms,catalog,receipts,quarantine,review}
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
MANIFEST="${ROOT}/catalog/drop-${STAMP}.jsonl"

find "${SOURCE}" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.pdf' \) -print0 |
while IFS= read -r -d '' file; do
  base="$(basename "${file}")"
  dest="${ROOT}/incoming/${base}"
  if [[ -e "${dest}" ]]; then
    echo "duplicate filename; quarantining: ${base}" >&2
    cp -p "${file}" "${ROOT}/quarantine/${STAMP}-${base}"
    dest="${ROOT}/quarantine/${STAMP}-${base}"
  else
    cp -p "${file}" "${dest}"
  fi
  hash="$(shasum -a 256 "${dest}" | awk '{print $1}')"
  size="$(wc -c < "${dest}" | tr -d ' ')"
  printf '{"schema":"document_drop.v1","received_at_utc":"%s","source_filename":%s,"staged_path":%s,"sha256":"%s","bytes":%s,"review_status":"pending","aida_route":"pending"}\n' \
    "${STAMP}" "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "${base}")" \
    "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "${dest}")" "${hash}" "${size}" >> "${MANIFEST}"
done

echo "staged manifest: ${MANIFEST}"
