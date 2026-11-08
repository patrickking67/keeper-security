# Security

This repository contains **documentation, agent skills, and a local MCP
server** that wrap Keeper's official CLIs - not a standalone crypto
implementation. Mistakes in docs, examples, or server code could still mislead
users or expose secret handling paths; please report problems responsibly.

## Supported versions

| Version | Supported |
| --- | --- |
| `main` (latest commit) | yes |
| older commits and tags | no |

Security fixes land on `main`. Use the latest commit when deploying these skills
or the MCP server.

## Reporting a vulnerability

**Please do not** open a public GitHub issue for undisclosed security
vulnerabilities.

Report privately through GitHub:
<https://github.com/patrickking67/keeper-security/security/advisories/new>

Vulnerabilities in Keeper Commander, KSM CLI, or the Keeper platform itself go
to [Keeper Security Support](https://keepersecurity.com/support), not this repo.

Include:

- A clear description of the issue and its impact
- Steps to reproduce (if applicable)
- Affected files or components (a specific skill, command, or server module)

Never include real secrets, configs or tenant data in a report.

## Response expectations

- Acknowledgement within 7 days.
- An initial assessment and plan within 14 days.
- Fixes ship on `main` and are noted in CHANGELOG.md; credit is given in the
  advisory unless you ask otherwise.

## Scope (in scope for this repo)

- Misleading or unsafe examples in skills or reference docs
- Instructions that could cause secrets to be exposed in logs or chat
- MCP server code paths that could leak secret field values or auth material
- Validation gaps that would let unsafe examples land
- Ways around the server's gating: the `confirm=true` requirement on
  `keeper_transfer_user`, the refused commands in `keeper_run_command`, or
  secret redaction

## Out of scope

- Vulnerabilities in Keeper's products or CLIs (report to Keeper)
- Issues requiring a compromised local machine or Keeper account
