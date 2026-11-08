# keeper-security

[![CI](https://github.com/patrickking67/keeper-security/actions/workflows/ci.yml/badge.svg)](https://github.com/patrickking67/keeper-security/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE.md)

Everything needed to give AI agents safe, first-class access to Keeper Security,
in one repo:

- **Plugin marketplace ("Keeper Security")** for Claude Code and Cursor, with
  four plugins - skills, slash commands, agents, and a bundled Keeper Docs MCP
  server in each.
- **Local MCP server + MCPB bundle** (`keeper-mcp`) that wraps the Keeper
  Commander CLI for MCP clients such as Claude Desktop - see
  [docs/mcp-server.md](docs/mcp-server.md).
- **Codex / Copilot / any-agent skills** via the standard `skills/` layout
  (installable with the Vercel Skills CLI).

Plugin and skill content is derived from Keeper Security's Apache-2.0
[keeper-agent-kit](https://github.com/Keeper-Security/keeper-agent-kit) and
extended here (keeper-msp plugin, commands, agents, extra skills, Keeper Docs
MCP wiring).

## What you get

| Plugin | Use it for | CLI |
| --- | --- | --- |
| keeper-admin | Vault ops, enterprise admin, PAM sessions, rotation, compliance reports | `keeper` |
| keeper-msp | Managed companies, licenses/add-ons, MSP billing, switch-to-mc, distributor | `keeper` |
| keeper-secrets | App secrets, `ksm exec`, templates, CI/CD, Keeper notation | `ksm` |
| keeper-setup | Install CLIs, profiles, first-time setup | both |

Every plugin also bundles the **keeper-docs** MCP server
(`https://docs.keeper.io/~gitbook/mcp`), so the agent can search official Keeper
documentation live instead of guessing command syntax.

Skills per plugin:

- **keeper-admin**: keeper-admin, enterprise-admin, keeper-pam, vault-records; agents pam-session-broker and secrets-access-auditor; commands `/keeper-admin:vault-search`, `/keeper-admin:rotate-secret`, `/keeper-admin:enterprise-report`
- **keeper-msp**: keeper-msp; command `/keeper-msp:msp-status`
- **keeper-secrets**: keeper-secrets, keeper-notation; commands `/keeper-secrets:get-secret`, `/keeper-secrets:list-secrets`
- **keeper-setup**: keeper-setup

## Prerequisites

- A Keeper Security account (MSP plugins need an MSP admin account)
- KSM CLI (`ksm`) for keeper-secrets; Commander CLI (`keeper`) for
  keeper-admin / keeper-msp - the keeper-setup skill walks through installation
- Python 3.10+ for the CLIs; 3.11 to 3.14 for the MCP server ([uv](https://docs.astral.sh/uv/) installs 3.13 for you)
- Linux, macOS, or Windows

## Installation

### Claude Code marketplace

```bash
/plugin marketplace add patrickking67/keeper-security
/plugin install keeper-admin@Keeper-Security
/plugin install keeper-msp@Keeper-Security
/plugin install keeper-secrets@Keeper-Security
/plugin install keeper-setup@Keeper-Security
```

### Any agent via Vercel Skills CLI (Claude Code, Cursor, Codex, Copilot)

```bash
npx skills add patrickking67/keeper-security          # interactive
npx skills add patrickking67/keeper-security -a codex # target a specific agent
npx skills add patrickking67/keeper-security -g       # global install
```

### Manual installation

```bash
git clone https://github.com/patrickking67/keeper-security
cd keeper-security
mkdir -p ~/.claude/skills
cp -r plugins/*/skills/* ~/.claude/skills/
```

| Agent | Typical skills path |
| --- | --- |
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |
| Codex | `~/.codex/skills/` |
| GitHub Copilot | `~/.github/skills/` |

### MCP server (MCPB bundle)

`manifest.json` describes the MCPB bundle that packages the local
Commander-backed MCP server for one-click install in Claude Desktop. Build
`keeper.mcpb` with `task mcpb` (requires the `mcpb` CLI); the built file is
gitignored, not committed. Setup, authentication bootstrap, tool list, and security notes:
[docs/mcp-server.md](docs/mcp-server.md).

## Architecture

- `src/keeper_mcp/server.py` defines 26 FastMCP tools. Each builds a Commander
  command line with `shlex.quote` on user input and calls `commander.py`.
- `src/keeper_mcp/commander.py` runs `keeper --config=<file> "<command>"` (or a
  `--batch-mode -` chain for managed companies) as a captured subprocess, so
  Commander never touches the MCP stdio stream. It rejects multi-line input,
  parses JSON out of noisy output, and redacts secret fields.
- Read tools carry `readOnlyHint`; `keeper_transfer_user` needs `confirm=true`;
  `keeper_run_command` refuses `shell`, `login`, `connect` and `logout`.
- Plugins are plain Markdown skills, commands and agents plus manifests for
  Claude Code (`.claude-plugin/`) and Cursor (`.cursor-plugin/`).

## Development and tests

```bash
uv sync              # Python 3.13 (.python-version), runtime and dev deps
scripts/check.sh     # ruff, offline pytest suite, plugin and manifest validation
```

The test suite never runs Commander or contacts a Keeper tenant. CI runs
`scripts/check.sh` on every push to `main` and every pull request. See
[AGENTS.md](AGENTS.md) for every command and the safety rules.

## Documentation

- [Commander CLI](https://docs.keeper.io/en/keeperpam/commander-cli/overview) - install, shell, admin commands
- [KSM CLI](https://docs.keeper.io/en/keeperpam/secrets-manager/overview) - install, profiles, commands
- [Keeper notation](https://docs.keeper.io/en/keeperpam/secrets-manager/about/keeper-notation) - `keeper://` references
- [MSP management commands](https://docs.keeper.io/keeperpam/commander-cli/command-reference/msp-management-commands)
- [docs/mcp-server.md](docs/mcp-server.md) - the bundled MCP server
- [CHANGELOG.md](CHANGELOG.md) - release notes

## Security

Security issues: see [SECURITY.md](SECURITY.md). Never commit Keeper configs,
one-time tokens, or secret values to this repo; skills and commands are written
to keep secret values out of transcripts by design.

## Contributing

Issues and pull requests welcome - see [CONTRIBUTING.md](CONTRIBUTING.md).
Keep edits focused, run `scripts/check.sh` before submitting, and describe how
you tested.

## License

Apache-2.0 - see [LICENSE.md](LICENSE.md). Portions derived from
[Keeper-Security/keeper-agent-kit](https://github.com/Keeper-Security/keeper-agent-kit)
(Apache-2.0).
