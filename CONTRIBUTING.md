# Contributing to keeper-plugin

Thanks for your interest in improving the plugin. This document covers what kinds of contributions are welcome, how to develop locally, and how PRs are reviewed.

## What kinds of changes are welcome

- **Skill prompt improvements** — better trigger phrases, clearer examples, more accurate command references, fixed broken doc links
- **Reference content** — adding worked examples, clarifying confusing sections in the `references/` files
- **MCP configuration** — adding additional Keeper-hosted MCP endpoints if/when Keeper publishes them
- **Documentation** — README clarifications, install instructions for additional platforms
- **Bug reports and fixes** — typos, incorrect command syntax, broken cross-references

## What's out of scope

- Redistributing Keeper's binaries (KSM CLI, Commander) — installation is up to the user via pip / official channels
- Changes that encourage logging or persisting secrets to disk in plaintext beyond explicit user instruction
- Skills that duplicate functionality already covered by the existing three skills — extend, don't fork

## Development setup

```bash
git clone https://github.com/patrickking67/keeper-plugin
cd keeper-plugin
# Symlink into your plugins folder for live testing
ln -s "$PWD" ~/.claude/plugins/keeper
```

Restart Claude Code. Use `/mcp` to confirm the `keeper-docs` server is connected. Trigger each skill by phrasing a request that matches its description, then refine.

For Cowork testing, rebuild the `.plugin` archive:

```bash
zip -r /tmp/keeper.plugin . -x "*.DS_Store" -x ".git/*"
```

Drop the resulting file into a Cowork chat.

## Style and conventions

**Skill prompts** are instructions for Claude, not user-facing prose. Use the imperative voice ("Run `ksm list`...", not "You can run `ksm list`...").

**Markdown** follows the conventions already in the repo: ATX-style headers, fenced code blocks with language tags, sentence-case section titles.

**Commits** should be small, focused, and have a descriptive subject line in the imperative mood ("Add MSP onboarding example to keeper-admin", not "Added stuff"). Do not include attribution to AI tools or bots in commit messages — see the repository's authoring rules.

**Author identity** on commits and PRs must be a real person. Bot/AI co-author trailers are not accepted.

## Pull request checklist

- [ ] One logical change per PR
- [ ] Commit subjects are imperative and descriptive
- [ ] If you changed a skill's frontmatter `description`, the new trigger phrases are tested by asking Claude something that should match
- [ ] If you added a reference file, it's linked from the parent SKILL.md
- [ ] No secrets, tokens, or real vault data anywhere in the diff

## Review

Maintainer aims to respond within a week. PRs that touch skill behavior may be tested locally before merge. Small documentation fixes typically merge quickly.

## Security

Security reports go privately to the email in [SECURITY.md](SECURITY.md). Do **not** open a public issue for vulnerabilities.
