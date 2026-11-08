@AGENTS.md

## Claude Code notes

- Validate plugin and marketplace manifests with
  `claude plugin validate --strict <path>` (`scripts/check.sh` does this for `.`
  and every `plugins/*/`). The `privacyPolicyUrl` notice it prints is a plugin
  directory submission warning, not a schema error.
- Install the marketplace locally with `/plugin marketplace add ./` from the repo
  root to try skills and commands.
- Use the `keeper-docs` MCP server (`searchDocumentation`, `getPage`) to check
  Commander and KSM syntax before editing a skill.
- No AI attribution in commits, PRs, files or metadata.
