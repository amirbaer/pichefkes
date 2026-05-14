---
name: babysit-pr
description: Monitor the current branch's open PR for merge conflicts, failing checks, and unresolved bot comments (e.g. cursorbot), then fix the issues, push, and resolve the comments. Use with `/loop` for continuous monitoring.
argument-hint: [pr-number] [--loop [N]] [--jira [PROJECT_KEY]]
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Agent, mcp__claude_ai_Atlassian__getAccessibleAtlassianResources, mcp__claude_ai_Atlassian__getVisibleJiraProjects, mcp__claude_ai_Atlassian__createJiraIssue, mcp__claude_ai_Atlassian__getJiraIssue
---

# Babysit PR — Fix Failing Checks & Resolve Bot Comments

Monitor an open pull request for failing CI checks and unresolved bot review comments, fix the underlying issues, commit the fixes, push, and resolve the comments.

## Arguments

- PR number (optional) — Pass as a bare number (e.g., `/babysit-pr 123`). If omitted, detect from the current branch using `gh pr view --json number -q .number`.
- `--loop [N]` (optional) — Maximum fix cycles before stopping. If N is omitted or `--loop` is not specified, defaults to 5. E.g., `/babysit-pr --loop 3` or `/babysit-pr 123 --loop`.
- `--jira [PROJECT_KEY]` (optional) — Create a Jira ticket for the PR, prefix the PR title with the ticket key, then close and re-open the PR (to retrigger workflows that depend on the title). Runs once at the start. If `PROJECT_KEY` is omitted, ask the user which project to use. Skipped entirely when the flag is not passed. E.g., `/babysit-pr --jira PROJ` or `/babysit-pr 123 --jira`.

## Steps

**IMPORTANT: Always execute steps 3–6 fully on every iteration. Do NOT shortcut by checking thread counts or combining queries to skip steps. The REST API queries in step 6 are the only reliable way to detect bot comments — GraphQL review thread counts will miss them.**

### 1. Identify the PR

```bash
# If $0 is provided, use it. Otherwise detect from current branch:
gh pr view --json number,url,headRefName,state -q '.'
```

Confirm the PR is open. If not, stop and report.

### 2. Create Jira ticket and prefix PR title (only if `--jira` was passed)

Skip this entire step if `--jira` was not passed. This step runs only once, on the first iteration — do not re-run it on loop iterations.

1. Check whether the PR title already starts with a Jira-style key (e.g. `ABC-123:` or `ABC-123 -`). If it does, skip this step entirely and proceed to step 3.

2. Determine the project key:
   - If `--jira PROJECT_KEY` was passed, use that key.
   - Otherwise, try to deduce it from repo context (in this order, stop at first hit):
     1. Recent PR titles — `gh pr list --state all --limit 30 --json title -q '.[].title'` and grep for a `[A-Z]{2,10}-\d+` prefix. Use the most common project key.
     2. Recent commit messages and branch names — `git log --oneline -100` and `git branch -a --sort=-committerdate | head -30`, same regex.
     3. Mentions in `CLAUDE.md`, `README.md`, or `.github/` files.
   - If exactly one project key is found, use it and tell the user ("Using Jira project `PROJ` based on recent PR titles").
   - If none found or multiple plausible keys, call `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` and `mcp__claude_ai_Atlassian__getVisibleJiraProjects` and ask the user which project to use.

