## What changed

## Why

## How it was verified

- [ ] `scripts/check.sh` passes
- [ ] Manual check (describe; use a test tenant, never production data):

## Safety

- [ ] No secrets, tokens, tenant IDs or real configs in the diff
- [ ] Write and destructive gating, refused commands and redaction are unchanged or stricter
- [ ] Claude and Cursor manifests stay in sync (if plugins changed)
- [ ] CHANGELOG.md updated under `[Unreleased]`

## Not verified
