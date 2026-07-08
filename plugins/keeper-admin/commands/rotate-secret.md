---
name: rotate-secret
description: Rotate a Keeper credential via Commander - propose the rotation, then trigger it only after explicit confirmation. Never prints old or new values
argument-hint: "<record-title-or-uid>"
---

# Keeper Rotate Secret

Rotate a credential safely. This is a **mutating, sensitive** operation: it
changes a live secret on a target system. It requires explicit confirmation
before executing, and it never prints the old or new value.

## Steps

1. **Resolve the record.** Find exactly one record by title or UID
   (`search "<title>"` in the Commander shell). Disambiguate if more than one
   matches - rotating the wrong credential can break production.
2. **Identify the rotation path.** Determine whether this is a KeeperPAM
   rotation (a PAM User record whose rotation settings reference a PAM
   Machine/Database/Directory and a Gateway) or a legacy Commander rotation
   plugin. Confirm a rotation target and gateway exist:

   ```bash
   My Vault> pam rotation list
   My Vault> pam rotation info -r <RECORD_UID>
   ```

3. **Show the plan and the blast radius.** State exactly what will rotate: the
   record (title + UID), the target system, the gateway, and what depends on
   this credential (services, integrations). Do not show the current value.
4. **Confirm, then rotate.** Only after the user explicitly confirms:

   ```bash
   My Vault> pam action rotate -r <RECORD_UID>
   My Vault> pam action job-info <JOB_ID>     # check rotation job status
   ```

   Report success by referencing the record - never by printing the new value.
5. **Verify and note.** Confirm the rotation job finished, remind the user that
   dependent systems may need to re-pull the secret, and note the rotation as
   an audited event. If a change/ticket reference was given, offer to log it.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| record-title-or-uid | Yes | The credential record to rotate, by title or UID |

## Safety

Rotation mutates a live credential. **Always require explicit confirmation
before executing.** Never display the old or new value. Confirm the exact
record, target, and gateway first, and treat the rotation as an audited event.
If the record has no rotation configuration, say so and stop rather than
guessing.

## Examples

```text
/keeper-admin:rotate-secret "Production Postgres"
/keeper-admin:rotate-secret 5NaygwI4LK1BDZmH3Ib
/keeper-admin:rotate-secret "IAM Account: demouser"
```
