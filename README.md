# Keeper

A unified Claude plugin for [Keeper Security](https://www.keepersecurity.com). Bundles the three Keeper CLI skills (`keeper-secrets`, `keeper-admin`, `keeper-setup`) and wires up the official Keeper documentation MCP server so Claude can answer questions straight from `docs.keeper.io`.

Works in both **Claude Code** and **Claude Cowork**.

## What's inside

| Component | Type | Purpose |
|-----------|------|---------|
| `keeper-secrets` | Skill | Retrieve and inject secrets from Keeper Vault via the KSM CLI (`ksm`). Use for application credentials, CI/CD injection, `keeper://` notation. |
| `keeper-admin` | Skill | Enterprise administration, PAM, and privileged access via Keeper Commander (`keeper`). User/team/role management, SSO, password rotation, KSM applications. |
| `keeper-setup` | Skill | Install and configure the Keeper CLI tools (KSM CLI and Commander). Authentication, profile setup, persistent login. |
| `keeper-docs` | MCP server | Live HTTP MCP for `docs.keeper.io`. Lets Claude search the official Keeper docs. |

## Installation

### Claude Code

```bash
# From the plugins folder
git clone https://github.com/patrickking67/keeper-plugin ~/.claude/plugins/keeper
```

Or symlink an existing clone:

```bash
ln -s ~/Development/keeper-plugin ~/.claude/plugins/keeper
```

Restart Claude Code. Verify the docs MCP with `/mcp`.

### Claude Cowork

Drop the packaged `keeper.plugin` file into Cowork — it'll appear as a rich preview with an install button. To rebuild the package:

```bash
cd ~/Development/keeper-plugin
zip -r /tmp/keeper.plugin . -x "*.DS_Store" -x ".git/*"
```

## Usage

Once installed, the three skills auto-trigger based on what you ask:

| Ask Claude... | Triggers |
|---------------|----------|
| "Install the Keeper CLI" / "set up `ksm`" | `keeper-setup` |
| "Get the prod DB password from Keeper" / "run my app with secrets injected" | `keeper-secrets` |
| "Create a KSM application" / "add a user to the SSO team" / "rotate this credential" | `keeper-admin` |
| Any question about Keeper features, configuration, or APIs | `keeper-docs` MCP |

You can also invoke skills directly:

- `/keeper:keeper-secrets`
- `/keeper:keeper-admin`
- `/keeper:keeper-setup`

## Prerequisites

The skills shell out to two Keeper CLI tools. If they're not installed yet, ask Claude to "install Keeper CLI" and `keeper-setup` will walk through it.

- **KSM CLI** (`ksm`) — `pip install keeper-secrets-manager-cli`
- **Commander** (`keeper`) — `pip install keepercommander`

Authentication is per-tool (KSM uses one-time tokens; Commander uses interactive login or persistent device approval). The `keeper-setup` skill covers both.

## MCP server

The `keeper-docs` MCP server is hosted by Keeper at `https://docs.keeper.io/en/~gitbook/mcp`. No authentication required — it serves the public documentation. Tools become available as `mcp__plugin_keeper_keeper-docs__*`.

## Repository layout

```
keeper-plugin/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── skills/
│   ├── keeper-admin/
│   ├── keeper-secrets/
│   └── keeper-setup/
├── LICENSE
└── README.md
```

## License

MIT. See [LICENSE](LICENSE).

The bundled skills originate from the `keeper-security` plugin family and are redistributed here under the same terms.
