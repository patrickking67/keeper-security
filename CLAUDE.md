# keeper-security

## Overview

One repo, two products:

1. **Local stdio MCP server** named `keeper` that exposes the Keeper Security
   vault and MSP/enterprise admin console. Thin wrapper: every tool shells out
   to the Keeper Commander CLI (`keeper`) non-interactively using a
   persistent-login config file, and returns captured output (JSON where
   Commander supports `--format=json`, table text otherwise). 14+ tools:
   curated vault/enterprise/MSP/reporting tools plus a generic
   `keeper_run_command` escape hatch. Packaged as an MCPB bundle
   (`manifest.json`, `keeper.mcpb`, `.mcpbignore`).
2. **"Keeper Security" plugin marketplace** for Claude Code and Cursor
   (`.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json`,
   marketplace name `Keeper-Security`) with four plugins under `plugins/`:
   keeper-admin, keeper-msp, keeper-secrets, keeper-setup. Skills also work
   with Codex/Copilot via the standard `skills/` layout (Vercel Skills CLI).
   Content derived from Keeper's Apache-2.0 keeper-agent-kit and extended.

## Tech stack

- Python 3.11+, FastMCP 3.x (`fastmcp`), stdio transport
- `keepercommander` (>=17.3,<19) as a dependency so the `keeper` CLI ships in the venv
- Packaging: pyproject.toml (hatchling), src layout, console script `keeper-mcp`
- Environment management: uv (`uv sync`); plain venv + `pip install -e .` also works
- Plugin validation: bash + jq (`scripts/validate-plugins.sh`, bash-3.2 compatible)

## Layout

- `src/keeper_mcp/server.py` - FastMCP server, all tool definitions, `main()` entry
- `src/keeper_mcp/commander.py` - subprocess wrapper: config/binary/timeout resolution,
  one-shot and `--batch-mode` invocation, managed-company chaining
  (`switch-to-mc`/`switch-to-msp`), JSON extraction from noisy stdout, secret redaction
- `manifest.json` / `keeper.mcpb` / `.mcpbignore` - MCPB packaging (bundle excludes
  the marketplace content)
- `.claude-plugin/marketplace.json`, `.cursor-plugin/marketplace.json` - marketplaces
  (must list exactly the plugins under `plugins/`)
- `plugins/<name>/` - each has `.claude-plugin/plugin.json`,
  `.cursor-plugin/plugin.json` (with `logo`), `.mcp.json` (bundles the
  `keeper-docs` HTTP MCP server, `https://docs.keeper.io/~gitbook/mcp`),
  `skills/<skill>/SKILL.md` (+ `references/`), optional `commands/` and `agents/`
- `scripts/validate-plugins.sh` - full validation; run via `task validate`
- `docs/mcp-server.md` - MCP server auth bootstrap runbook and client registration
- `README.md` - marketplace + MCPB overview and install paths

## Build / run / verify

```bash
uv sync                                        # create .venv and install
uv run python -c "import keeper_mcp.server"    # import check (task mcp-check)
uv run keeper-mcp                              # start the stdio server (Ctrl+C to stop)
task validate                                  # plugin/marketplace validation
```

There is no test suite yet; verify server changes with the import check plus a
JSON-RPC handshake (pipe `initialize` / `notifications/initialized` /
`tools/list` lines into `.venv/bin/keeper-mcp`). Verify plugin changes with
`task validate` - it must pass with zero errors.

## Conventions (MCP server)

- **stdio purity:** never print to stdout. Diagnostics go to stderr. Subprocess output
  is always captured (`capture_output=True`) and the child's stdin is `/dev/null` or an
  explicit pipe so Commander can never read or write the MCP protocol stream.
- **No startup env validation:** the server must start and complete the MCP handshake
  with no env vars and no config file. Config existence is checked on first command;
  the error carries the bootstrap runbook.
- **Error handling:** explicit, no silent failures. `CommanderError` includes the
  command, exit code meaning (1 general / 2 auth / 3 syntax / 4 not found), and
  stderr/stdout truncated to ~2000 chars. Tools re-raise as `ToolError` so the message
  always reaches the client as an `isError` result.
- **Secret redaction:** `keeper_get_record` / `keeper_search_records` output is
  scrubbed (field types password, secret, pinCode, oneTimeCode, keyPair, hidden/secured
  note, passkey, plus password-like dict keys) unless `reveal_secrets=true`. Never add
  a code path that calls `get --unmask` or logs raw record output.
- **Interactivity ban:** never run `shell`, `login`, `connect`, or bare `add`/`edit`;
  never run `logout` (it permanently invalidates the persistent-login session).
- **mc_id pattern:** managed-company scoping is always a self-contained batch chain
  `switch-to-mc <id>` -> command -> `switch-to-msp`; never rely on sticky context.
- Tool names are snake_case with the `keeper_` prefix; every parameter has a pydantic
  `Field` description; read-only tools carry `readOnlyHint`, the escape hatch carries
  `destructiveHint`.
- Commander calls are serialized via a module lock (config file gets rewritten with
  rotated tokens on each login).

## Conventions (plugins / marketplace)

- SKILL.md frontmatter is single-line `name:` and `description:` (the validator
  enforces this convention; folded `>` descriptions break trigger checks).
- Fenced code blocks always declare a language (`text` for shell-transcript
  style examples).
- Skills/commands/agents never print secret values into transcripts; mutating
  operations (rotate, msp-remove, share changes) always require explicit user
  confirmation in their instructions.
- Command syntax in skills must be verified against docs.keeper.io (each plugin
  bundles the `keeper-docs` MCP server for this; endpoint
  `https://docs.keeper.io/~gitbook/mcp`, tools `searchDocumentation`/`getPage`).
- Claude and Cursor plugin manifests stay in sync (Cursor adds `logo`).
- Adding a plugin: create `plugins/<name>/` with both manifests + `.mcp.json`,
  add it to BOTH marketplace.json files, and extend
  `scripts/validate-plugins.sh` (trigger keywords, section checks, references).
- `scripts/validate-plugins.sh` must stay bash-3.2 compatible (no `mapfile`) -
  macOS default bash runs it locally.

## Attribution rule

Never add AI attribution anywhere: no co-author or sign-off trailers, no
generated-by footers, and no AI/bot identities in commits, files, PRs, or
metadata of any kind.
