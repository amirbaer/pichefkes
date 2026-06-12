---
description: Publish a Claude Code plugin, command, or skill to the Remedio AI Hub via the ai-hub MCP
allowed-tools: Read, mcp__ai-hub__add_plugin, mcp__ai-hub__edit_plugin, mcp__ai-hub__add_skill, mcp__ai-hub__edit_skill, mcp__ai-hub__list_plugins, mcp__ai-hub__list_skills, mcp__ai-hub__get_item, mcp__ai-hub__install_plugin, mcp__ai-hub__install_skill, mcp__ai-hub__install_marketplace
---

Publish to the Remedio AI Hub through the **`ai-hub` MCP** — it signs in with your Hub
SSO, so there are no tokens or cookies to manage. A public submission opens a review PR in
`gytpol/ai-hub` (nothing is published until a maintainer merges); inside a space you own as
space-admin, changes publish immediately. Authoring lints + semver are enforced server-side.

If the `ai-hub` tools (namespaced `mcp__ai-hub__*`) aren't available, the plugin isn't
installed — tell the user to run `/plugin marketplace add gytpol/ai-hub@marketplace` then
`/plugin install ai-hub-mcp@remedio` and restart Claude Code. The *first* tool call may open
a browser for SSO login; that's expected (the session caches in `~/.ai-hub-mcp` and refreshes
silently after).

Arguments: $ARGUMENTS

Map the request to a tool:

- **Publish a plugin** (including a slash-command packaged as a one-command plugin) →
  `add_plugin` `{repo:"owner/repo"|URL, ref?, subdir?, name?, description?, tags?, space?}`.
  The plugin must live in a **GitHub repo the hub can read** (public, or a repo the hub's
  GitHub app is installed on) and contain a `.claude-plugin/plugin.json`. The hub validates
  the source against GitHub and pins a commit. **If the plugin is local-only, first push it
  to a hub-readable repo** (as a proper plugin dir / marketplace), then point `add_plugin`
  at it (use `subdir` if it's not at the repo root). To publish an updated version, push the
  change to the source repo and re-run `add_plugin` against the new ref.
- **Author a new skill from inline content** → `add_skill`
  `{name, description (write it as a "Use when…" trigger), body (the SKILL.md markdown, no frontmatter), tags?, space?}`.
- **Edit a skill** (content or metadata) → `edit_skill` `{slug, …only the fields to change}`.
- **Edit a plugin's metadata** → `edit_plugin` `{slug, description?, tags?, version?, space?}`
  (`version` must increase). Rewrites only `plugin.json`; to change a plugin's command/skill
  files, push to the source repo and re-run `add_plugin`.
- **Find / install** → `list_plugins`, `list_skills`, `get_item`, `install_plugin`,
  `install_skill`, `install_marketplace` (the `install_*` tools return the exact `/plugin …`
  commands to paste — add the marketplace first, then install).

Report what the tool returns (slug, scope public/space, pending-review vs published, any
lint warnings, PR url). On failure the hub returns a structured error envelope — relay it
verbatim rather than guessing.
