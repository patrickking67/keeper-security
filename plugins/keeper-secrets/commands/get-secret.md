---
name: get-secret
description: Retrieve ONE named field from one Keeper record by title or UID using the KSM CLI - injected or piped, never printed into the transcript
argument-hint: "<record-title-or-uid> [field]"
---

# Keeper Get Secret

Retrieve a single secret field from one record, safely. This command targets the
*specific* field requested - never the whole record - and never prints the
secret value into the conversation.

## Steps

1. **Resolve the record.** If the argument looks like a UID, use it directly;
   otherwise run `ksm secret list` and match by title. If more than one record
   matches, list the candidates (title + UID) and ask - never guess.
2. **Pick the one field.** Default to the field the task needs (`password`,
   `login`, an `api_key` custom field). Address it with Keeper notation:
   `keeper://<UID>/field/password` or `keeper://<UID>/custom_field/api_key`.
3. **Deliver without echoing.** Route the value directly to its destination -
   never through the transcript:

   ```bash
   # Inject into the consuming process (preferred)
   MYAPP_DB_PASSWORD="keeper://<UID>/field/password" ksm exec -- myapp

   # Or capture into an environment variable in the user's shell
   export DB_PASSWORD="$(ksm secret get keeper://<UID>/field/password)"
   ```

   Do **not** run a bare `ksm secret get ... -f password` whose stdout lands in
   the conversation, a log, or a summary.
4. **Warn on persistence.** If the user asks to paste the value into a shared
   channel, ticket, commit, doc, or log, decline and explain the risk - give
   them the record reference (title + UID + field) instead.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| record-title-or-uid | Yes | The record to read, by title or UID |
| field | No | The single field to retrieve (default `password`) |

## Safety

This command handles secret material. It retrieves only the one requested
field, never displays the value in the transcript, references the record by
title/UID, and treats the retrieval as an audited event.

## Examples

```text
/keeper-secrets:get-secret "Production Postgres" password
/keeper-secrets:get-secret 8f8I-OqPV58o2r91wVgZ_A login
/keeper-secrets:get-secret "Stripe Live API Key" api_key
```
