#!/usr/bin/env bash
# The one check command: lint, format, offline tests, manifest and plugin
# validation. CI runs exactly this. Nothing here contacts a Keeper tenant.
#
# Usage: scripts/check.sh
# Optional tools are used when installed and skipped with a note otherwise:
#   claude (Claude Code CLI)  -> claude plugin validate --strict
#   rumdl                     -> Markdown lint

set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n== %s ==\n' "$1"; }

# Run quietly; print the full output only when the command fails.
quiet() {
  local out
  if ! out=$("$@" 2>&1); then
    printf '%s\n' "$out"
    echo "FAILED: $*"
    exit 1
  fi
}

step "Dependencies (uv sync --locked)"
uv sync --locked --quiet

step "Lint (ruff check)"
uv run ruff check .

step "Format (ruff format --check)"
uv run ruff format --check .

step "Tests (pytest, offline)"
uv run pytest

step "Plugins, marketplaces and skills (scripts/validate-plugins.sh)"
quiet ./scripts/validate-plugins.sh
echo "validate-plugins.sh passed"

step "Claude Code manifests (claude plugin validate --strict)"
if command -v claude > /dev/null 2>&1; then
  for target in . plugins/*/; do
    quiet claude plugin validate --strict "$target"
    echo "ok: ${target%/}"
  done
else
  echo "skipped: claude CLI not installed"
fi

step "Markdown (rumdl)"
if command -v rumdl > /dev/null 2>&1; then
  rumdl check .
else
  echo "skipped: rumdl not installed"
fi

printf '\nAll checks passed.\n'
