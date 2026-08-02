#!/usr/bin/env bash
# Launch mok-tua conductor TUI (C64 skin default).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"

SKIN="${MOK_TUA_TUI_SKIN:-c64}"
EXTRA=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skin) SKIN="$2"; shift 2 ;;
    --repl) EXTRA+=(--repl); shift ;;
    *) EXTRA+=("$1"); shift ;;
  esac
done

# Prefer venv if present
PY=python3
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
fi

# Install textual lightly if missing and not forcing repl
if [[ " ${EXTRA[*]} " != *" --repl "* ]]; then
  if ! "$PY" -c "import textual" 2>/dev/null; then
    echo "[run_tui] textual not installed — using stdlib REPL (pip install -r tui/requirements.txt for full-screen)" >&2
    EXTRA+=(--repl)
  fi
fi

exec "$PY" -m tui --skin "$SKIN" "${EXTRA[@]}"
