# AGENTS.md

Guide for coding agents working in this repo. Security is the point of this
project: it hands AI agents access to a password vault and an MSP admin console.

## What this repo is

1. **`keeper-mcp`**, a local stdio MCP server (Python, FastMCP 3) with 26 tools.
   Every tool shells out to the Keeper Commander CLI (`keeper`) with a
   persistent-login config file and returns its output. Packaged for Claude
   Desktop as an MCPB bundle.
2. **The "Keeper-Security" plugin marketplace** for Claude Code and Cursor with
   four plugins (keeper-admin, keeper-msp, keeper-secrets, keeper-setup):
   skills, slash commands, agents, and the bundled `keeper-docs` HTTP MCP server.

## Layout

| Path | What it holds |
| --- | --- |
| `src/keeper_mcp/server.py` | All tool definitions, `main()` entry point |
| `src/keeper_mcp/commander.py` | Subprocess wrapper: config, binary, timeout, batch chains, JSON extraction, secret redaction |
| `tests/` | Offline pytest suite (Commander is never executed) |
| `manifest.json`, `.mcpbignore` | MCPB packaging; `keeper.mcpb` is a gitignored build output |
| `.claude-plugin/`, `.cursor-plugin/` | Marketplace manifests; must list exactly the plugins under `plugins/` |
| `plugins/<name>/` | `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json` (adds `logo`), `.mcp.json`, `skills/`, optional `commands/`, `agents/` |
| `scripts/check.sh` | The one check command |
| `scripts/validate-plugins.sh` | Plugin, marketplace and skill validator (bash 3.2 compatible) |
| `docs/mcp-server.md` | Server setup, auth bootstrap, tool list, security notes |

## Commands

Python 3.13 is pinned in `.python-version`; uv provisions it.

```bash
uv sync                    # create .venv with runtime and dev dependencies
scripts/check.sh           # everything CI runs; must pass before any commit
uv run pytest              # tests only
uv run ruff check .        # lint
uv run ruff format .       # format
scripts/validate-plugins.sh   # plugin and marketplace validation only
uv run keeper-mcp          # start the stdio server (needs a Commander config to do real work)
task mcpb                  # build keeper.mcpb (needs the mcpb CLI; do not commit the output)
```

`scripts/check.sh` runs: `uv sync --locked`, ruff check, ruff format --check,
pytest, `validate-plugins.sh`, `claude plugin validate --strict` on the
marketplace and each plugin (skipped if the `claude` CLI is missing), and
`rumdl` if installed. [Taskfile](Taskfile.yaml) wraps the same commands
(`task check`, `task test`, `task validate`).

## Safety rules (do not weaken)

- **Never contact a real Keeper tenant.** Tests stay offline: `tests/conftest.py`
  replaces `subprocess.run` for every test. Do not add a test that runs `keeper`.
- **No secrets anywhere:** no configs, tokens, record UIDs, tenant or company IDs,
  emails of real people, in code, tests, docs or commits. Use `example.com`.
- **Write and destructive gating stays as strict or stricter.** `keeper_transfer_user`
  refuses without `confirm=true`. `keeper_run_command` refuses `shell`, `login`,
  `connect` and `logout` however they are prefixed or cased. Every Commander call
  rejects line breaks and NUL (batch mode would run them as extra commands).
  Annotations: read tools carry `readOnlyHint`, the escape hatch and transfer carry
  `destructiveHint`; `tests/test_server.py` enforces this.
- **Redaction:** `keeper_get_record` and `keeper_search_records` scrub secret fields
  unless `reveal_secrets=true`. Never add a path that runs `get --unmask` or logs raw
  record output.
- **stdio purity:** never print to stdout; diagnostics go to stderr. Child processes
  always capture output and never inherit the server's stdin.
- **No startup validation:** the server must start and answer `initialize` and
  `tools/list` with no env vars and no config (`tests/test_stdio.py`).
- **Managed companies:** `mc_id` is always a self-contained batch chain
  `switch-to-mc <id>` -> command -> `switch-to-msp`.
- User-supplied values are passed through `shlex.quote`. Keep it that way.

## Conventions

- Tool names are snake_case with the `keeper_` prefix; every parameter has a
  pydantic `Field` description. Adding or removing a tool means updating
  `manifest.json` (a test compares them) and the table in `docs/mcp-server.md`.
- Versions in `manifest.json`, `pyproject.toml` and `src/keeper_mcp/__init__.py` must match.
- SKILL.md frontmatter is single-line `name:` and `description:`. Fenced code
  blocks declare a language. Skills never print secret values and require explicit
  user confirmation for mutating operations.
- Verify Commander and KSM syntax against docs.keeper.io (the bundled `keeper-docs`
  MCP server, `https://docs.keeper.io/~gitbook/mcp`) before writing it into a skill.
- Claude and Cursor plugin manifests stay in sync. A new plugin goes in both
  marketplace files and in `scripts/validate-plugins.sh`.
- Dependencies: respect `uv.lock`; update with `uv lock --upgrade-package <name>`.
  No major upgrades without a stated reason.

## What not to touch

- `LICENSE.md` and the keeper-agent-kit attribution in README.md.
- Do not commit `keeper.mcpb`, `*.bundle`, `.venv/`, `.env` or any `config.json`.
- Do not change repo settings, branch protection or secrets.

## How to ship

1. Branch from `main`: `feat/`, `fix/`, `docs/`, `chore/` (or `improve/`).
2. Small Conventional Commits (`scripts/validate-commit-msg.sh` checks the format),
   each with `scripts/check.sh` passing. Signed commits; no AI attribution.
3. Update `CHANGELOG.md` under `[Unreleased]`.
4. Open a PR against `main`; CI runs `scripts/check.sh`.

## Definition of done

`scripts/check.sh` passes locally and in CI, docs match the code, the changelog
is updated, and no secret or real tenant data appears in the diff.
