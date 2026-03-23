---
name: babysit-pr
description: Monitor the current branch's open PR for failing checks and unresolved bot comments (e.g. cursorbot), then fix the issues, push, and resolve the comments. Use with `/loop` for continuous monitoring.
argument-hint: [pr-number]
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Agent
---

# Babysit PR — Fix Failing Checks & Resolve Bot Comments

Monitor an open pull request for failing CI checks and unresolved bot review comments, fix the underlying issues, commit the fixes, push, and resolve the comments.

## Arguments

- PR number (optional) — Pass as a bare number (e.g., `/babysit-pr 123`). If omitted, detect from the current branch using `gh pr view --json number -q .number`.
- `--loop N` (optional, default: 5) — Maximum fix cycles before stopping. E.g., `/babysit-pr --loop 3` or `/babysit-pr 123 --loop 3`.

## Steps

### 1. Identify the PR

```bash
# If $0 is provided, use it. Otherwise detect from current branch:
gh pr view --json number,url,headRefName,state -q '.'
```

Confirm the PR is open. If not, stop and report.

### 2. Wait for Cursor Bugbot to finish

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
3. Once finished, proceed to step 3. The bot may have added new review comments that need to be addressed.

If no Cursor Bugbot check is running (or none exists), proceed immediately to step 3.

### 3. Check for failing checks

```bash
gh pr checks --json name,state,conclusion,link --jq '.[] | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED" or .state == "FAILURE")'
```

If there are no failing checks, report "All checks passing" and move to step 4 (bot comments).

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

### 4. Check for unresolved bot comments

```bash
# Get all review comments on the PR
gh api repos/{owner}/{repo}/pulls/{number}/comments --jq '.[] | select(.user.login | test("bot|cursor|coderabbit|copilot"; "i")) | {id, user: .user.login, path, line, body, in_reply_to_id}'
```

Also check issue-style comments:
```bash
gh api repos/{owner}/{repo}/issues/{number}/comments --jq '.[] | select(.user.login | test("bot|cursor|coderabbit|copilot"; "i")) | {id, user: .user.login, body}'
```

For each unresolved bot comment:
1. Read the comment body to understand what the bot is requesting.
2. If the comment points to a specific file and line, read that code.
3. Apply the fix. Do NOT skip comments because they seem unrelated to the PR's scope, or because they reference code from the base branch — address them anyway.
4. If the fix is too large or complex (e.g., requires a major refactor, touches many files, or has unclear trade-offs), ask the user for guidance instead of skipping.
5. After applying fixes, stage, commit with a message referencing the bot feedback, and push.

After pushing fixes, resolve the addressed review threads:
```bash
# For GraphQL thread resolution (preferred for review comments):
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
```

Then resolve each addressed thread:
```bash
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "THREAD_NODE_ID"}) {
      thread { isResolved }
    }
  }
'
```

### 5. Loop until clean

After pushing fixes, loop back to step 2 and repeat the full cycle (wait for bots, check failures, check bot comments, fix, push). At the **start** of each iteration, check if there are any failing checks or unresolved bot comments — if everything is clean, stop early and report success.

Stop looping if:
- The max iteration count is reached (default 5). Report remaining issues to the user.
- A bot comment requires a change that is too large/complex — escalate to the user and stop.
- The same failure persists after 2 consecutive attempts to fix it — escalate to the user and stop.

Track the iteration count and report it (e.g., "Iteration 2/5").

### 6. Report

Summarize what was done:
- Which checks were failing and how they were fixed
- Which bot comments were addressed and how
- Which bot comments were escalated to the user (with reason — should only be due to size/complexity)
- Current PR status

## Important Rules

- **Never force-push.** Always create new commits for fixes.
- **Address ALL bot comments.** Do not skip comments for being "out of scope" or "from the base branch." Only escalate to the user if the requested change is too large or complex to apply confidently.
- **Respect the codebase patterns.** Read CLAUDE.md files in relevant directories before making changes.
- **Keep commits atomic.** One commit per logical fix (e.g., separate "fix ruff format" from "fix Go test").
- If you cannot fix a failure after 2 attempts, report it clearly so the user can intervene.
