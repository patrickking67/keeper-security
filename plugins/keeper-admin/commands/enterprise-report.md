---
name: enterprise-report
description: Run a Keeper compliance / access report for an audit - who can access what, record-access history, team and shared-folder access. Metadata only
argument-hint: "[--user <email>] [--team <name>] [--node <name>]"
---

# Keeper Enterprise Report

Produce an auditor-ready access report from Commander's compliance surface.
Compliance reports decrypt only record *metadata* (title, type, URL) - never
secret values - and that is exactly what this command works with. Requires the
Compliance Reporting add-on and admin permission.

## Steps

1. **Pick the report and scope.** Choose the report type from the request and
   scope it as narrowly as possible:
   - **Compliance report** (`compliance-report`) - owned records per user
     vault and their sharing relationships; filter by `--username`, `--node`,
     `--team`, `--job-title`, `--url`.
   - **Record-access report** (`compliance record-access-report`) - what a
     user has historically accessed; vault mode shows what they can access now.
   - **Team report** (`compliance team-report [-tu]`) - which teams reach
     which shared folders, with permissions (add `-tu` for team members).
   - **Shared-folder report** (`compliance shared-folder-report`) - all
     entities (teams and users) with access to each shared folder.
2. **Run it** in the Commander shell, using `--format csv --output <file>` for
   auditor delivery. Resolve names first with `enterprise-info --users` /
   `enterprise-info --teams` if needed. First runs build a report cache and can
   be slow on large tenants; scope by user to speed it up.
3. **Read the metadata only.** Reason over titles, UIDs, types, URLs, owners,
   permissions, and timestamps. Never retrieve or display a secret field value.
4. **Summarize for the audit.** Present the access relationships and flag
   notable findings - over-broad shares, access retained by departed users,
   edit/share where read-only suffices. Tie each finding to its source report.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| --user | No | Filter to one user (email) - required for record-access history |
| --team | No | Filter to one team |
| --node | No | Filter to records owned by users in a node |

## Safety

Compliance reports expose access *metadata* only and require administrator
permission to run. This command never retrieves or displays a secret value,
and treats report generation as an audited action.

## Examples

```text
/keeper-admin:enterprise-report --user offboarded.user@company.com
/keeper-admin:enterprise-report --team "Engineering"
/keeper-admin:enterprise-report --node "Finance"
```
