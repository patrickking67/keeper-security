# Contributing

Thanks for your interest in improving the Keeper Security agent marketplace and
MCP server.

## How to Contribute

### Reporting issues

1. Check existing GitHub issues first.
2. Open a new issue with a clear title, what you expected, what happened, and
   the affected plugin/skill/file.

### Making changes

1. Fork and branch from `main`.
2. Keep edits focused - one plugin or concern per PR.
3. Follow the existing conventions:
   - SKILL.md frontmatter is single-line `name:` and `description:`.
   - Commands/agents never print secret values into transcripts.
   - Fenced code blocks always declare a language.
   - Command syntax must be verified against the official Keeper docs
     (each plugin bundles the keeper-docs MCP server for exactly this).
4. Commit messages follow Conventional Commits
   (`scripts/validate-commit-msg.sh` enforces this as a commit-msg hook).

## Testing Guidelines

- Run `task validate` (or `./scripts/validate-plugins.sh`) - it must pass with
  zero errors.
- For MCP server changes, run `task mcp-check` and exercise a JSON-RPC
  handshake against `.venv/bin/keeper-mcp`.
- Never test with real production secrets; use a trial/test Keeper tenant.

## Submission Checklist

- [ ] `task validate` passes
- [ ] New/changed commands verified against official Keeper documentation
- [ ] No secret values, tokens, or real configs in examples or fixtures
- [ ] Plugin manifests (`.claude-plugin/` and `.cursor-plugin/`) stay in sync
- [ ] README/skill docs updated if behavior or structure changed
- [ ] PR describes what changed, why, and how it was tested
