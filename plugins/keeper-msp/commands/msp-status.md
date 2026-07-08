---
name: msp-status
description: Show the Keeper MSP tenant status - license pools, managed companies with allocation and active counts, and optional billing for a month. Read-only
argument-hint: "[--month YYYY-MM]"
---

# Keeper MSP Status

Produce a current status picture of the MSP tenant: license pools, every
managed company with its plan / allocated / active seats, and (optionally) the
billing breakdown for a month. Read-only - this command changes nothing.

## Steps

1. **Refresh and read.** In the Commander shell run `msp-down` then `msp-info`
   to get current license pools and the managed-company table (IDs, plan,
   allocated, active).
2. **Billing (optional).** If a `--month` was given, run
   `msp-billing-report --month <YYYY-MM> --show-company` and fold the results
   into the summary.
3. **Summarize.** Report license pools (available vs total per plan), the MC
   table, and call out anything notable: MCs with 0 active users, pools close
   to exhaustion, allocation far above active usage.
4. **Hand off.** If the user wants to change seats/plans/add-ons, point them at
   `msp-update` (keeper-msp skill) and confirm before any change.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| --month | No | Include an MSP billing report breakdown for the given month (YYYY-MM) |

## Safety

Read-only reporting over MSP license and billing metadata. No vault records are
opened and no secret values are touched. Do not run any `msp-update`,
`msp-add`, or `msp-remove` from this command.

## Examples

```text
/keeper-msp:msp-status
/keeper-msp:msp-status --month 2026-06
```
