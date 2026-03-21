---
name: babysit-pr
description: Monitor the current branch's open PR for failing checks and unresolved bot comments (e.g. cursorbot), then fix the issues, push, and resolve the comments. Use with `/loop` for continuous monitoring.
argument-hint: [pr-number]
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Agent
---

# Babysit PR — Fix Failing Checks & Resolve Bot Comments

Monitor an open pull request for failing CI checks and unresolved bot review comments, fix the underlying issues, commit the fixes, push, and resolve the comments.

## Arguments

- `$0` — PR number (optional). If omitted, detect from the current branch using `gh pr view --json number -q .number`.

## Steps

### 1. Identify the PR

```bash
# If $0 is provided, use it. Otherwise detect from current branch:
gh pr view --json number,url,headRefName,state -q '.'
```

Confirm the PR is open. If not, stop and report.

### 2. Check for failing checks

```bash
gh pr checks --json name,state,conclusion,link --jq '.[] | select(.conclusion == "FAILURE" or .conclusion == "CANCELLED" or .state == "FAILURE")'
```

If there are no failing checks, report "All checks passing" and move to step 3.

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

### 3. Check for unresolved bot comments

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
3. If the suggestion is valid and actionable, apply the fix.
4. If the suggestion is a false positive or not applicable, note why (do NOT blindly apply every suggestion).
5. After applying valid fixes, stage, commit with a message referencing the bot feedback, and push.

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

### 4. Re-verify

After pushing fixes, wait briefly and re-check:
```bash
gh pr checks --watch --fail-fast
```

If new failures appear, loop back to step 2 (max 3 iterations to avoid infinite loops).

### 5. Report

Summarize what was done:
- Which checks were failing and how they were fixed
- Which bot comments were addressed and how
- Which bot comments were skipped (with reason)
- Current PR status

## Important Rules

- **Never force-push.** Always create new commits for fixes.
- **Don't blindly apply bot suggestions.** Evaluate each one — bots can be wrong.
- **Respect the codebase patterns.** Read CLAUDE.md files in relevant directories before making changes.
- **Keep commits atomic.** One commit per logical fix (e.g., separate "fix ruff format" from "fix Go test").
- **Max 3 fix-and-push cycles** to prevent infinite loops if a check keeps failing.
- If you cannot fix a failure, report it clearly so the user can intervene.
