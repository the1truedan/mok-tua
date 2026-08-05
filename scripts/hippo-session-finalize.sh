#!/usr/bin/env bash
# Best-effort post-session Hippo consolidation for wrappers without a native
# SessionEnd hook (for example Grok/Tok tmux sessions).
set -u

if [[ "${HIPPO_AUTO_CONTEXT:-1}" == "0" ]]; then
  exit 0
fi

HIPPO_BIN="${HIPPO_BIN:-hippo}"
LOG_FILE="${HIPPO_SESSION_LOG:-${HOME}/.hippo/logs/wrapper-session.log}"
mkdir -p "$(dirname "${LOG_FILE}")" 2>/dev/null || true

# Hippo's session-end command detaches its worker, runs sleep then capture,
# deduplicates, applies secret filtering, and auto-shares only high-value
# memories. Never make teardown fail because memory capture is unavailable.
"${HIPPO_BIN}" session-end --log-file "${LOG_FILE}" >/dev/null 2>&1 || true
