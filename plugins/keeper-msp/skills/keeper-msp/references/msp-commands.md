# MSP Command Reference

Commands specific to Managed Service Provider (MSP) tenants. Run `help <command>`
in `keeper shell` for authoritative usage; the official reference lives at
[MSP Management Commands](https://docs.keeper.io/keeperpam/commander-cli/command-reference/msp-management-commands).

MSP commands require an MSP-type Keeper account and MSP Admin privileges.

## Command summary

| Command | Alias | Explanation |
| --- | --- | --- |
| `msp-info` | `mi` | Display MSP details: license pools and managed companies |
| `msp-down` | `md` | Refresh local MSP data from server |
| `msp-add` | `ma` | Create a Managed Company |
| `msp-remove` | `mrm` | Remove a Managed Company (destructive) |
| `msp-update` | `mu` | Modify Managed Company licenses, plan, storage, add-ons |
| `msp-billing-report` | | Generate MSP billing reports |
| `msp-legacy-report` | | Generate MSP legacy license report |
| `switch-to-mc` | | Switch context to run commands as a managed company |
| `switch-to-msp` | | Switch context back to the MSP |
| `msp-convert-node` | | Convert an enterprise node into a managed company |
| `msp-copy-role` | | Copy role enforcements from MSP to MCs |
| `distributor` | | Distributor accounts: manage MSPs and their licenses |

## msp-add

```text
msp-add --plan=<business|businessPlus|enterprise|enterprisePlus> --seats=<N> "<MC Name>"
```

- `--plan` / `-p` - MC plan or product
- `--seats` / `-s` - number of seats
- On success, Commander stores the new MC id in the `last_mc_id` environment
  variable for use in follow-up commands.

## msp-update

```text
msp-update "<MC Name or ID>" [--plan <plan>] [--seats <N>] [--file-plan <100gb|1tb|10tb>] \
  [--add-addon <ADDON>] [--remove-addon <ADDON>] [--node <NODE>]
```

Add-on names accepted by `--add-addon` / `--remove-addon`:

- `compliance_report`
- `enterprise_audit_and_reporting`
- `secrets_manager`
- `enterprise_breach_watch`
- `onboarding_and_certificate`
- `msp_service_and_support`
- `connection_manager`
- `chat`
- `password_rotation`
- `remote_browser_isolation`
- `privileged_access_manager`
- `keeper_endpoint_privilege_manager`

## msp-remove

```text
msp-remove <MC ID>
msp-remove "<MC Name>"
```

Destructive - always confirm with the user first.

## msp-billing-report

```text
msp-billing-report --month YYYY-MM [-d|--show-date] [-c|--show-company] \
  [--format {json,csv,table}] [--output <filename>]
```

## switch-to-mc / switch-to-msp

```text
switch-to-mc <MC ID>     # get IDs from msp-info
switch-to-msp            # return to MSP context
```

All commands after `switch-to-mc` run as an administrator of that managed
company. Treat the switch/commands/switch-back sequence as one block.

## msp-convert-node

```text
msp-convert-node <NODE ID or NAME>
```

Remove SSO provisioning from the node before converting.

## msp-copy-role

```text
msp-copy-role "<MC Name>" --role "<ROLE NAME>"
```

## distributor

Available to distributor accounts that manage multiple MSPs:

```text
distributor info [--mc-details] [--reload] [--format {json,csv,table}] [--output <file>]
distributor msp-info <MSP>
distributor license <MSP>
```

- `info` - list all managed MSPs (optionally with their managed companies)
- `msp-info` - information and usage for one MSP
- `license` - view or edit the license options for one MSP
