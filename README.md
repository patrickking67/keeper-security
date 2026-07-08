# keeper-security

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
- Python 3.10+ (3.11+ for the MCP server)
- Linux, macOS, or Windows

## Installation

### Claude Code marketplace

```bash
/plugin marketplace add patrickking67/keeper-security
/plugin install keeper-admin@keeper-security
/plugin install keeper-msp@keeper-security
/plugin install keeper-secrets@keeper-security
/plugin install keeper-setup@keeper-security
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

`manifest.json` + `keeper.mcpb` package the local Commander-backed MCP server
for one-click install in Claude Desktop. Build with `task mcpb` (requires the
`mcpb` CLI). Setup, authentication bootstrap, tool list, and security notes:
[docs/mcp-server.md](docs/mcp-server.md).

## Validation

```bash
task validate        # plugin/marketplace/skill validation (scripts/validate-plugins.sh)
task mcp-check       # import-check the MCP server
```

## Documentation

- [Commander CLI](https://docs.keeper.io/en/keeperpam/commander-cli/overview) - install, shell, admin commands
- [KSM CLI](https://docs.keeper.io/en/keeperpam/secrets-manager/overview) - install, profiles, commands
- [Keeper notation](https://docs.keeper.io/en/keeperpam/secrets-manager/about/keeper-notation) - `keeper://` references
- [MSP management commands](https://docs.keeper.io/keeperpam/commander-cli/command-reference/msp-management-commands)
- [docs/mcp-server.md](docs/mcp-server.md) - the bundled MCP server

## Security

Security issues: see [SECURITY.md](SECURITY.md). Never commit Keeper configs,
one-time tokens, or secret values to this repo; skills and commands are written
to keep secret values out of transcripts by design.

## Contributing

Issues and pull requests welcome - see [CONTRIBUTING.md](CONTRIBUTING.md).
Keep edits focused, run `task validate` before submitting, and describe how you
tested.

## License

Apache-2.0 - see [LICENSE.md](LICENSE.md). Portions derived from
[Keeper-Security/keeper-agent-kit](https://github.com/Keeper-Security/keeper-agent-kit)
(Apache-2.0).
