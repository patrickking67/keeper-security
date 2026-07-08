---
name: vault-search
description: Search Keeper vault records by title, type, URL, or folder via Commander - returns matching records by title and UID, never values
argument-hint: "<query> [--type <record-type>]"
---

# Keeper Vault Search

Find the right record across the vault by title, record type, URL, or folder.
Returns the matching records as **metadata** - title, UID, type, folder - so
the user can identify and act on the right one. Never returns secret values.

## Steps

1. **Build the query.** In the Commander shell (tmux pattern from the
   keeper-admin skill):

   ```bash
   My Vault> search "<query>"          # searches titles, logins, URLs, notes
   My Vault> ls -l                     # detailed listing with UIDs in a folder
   My Vault> record-type-report        # if filtering by type is needed
   ```

   For a `--type` filter (e.g. only `pamMachine` or `databaseCredentials`),
   filter the search output by the record-type column.
2. **Run and rank.** Rank matches by exactness of title match, then folder
   relevance. Review the full result set before concluding - never
   characterize the vault from a truncated listing.
3. **Present metadata.** For each match show title, UID, record type, and
   folder. Do not run `get <UID>` with masked fields revealed, and do not
   expand any field value.
4. **Hand off.** If the user wants a value from a match, route to
   `/keeper-secrets:get-secret` with the chosen UID; if they want to rotate
   it, route to `/keeper-admin:rotate-secret`.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| query | Yes | Search term matched against record title, URL, and notes |
| --type | No | Restrict to a record type (e.g. `login`, `pamMachine`, `databaseCredentials`) |

## Safety

Search returns record metadata only. It never retrieves or displays a secret
value. Records are referenced by title and UID.

## Examples

```text
/keeper-admin:vault-search postgres
/keeper-admin:vault-search "AWS" --type login
/keeper-admin:vault-search bastion --type pamMachine
```
