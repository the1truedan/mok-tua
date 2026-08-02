#!/usr/bin/env bash
# Dry-run smoke for still/video provider routing (no cloud spend).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API="${MOCK_TUA_URL:-http://127.0.0.1:8799}"
MD="$(python3 -c "import pathlib; print(pathlib.Path('$ROOT/fixtures/sample_instructor_story.md').read_text())")"

echo "== healthz =="
curl -sf "$API/healthz" | python3 -m json.tool | head -40

echo "== info providers =="
curl -sf "$API/v1/info" | python3 -c "import sys,json; d=json.load(sys.stdin); print('still', list((d.get('still_providers') or {}).keys())); print('video', list((d.get('video_providers') or {}).keys())); print('defaults', d.get('defaults'))"

for PROVIDER in local_sd_minimal local_qwen_edit grok_imagine nano_banana; do
  echo "== dry run still_provider=$PROVIDER =="
  curl -sf "$API/v1/runs" -H 'content-type: application/json' -d "$(python3 - <<PY
import json
print(json.dumps({
  "markdown": '''$MD''',
  "dry_run": True,
  "still_provider": "$PROVIDER",
  "video_provider": "local_wan",
  "qqq": "QQQ1" if "$PROVIDER" in ("grok_imagine", "nano_banana") else "QQQ0",
}))
PY
)" | python3 -c "import sys,json; d=json.load(sys.stdin); s=(d.get('shots') or [{}])[0]; print('run', d.get('run_id')); print('still_provider', d.get('still_provider')); print('panel_prompt', (s.get('panel_prompt') or '')[:160]); print('still_status', (s.get('still') or {}).get('status'), (s.get('still') or {}).get('provider') or (s.get('still') or {}).get('graph_mode'))"
done

echo "OK smoke_providers"
