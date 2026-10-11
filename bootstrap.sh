#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
EXPECTED_REMOTE="https://github.com/hcchengithub/peforth.git"

if [[ ! -f "$ROOT/pyproject.toml" || ! -f "$ROOT/peforth/repl.py" ]]; then
  printf 'Not a complete peforth source checkout: %s\n' "$ROOT" >&2
  exit 2
fi
if ! command -v git >/dev/null 2>&1; then
  printf 'Git is required. Install Git and retry.\n' >&2
  exit 2
fi
REMOTE="$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)"
if [[ "$REMOTE" != "$EXPECTED_REMOTE" ]]; then
  printf 'Unexpected origin remote in %s: %s\n' "$ROOT" "${REMOTE:-<missing>}" >&2
  printf 'Expected: %s\n' "$EXPECTED_REMOTE" >&2
  exit 2
fi
BRANCH="$(git -C "$ROOT" branch --show-current)"
if [[ "$BRANCH" != "v2-migration-orphan-bootstrap" ]]; then
  printf 'Refusing bootstrap on unexpected branch: %s\n' "${BRANCH:-<detached>}" >&2
  exit 2
fi
if [[ -n "$(git -C "$ROOT" status --porcelain --untracked-files=all)" ]]; then
  printf 'Notice: checkout has local changes; bootstrap will not alter or discard source files.\n'
fi

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  printf 'Python 3.10+ is required (tried %s).\n' "$PYTHON" >&2
  exit 2
fi
"$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' || {
  printf 'Python 3.10+ is required.\n' >&2
  exit 2
}
VENV="$ROOT/.venv"
if [[ -e "$VENV" && ! -f "$VENV/pyvenv.cfg" ]]; then
  printf 'Refusing to reuse an existing non-venv path: %s\n' "$VENV" >&2
  exit 2
fi
if [[ -f "$VENV/pyvenv.cfg" ]] && ! "$VENV/bin/python" -c 'import sys; raise SystemExit(0 if sys.platform != "win32" else 1)' 2>/dev/null; then
  printf 'Existing .venv is not a usable Linux/WSL environment; use a separate WSL checkout.\n' >&2
  exit 2
fi
if [[ ! -f "$VENV/pyvenv.cfg" ]]; then
  "$PYTHON" -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install -e "$ROOT"
printf '\npeforth v2 editable install is ready. Source files were not updated.\n'
printf 'Run from any directory: %s/.venv/bin/f --help\n' "$ROOT"
printf 'Smoke test: %s/.venv/bin/f -e 10 20 + . cr\n' "$ROOT"
printf 'To use bare f in this shell: export PATH="%s/.venv/bin:$PATH"\n' "$ROOT"
printf 'No commit, reset, checkout, or push was performed.\n'
