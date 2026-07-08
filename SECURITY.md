# Security

This repository contains **documentation, agent skills, and a local MCP
server** that wrap Keeper's official CLIs - not a standalone crypto
implementation. Mistakes in docs, examples, or server code could still mislead
users or expose secret handling paths; please report problems responsibly.

## Supported versions

Security fixes are applied to the default branch (`main`). Use the latest
commit or tagged release when deploying these skills or the MCP server.

## Reporting a vulnerability

**Please do not** open a public GitHub issue for undisclosed security
vulnerabilities.

Instead:

1. **Email:** patrick.king@barkrowsystems.com for issues specific to this
   repository (skill content, validation, the MCP server).
2. **Keeper products:** vulnerabilities in Keeper Commander, KSM CLI, or the
   Keeper platform itself should go to
   [Keeper Security Support](https://keepersecurity.com/support) - not this repo.

Include:

- A clear description of the issue and its impact
- Steps to reproduce (if applicable)
- Affected files or components (a specific skill, command, or server module)

## Scope (in scope for this repo)

- Misleading or unsafe examples in skills or reference docs
- Instructions that could cause secrets to be exposed in logs or chat
- MCP server code paths that could leak secret field values or auth material
- Validation gaps that would let unsafe examples land

## Out of scope

- Vulnerabilities in Keeper's products or CLIs (report to Keeper)
- Issues requiring a compromised local machine or Keeper account
