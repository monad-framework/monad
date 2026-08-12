#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(git -C "$SCRIPT_ROOT" rev-parse --show-toplevel 2>/dev/null || printf '%s\n' "$SCRIPT_ROOT")"
export EOS_ROOT="$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'ERROR: python3 is required by the repository-local EOS control tooling.\n' >&2
  exit 127
fi

exec python3 "$ROOT/tools/eos/eos.py" "$@"
