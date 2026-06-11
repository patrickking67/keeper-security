# keeper-mcp

Local MCP server (stdio) named **keeper** that exposes the Keeper Security vault and
MSP/enterprise admin console to MCP clients. It is a thin,
non-interactive wrapper around the [Keeper Commander CLI](https://docs.keeper.io/en/keeperpam/commander-cli/overview):
every tool spawns `keeper --config=<file> "<command>"` (or a `--batch-mode -` chain for
managed-company scoping) and returns the captured output, preferring `--format=json`
wherever Commander supports it.

Built for an MSP admin account: vault search/records, enterprise users/teams,
lock/unlock, MSP managed companies, security audit and ARAM event reporting, cloud-SSO
device approvals, plus a generic command escape hatch.

## How it works

- Commander runs as a subprocess per tool call with a **persistent-login config file**
  (no prompts, no master password on the CLI). The child process never inherits the
  server's stdin/stdout, so the MCP protocol stream stays clean.
- Each call is a fresh Commander process, which performs login resume plus a vault sync.
  On large MSP vaults a call can take several seconds - that is the accepted v1
  tradeoff. (The official `keepersdk` Python SDK is the eventual in-process migration
  target.)
- Tools that accept `mc_id` chain `switch-to-mc <id>` -> command -> `switch-to-msp`
  through batch mode, so managed-company context never leaks between calls.
- Secret redaction: record output masks `password`, `secret`, `pinCode`, `oneTimeCode`,
  `keyPair`, hidden/secured note and `passkey` field values (and password-like keys)
  unless `keeper_get_record` is called with `reveal_secrets=true`.
- Refused outright: `shell`, `login`, `connect` (interactive) and `logout` (it
  permanently kills the persistent-login session).

## Requirements

- Python 3.11+ ([uv](https://docs.astral.sh/uv/) recommended; it will provision one)
- Keeper Commander 17.3+ - installed automatically into this project's virtualenv as
  the `keepercommander` dependency; the venv's `keeper` binary is auto-detected.
  Override with `KEEPER_COMMANDER_BIN` to use a different install.
- A Keeper account with the right privileges:
  - MSP tools need an MSP admin with the "Manage Companies (MSP)" permission.
  - `keeper_audit_report` needs the ARAM add-on; `compliance ...` commands (via
    `keeper_run_command`) need the Compliance Reporting add-on.

## Install

With uv:

```bash
cd /Users/patrickking/Code/MCP/keeper-mcp
uv sync
```

Without uv:

```bash
cd /Users/patrickking/Code/MCP/keeper-mcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Authentication bootstrap (one-time, interactive)

Commander stores credentials in the OS keychain by default; this server needs the
**file-based persistent-login config** instead so it can run headlessly.

```bash
# 1. Confirm Commander is available (the project venv has it: .venv/bin/keeper)
keeper version

# 2. One-time interactive bootstrap (file-based storage mode)
keeper shell --config-file
Not logged in> server US               # only if not US data center: US|EU|AU|CA|JP|GOV
Not logged in> login you@yourmsp.com   # complete device approval + MFA (see below)

# 3. Enable persistent login on this device (30 days max)
My Vault> this-device register
My Vault> this-device persistent-login on
My Vault> this-device ip-auto-approve on
My Vault> this-device timeout 30d
My Vault> this-device 2fa_expiration forever   # only if 2FA is on the account
My Vault> quit                                  # MUST be quit - 'logout' invalidates the session
```

Device approval on first login, when prompted in the shell: `email_send` then
`email_code=<code>`; or `keeper_push` then `approval_check`; or `2fa_send` /
`2fa_code=<code>`.

This writes `~/.keeper/config.json` (macOS/Linux). **pip installs write the config to
the current working directory where `keeper` was started** - start the shell from `~`
or pass `--config ~/.keeper/config.json` explicitly. The resulting file looks like:

```json
{
  "private_key": "...", "device_token": "...", "clone_code": "...",
  "user": "you@yourmsp.com", "server": "keepersecurity.com"
}
```

Protect it - it contains the device private key and clone code:

```bash
chmod 600 ~/.keeper/config.json
```

Verify non-interactive auth works before registering the MCP server:

```bash
keeper --config=$HOME/.keeper/config.json "whoami"
# expect: "Successfully authenticated with Persistent Login"
```

### Caveats you must know

- **Never run `logout`** - it permanently invalidates persistent login and you must
  re-bootstrap. The MCP server refuses to run it; exit interactive shells with `quit`.
- **One device per config.json.** Logging in with the same config from a second machine
  revokes both sessions. If you move the config to another host, delete the local copy.
- **Timeout max is 30 days** (`this-device timeout 30d`), also bounded by the role's
  "Enterprise Logout Timeout". Expect to re-run the bootstrap when it expires - the
  server's error message tells you when authentication fails (Commander exit code 2).
- **SSO admins:** persistent login works, but a fully expired session needs an
  interactive re-login. For headless reliability, enable the role policy "Allow users
  who login with SSO to create a Master Password", set a Master Password in Vault
  Settings -> General, and add `"sso_master_password": true` to the config.
- **Hardening:** Keeper recommends a dedicated low-privilege service-user account with
  an IP-restricted role enforcement for automation configs.

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `KEEPER_CONFIG_FILE` | `~/.keeper/config.json` | Persistent-login config file Commander authenticates with. |
| `KEEPER_COMMANDER_BIN` | `keeper` (venv copy auto-detected) | Path/name of the Keeper Commander executable. |
| `KEEPER_COMMAND_TIMEOUT` | `120` | Per-command timeout in seconds. |

No variable is validated at startup; problems surface as clear tool errors on first use.
The server never loads `.env` files - pass variables through the MCP client config.

## Register with the claude CLI

With uv:

```bash
claude mcp add keeper -- uv run --directory /Users/patrickking/Code/MCP/keeper-mcp keeper-mcp
```

Plain pip/python alternative (after the venv install above):

```bash
claude mcp add keeper -- /Users/patrickking/Code/MCP/keeper-mcp/.venv/bin/keeper-mcp
```

To point at a non-default config file, add `-e` flags before `--`:

```bash
claude mcp add keeper -e KEEPER_CONFIG_FILE=$HOME/.keeper/config.json -- uv run --directory /Users/patrickking/Code/MCP/keeper-mcp keeper-mcp
```

## Tools

| Tool | Read-only | Description |
| --- | --- | --- |
| `keeper_search_records(query)` | yes | Search vault records; returns metadata JSON, never passwords. |
| `keeper_get_record(uid, reveal_secrets=false)` | yes | Fetch one record as JSON; secret fields masked unless `reveal_secrets=true` (returns live credentials - explicit user request only). |
| `keeper_list_folders()` | yes | Vault folder tree (`tree`) plus shared folders and permissions (`list-sf`). |
| `keeper_enterprise_info(verbose, mc_id)` | yes | Enterprise/tenant overview (`enterprise-info`). |
| `keeper_list_users(mc_id)` | yes | Enterprise users as JSON (`enterprise-info --users`). |
| `keeper_lock_user(email, mc_id)` | no | Lock a user account (reversible). |
| `keeper_unlock_user(email, mc_id)` | no | Unlock a user account. |
| `keeper_list_teams(mc_id)` | yes | Enterprise teams as JSON (`enterprise-info --teams`). |
| `keeper_security_audit(node, mc_id)` | yes | Per-user password-health summary (`security-audit-report`). |
| `keeper_audit_report(report_type, created, limit, event_type, username, record_uid, mc_id)` | yes | ARAM event-log reporting (`audit-report`). |
| `keeper_msp_info()` | yes | MSP plans/licenses + managed-company table (`msp-info`, table text). |
| `keeper_list_managed_companies()` | yes | Managed companies with their IDs (`msp-info` table); the ID column feeds `mc_id`. |
| `keeper_device_approve(action, device, mc_id)` | list only | List/approve/deny pending cloud-SSO device approval requests. |
| `keeper_run_command(command, mc_id)` | no | Escape hatch for the full Commander command set; destructive commands run as given; interactive commands and `logout` refused. |

`mc_id` on a tool means it can run inside a managed company: the server wraps the
command in `switch-to-mc <id>` / `switch-to-msp` automatically.

## Security notes

- Secrets are masked by default everywhere; `reveal_secrets=true` is the only way to
  get plaintext credentials, and the tool description warns the model accordingly.
- When creating records through `keeper_run_command`, use `password=$GEN` so Commander
  generates a policy-compliant password instead of putting plaintext in tool arguments.
- The server never runs `logout`, `shell`, `login`, or `connect`.
- Keep `~/.keeper/config.json` at mode 600; it is equivalent to a logged-in device.
- Commander invocations are serialized inside the server: concurrent processes would
  race on the config file, which Commander rewrites with rotated session tokens.

## Troubleshooting

- "Keeper Commander config not found": run the bootstrap above, or set
  `KEEPER_CONFIG_FILE` to where the config actually lives.
- "exit 2: authentication error": the persistent-login session expired (30-day max) or
  was revoked (for example by logging in with the same config elsewhere). Re-run the
  bootstrap.
- Commander binary not found: `uv sync` (or `pip install -e .`) installs
  `keepercommander` into the venv; otherwise set `KEEPER_COMMANDER_BIN`.
- Slow tools: every call logs in and syncs the vault. Raise `KEEPER_COMMAND_TIMEOUT`
  for big reports; consider adding `"skip_records": true` to the config for huge vaults
  if you only use enterprise/MSP tools.
- Unknown command syntax: `keeper_run_command("help <command>")` prints the usage.
