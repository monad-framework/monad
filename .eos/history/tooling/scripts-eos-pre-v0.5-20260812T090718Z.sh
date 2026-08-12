#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd))"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'ERROR: python3 is required by the repository-local EOS control tooling.\n' >&2
  exit 127
fi

exec python3 "$ROOT/tools/eos/eos.py" "$@"
