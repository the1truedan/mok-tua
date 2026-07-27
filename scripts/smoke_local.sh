#!/usr/bin/env bash
# Local smoke: health + parse + estimate + dry-run create from fixture.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${MOCK_TUA_URL:-http://127.0.0.1:8799}"
FIX="$ROOT/fixtures/sample_instructor_story.md"

echo "== MOCK-TUA smoke (local) =="
echo "base=$BASE"

if ! curl -fsS "$BASE/healthz" >/tmp/mock-tua-health.json; then
  echo "API not up. Try: cd $ROOT && docker compose up -d --build"
  echo "Or host: cd $ROOT/api && MOCK_TUA_CONFIG=$ROOT/config WORK_FALLBACK=$ROOT/work python3 -m uvicorn app:app --port 8799"
  exit 1
fi
python3 -m json.tool </tmp/mock-tua-health.json | head -40

MD="$(python3 -c "import json,pathlib; print(json.dumps({'markdown': pathlib.Path('$FIX').read_text()}))")"

echo "== parse =="
curl -fsS -X POST "$BASE/v1/parse" -H 'content-type: application/json' -d "$MD" | python3 -m json.tool | head -50

echo "== estimate =="
curl -fsS -X POST "$BASE/v1/estimate" -H 'content-type: application/json' -d "$MD" | python3 -m json.tool | head -60

echo "== dry-run create =="
RUN_BODY="$(python3 -c "import json,pathlib; print(json.dumps({'markdown': pathlib.Path('$FIX').read_text(), 'dry_run': True}))")"
curl -fsS -X POST "$BASE/v1/runs" -H 'content-type: application/json' -d "$RUN_BODY" | tee /tmp/mock-tua-run.json | python3 -m json.tool | head -80

echo "== list runs =="
curl -fsS "$BASE/v1/runs" | python3 -m json.tool | head -40

echo "OK mock-tua smoke_local"