3. Create the Jira issue with `mcp__claude_ai_Atlassian__createJiraIssue`:
   - `summary`: the current PR title
   - `description`: include the PR URL and a one-line summary of the change (derive from the PR body / commit messages)
   - `issueType`: `Task` (or whatever the project's default is — check with `mcp__claude_ai_Atlassian__getJiraProjectIssueTypesMetadata` if `Task` is rejected)
   - Capture the new issue key (e.g. `PROJ-123`).

4. Prefix the PR title with the new key:
   ```bash
   current_title=$(gh pr view <pr-number> --json title -q .title)
   gh pr edit <pr-number> --title "<KEY>: $current_title"
   ```

5. Close and re-open the PR to retrigger any workflows that key off the title:
   ```bash
   gh pr close <pr-number>
   gh pr reopen <pr-number>
   ```

6. Report the created ticket key and URL to the user, then proceed to step 3.

If ticket creation fails (auth, missing project, etc.), report the error and ask the user how to proceed — do NOT silently continue without the prefix.

### 3. Check for merge conflicts

```bash
gh pr view --json mergeable,mergeStateStatus -q '.'
```

If the PR has merge conflicts (`mergeable` is `"CONFLICTING"` or `mergeStateStatus` is `"DIRTY"`):
1. Fetch and merge the base branch locally:
   ```bash
   git fetch origin
   base_branch=$(gh pr view --json baseRefName -q '.baseRefName')
   git merge "origin/$base_branch"
   ```
2. Resolve the conflicts in each file. Read the conflicted files, understand both sides, and pick the correct resolution (preserving changes from both branches where appropriate).
3. After resolving all conflicts, stage the files, commit the merge, and push.
4. If the conflicts are too complex to resolve confidently, escalate to the user.

If no merge conflicts, proceed to the next step.

### 4. Wait for Cursor Bugbot to finish

Before checking results, see if Cursor Bugbot (or similar bot checks) is still running:

```bash
gh pr checks --json name,state,conclusion --jq '.[] | select(.state == "PENDING" or .state == "QUEUED" or (.state == "IN_PROGRESS") or (.conclusion == "" and .state != "COMPLETED")) | select(.name | test("cursor|bugbot"; "i"))'
```

If any Cursor Bugbot check is still in progress:
1. Report: "Cursor Bugbot is still running — waiting for it to finish before proceeding."
2. Poll every 30 seconds (up to 10 minutes) until the check completes:
   ```bash
   # Re-check status in a loop
   for i in $(seq 1 20); do
     result=$(gh pr checks --json name,state,conclusion --jq '.[] | select(.name | test("cursor|bugbot"; "i")) | .state + ":" + .conclusion')
     echo "Attempt $i: $result"
     # If all cursor/bugbot checks are COMPLETED, break
     if echo "$result" | grep -qv 'COMPLETED\|SUCCESS\|FAILURE\|CANCELLED\|NEUTRAL\|SKIPPED' 2>/dev/null; then
       sleep 30
     else
       break
     fi
   done
   ```
3. Once finished, proceed to step 5. The bot may have added new review comments that need to be addressed.

If no Cursor Bugbot check is running (or none exists), proceed immediately to step 5.

### 5. Check for failing checks

```bash
gh pr checks --json name,state,conclusion,link --jq '.[] | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED" or .state == "FAILURE")'
```

If there are no failing checks, report "All checks passing" and move to step 6 (bot comments).

For each failing check:
1. Read the check name and link to understand what failed.
2. If a log URL is available, fetch it with `gh api` or `gh run view --log-failed` to get failure details.
3. Diagnose the root cause by reading the relevant source files.
4. Fix the issue in the codebase.
5. After fixing ALL failing checks, stage the changed files, commit with a descriptive message, and push.

Common check failures and how to fix them:
- **ruff format**: Run `ruff format generator/` and commit the result.
- **schema-validation**: Regenerate DSL files or fix schema.json.
- **generate-and-compare**: Run the generator and commit updated files.
- **go vet / staticcheck**: Fix the reported Go issues.
- **go-coverage**: Fix failing Go tests.
- **lint / typecheck**: Fix the reported issues in the source.

### 6. Check for unresolved bot comments

```bash
# Get all review comments on the PR
gh api repos/{owner}/{repo}/pulls/{number}/comments --jq '.[] | select(.user.login | test("bot|cursor|coderabbit|copilot|claude"; "i")) | {id, user: .user.login, path, line, body, in_reply_to_id}'
```

Also check issue-style comments:
```bash
gh api repos/{owner}/{repo}/issues/{number}/comments --jq '.[] | select(.user.login | test("bot|cursor|coderabbit|copilot|claude"; "i")) | {id, user: .user.login, body}'
```

For each unresolved bot comment:
1. Read the comment body to understand what the bot is requesting.
2. If the comment points to a specific file and line, read that code.
3. Apply the fix. Do NOT skip comments because they seem unrelated to the PR's scope, or because they reference code from the base branch — address them anyway.
4. If the fix is too large or complex (e.g., requires a major refactor, touches many files, or has unclear trade-offs), ask the user for guidance instead of skipping.
5. After applying fixes, stage, commit with a message referencing the bot feedback, and push.

After pushing fixes, reply to each addressed bot comment and resolve its thread. **Do NOT resolve threads started by human reviewers** — only reply to those; the human must resolve their own threads.

1. **Reply** to the comment with a short explanation of the fix (e.g., "Fixed: changed `remeidation` → `remediation` in coverage_report.py line 298, commit abc1234"):
```bash
# For review comments (pulls/comments):
gh api repos/{owner}/{repo}/pulls/{number}/comments/{comment_id}/replies -f body="Fixed: <explanation>"

# For issue-style comments:
gh api repos/{owner}/{repo}/issues/{number}/comments -f body="Fixed: <explanation>"
```

2. **Resolve** bot review threads (skip this step for human reviewer threads):
```bash
# Find all review threads and their authors:
gh api graphql -f query='
  query {
    repository(owner: "OWNER", name: "REPO") {
      pullRequest(number: PR_NUM) {
        reviewThreads(first: 100) {
          nodes {
            id
            isResolved
            comments(first: 1) {
              nodes {
                body
                author { login }
              }
            }
          }
        }
      }
    }
  }
'

# For each thread: check if the author login matches a bot pattern
# (contains "bot", "cursor", "coderabbit", "copilot", "claude", etc.)
# If YES (bot) → resolve the thread.
# If NO (human reviewer) → do NOT resolve. The human resolves their own threads.
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "THREAD_NODE_ID"}) {
      thread { isResolved }
    }
  }
'
```

### 7. Loop until clean

If fixes were pushed during this iteration, you MUST loop back to step 3 and repeat the full cycle — pushing triggers new Bugbot runs and CI checks that must be waited on before declaring the PR clean. Do NOT re-run step 2 (Jira setup); that step runs once on the first iteration only.

Only declare the PR clean after completing a full iteration of steps 3–6 where NO fixes were needed (no merge conflicts, no failing checks, no unresolved bot comments). Always run steps 3–6 completely each iteration — the REST API queries in step 6 are the ONLY way to reliably detect bot comments. Never skip step 6 or substitute it with a GraphQL thread count.

Stop looping if:
- The max iteration count is reached (default 5). Report remaining issues to the user.
- A bot comment requires a change that is too large/complex — escalate to the user and stop.
- The same failure persists after 2 consecutive attempts to fix it — escalate to the user and stop.

Track the iteration count and report it (e.g., "Iteration 2/5").

### 8. Report

Summarize what was done:
- Jira ticket created (key + URL), if `--jira` was used
- Which checks were failing and how they were fixed
- Which bot comments were addressed and how
- Which bot comments were escalated to the user (with reason — should only be due to size/complexity)
- Current PR status

## Important Rules

- **Never force-push.** Always create new commits for fixes.
- **Address ALL bot comments.** Do not skip comments for being "out of scope" or "from the base branch." Only escalate to the user if the requested change is too large or complex to apply confidently.
- **Always resolve bot threads after fixing them.** Bot comments (cursor, coderabbit, copilot, etc.) must be resolved once addressed.
- **Never resolve human reviewer threads.** Human reviewers' threads must be left for the human to resolve, even if the underlying issue was fixed. Reply with what was done, but do not resolve.
- **Respect the codebase patterns.** Read CLAUDE.md files in relevant directories before making changes.
- **Keep commits atomic.** One commit per logical fix (e.g., separate "fix ruff format" from "fix Go test").
- If you cannot fix a failure after 2 attempts, report it clearly so the user can intervene.
