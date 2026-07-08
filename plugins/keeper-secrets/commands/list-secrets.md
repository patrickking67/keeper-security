---
name: list-secrets
description: List the records the KSM Application can see - title, UID, and type. Metadata only, never secret values
argument-hint: "[--folder <folder-uid>] [--profile <name>]"
---

# Keeper List Secrets

Enumerate the records available to the configured KSM Application so the user
can pick the right one - by title, UID, and record type. This command returns
**metadata only**; it never retrieves or displays any secret field value.

## Steps

1. **Determine scope.** Default to the active KSM profile; honor `--profile`
   and `--folder-uid` if given:

   ```bash
   ksm secret list
   ksm secret list --json
   ksm secret list --folder-uid <FOLDER_UID>
   ksm secret list --profile production
   ```

2. **List metadata.** Report UID, record type, and title for each record. Stop
   there - do not run `ksm secret get` or expand any field.
3. **Summarize.** Group by record type (login, databaseCredentials, sshKeys,
   pamUser, etc.) so the user can see what kinds of secrets are in scope.
4. **Point to the next step.** If the user wants a specific value, hand off to
   `/keeper-secrets:get-secret` with the chosen title/UID rather than fetching
   it here.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| --folder | No | Folder UID to scope the listing |
| --profile | No | KSM profile to use (default profile otherwise) |

## Safety

This command lists records, not their contents. It never retrieves or prints a
secret value. Records are identified by title and UID only.

## Examples

```text
/keeper-secrets:list-secrets
/keeper-secrets:list-secrets --folder Vv9KrxxdKKJnp5EWa0OFXw
/keeper-secrets:list-secrets --profile production
```
