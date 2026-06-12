---
description: Publish a Claude Code plugin, command, or skill to the Remedio AI Hub by name (via the ai-hub MCP)
allowed-tools: Read, Bash(git:*), Bash(ls:*), Bash(find:*), mcp__plugin_ai-hub-mcp_ai-hub__add_plugin, mcp__plugin_ai-hub-mcp_ai-hub__add_skill, mcp__plugin_ai-hub-mcp_ai-hub__edit_plugin, mcp__plugin_ai-hub-mcp_ai-hub__edit_skill, mcp__plugin_ai-hub-mcp_ai-hub__list_plugins, mcp__plugin_ai-hub-mcp_ai-hub__list_skills, mcp__plugin_ai-hub-mcp_ai-hub__get_item, mcp__plugin_ai-hub-mcp_ai-hub__install_plugin, mcp__plugin_ai-hub-mcp_ai-hub__install_skill, mcp__plugin_ai-hub-mcp_ai-hub__install_marketplace
---

Publish a plugin/command/skill to the Remedio AI Hub through the **`ai-hub` MCP** (SSO — no
cookie). **You give a name; this command does the rest** — finds the local source, derives the
GitHub coordinates from git, and calls the right MCP tool. You never write JSON. A public
submission opens a review PR in `gytpol/ai-hub`; in a space you own as space-admin it
publishes immediately. Lints + semver are enforced server-side.

Arguments: $ARGUMENTS — a plugin/skill **name** (e.g. `speak`), optionally followed by
`--tags a,b`, `--space NAME`, or an explicit path to the source dir.

### Steps

1. **Find the source for the name.** Take the first argument as the name; locate its local dir:
   - **Plugin** — a directory named `<name>` (or whose `.claude-plugin/plugin.json` has
     `"name": "<name>"`) that contains `.claude-plugin/plugin.json`.
   - **Skill** — a `<name>/SKILL.md` (or `skills/<name>/SKILL.md`).
   Search the user's plugin repo first — on this machine that's `~/Home/code/pichefkes/claude/`
   (sibling dirs like `claude/speak/`, `claude/hub-submit/`) — then `$PWD`. If an explicit path
   was given, use it. If nothing matches, or more than one does, list what you found and ask.

2. **Derive the GitHub coordinates from git** (this is what replaces hand-written JSON):
   - `repo` = `owner/repo` parsed from `git -C <dir> remote get-url origin`.
   - `ref`  = `git -C <dir> rev-parse --abbrev-ref HEAD` (current branch).
   - `subdir` = `<dir>` relative to `git -C <dir> rev-parse --show-toplevel` (omit if at repo root).
   Then confirm the hub will be able to fetch it: the working tree under `<dir>` is clean and
   `<ref>` is pushed (`git -C <dir> status --porcelain -- <dir>` is empty AND local `<ref>` ==
   `origin/<ref>`). If not, tell the user to commit/push first — the hub pins the commit it reads
   from GitHub, so unpushed changes are invisible to it. The repo must be **public or a
   gytpol-org repo** (the hub's PAT can't read personal *private* repos).

3. **Call the MCP tool** (no JSON from the user — you build the args):
   - Has `.claude-plugin/plugin.json` → `add_plugin` with `{repo, ref, subdir}` (also handles
     skill-only repos). Tags: from `--tags`, else the manifest's `keywords`.
   - Skill defined only by a local `SKILL.md` (not in a hub-readable repo) → `add_skill` with
     `{name, description, body}` where `body` is the SKILL.md minus its frontmatter.
   - Metadata-only change to something already in the hub (description / tags / version bump) →
     `edit_plugin` / `edit_skill` with `{slug, …}`.
   Pass `--space` through if given.

4. **Report** exactly what the tool returns: slug, scope (public/space), pending-review vs
   published, any lint warnings, and the PR url. If the hub says the **slug already exists**
   (e.g. an earlier authored-in-hub entry), surface that and ask whether to `edit_*` it, bump
   the version, or use a new slug — never silently duplicate. The *first* MCP call may open a
   browser for SSO; that's expected (session caches in `~/.ai-hub-mcp`).

If the `mcp__plugin_ai-hub-mcp_ai-hub__*` tools aren't available, the `ai-hub-mcp` plugin isn't
loaded — have the user run `/plugin install ai-hub-mcp@remedio` then `/reload-plugins` (or restart).
