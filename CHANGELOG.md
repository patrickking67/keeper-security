# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Versions below are
the MCP server version (`manifest.json`, `pyproject.toml`); plugin manifests
carry their own versions.

## [Unreleased]

### Security

- Reject line breaks and NUL in every Commander command and argument. With
  `mc_id`, commands run through `--batch-mode` one per line, so a line break
  let a value such as `tree\nlogout` run `logout` past the refusal list.
- `keeper_run_command` now strips a `keeper` prefix separated by any whitespace,
  so `keeper\tlogout` is refused like `keeper logout`.
- Updated locked dependencies to patched versions (Pillow 13.0.0, cryptography
  50.0.2, PyJWT 2.15.1, authlib 1.9.5, mcp 1.30.0, fastmcp 3.4.11, urllib3 2.8.0
  and others), clearing the open Dependabot advisories against `uv.lock`.

### Added

- Offline pytest suite for the Commander wrapper, tool gating, redaction,
  manifest agreement and the stdio handshake.
- `scripts/check.sh`, the single check command (ruff, pytest, plugin validation,
  `claude plugin validate --strict`), also run in CI.
- AGENTS.md, CHANGELOG.md, llms.txt, .editorconfig, .gitattributes, CODEOWNERS,
  Dependabot config, PR and issue templates, and a GitHub Actions workflow.
- `.python-version` pinning Python 3.13 so `uv sync` does not pick an
  interpreter without wheels for every dependency.

### Changed

- `keeper.mcpb` and the `legacy-*.bundle` files are no longer tracked; build the
  bundle with `task mcpb`. They remain in git history.
- `manifest.json` and `pyproject.toml` declare the Apache-2.0 license.
- docs/mcp-server.md lists all 26 tools and uses portable paths.

## [0.1.0] - 2026-07-08

### Added

- 2026-06-10: local stdio MCP server `keeper-mcp` wrapping Keeper Commander, with
  vault, enterprise, MSP, reporting and device-approval tools, secret redaction and
  a guarded `keeper_run_command` escape hatch.
- 2026-07-08: "Keeper-Security" marketplace for Claude Code and Cursor with the
  keeper-admin, keeper-msp, keeper-secrets and keeper-setup plugins, display names,
  and MCPB packaging.

### Security

- 2026-07-08: starlette and pydantic-settings updated to patched versions.
