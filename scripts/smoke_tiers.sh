#!/usr/bin/env bash
# T0–T4 director stack smoke scorecard.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python3 scripts/mok_tua_cli.py smoke --tiers "${1:-T0-T4}"
