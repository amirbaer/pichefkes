---
name: send-slack
description: Send the latest answer from the conversation to Slack via a webhook. Formats the message using Slack's markdown block with full markdown support including headers, tables, and code blocks.
argument-hint: [custom title or topic override]
allowed-tools: Read, Bash
---

# Send Latest Answer to Slack

Send the most recent assistant answer from the current conversation to Slack, formatted using the new `markdown` block type for rich rendering.

## Configuration

The Slack webhook URL is read from the `SLACK_WEBHOOK_URL` environment variable (set in `~/.claude/settings.local.json`).

## Arguments

- `$0` (optional) — A custom title or topic to override the auto-detected one.

## Steps

### 1. Identify the latest answer

Review the conversation and identify your most recent substantive answer (the one just before the user invoked `/send-slack`). This is the content to send.

### 2. Convert to Slack Block Kit JSON using the `markdown` block

Transform the answer into a Slack Block Kit payload using the `markdown` block type. This block supports **standard markdown syntax** — not Slack's legacy `mrkdwn`.

#### Payload structure

```json
{
  "blocks": [
    {
      "type": "markdown",
      "text": "# Title\n\nFull markdown content here..."
    }
  ]
}
```

#### The `markdown` block

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Must be `"markdown"` |
| `text` | string | Standard markdown content. 12,000 character cumulative limit per payload. |

#### Supported markdown syntax

Use **standard markdown** — not Slack `mrkdwn`. The `markdown` block supports:

- **Headers**: `# H1`, `## H2`, `### H3`, etc.
- **Bold**: `**bold**` or `__bold__`
- **Italic**: `*italic*` or `_italic_`
- **Strikethrough**: `~~text~~`
- **Links**: `[label](https://url)`
- **Inline code**: `` `code` ``
- **Code blocks**: Triple backticks with optional language identifier for syntax highlighting
- **Block quotes**: `> text`
- **Horizontal rules**: `---`
- **Unordered lists**: `- item` or `* item`
- **Ordered lists**: `1. item`
- **Task lists**: `- [ ] todo` and `- [x] done`
- **Tables**: Standard pipe-delimited markdown tables:
  ```
  | Column A | Column B | Column C |
  |----------|----------|----------|
  | value 1  | value 2  | value 3  |
  ```
- **Images**: `![alt](url)` (rendered as hyperlinks in Slack)

#### Formatting guidelines

1. **Start with a header**: Use `# Title` as the first line, derived from the topic or from `$0` if provided.
2. **Use headers to structure sections**: `## Section` and `### Subsection` for logical grouping.
3. **Use tables for structured data**: Any comparisons, listings, or reference data should be markdown tables.
4. **Use code blocks with language tags**: e.g., ` ```python ` for syntax highlighting.
5. **Use block quotes for callouts**: `> Important: ...` for key takeaways.
6. **Use horizontal rules** (`---`) to separate major sections.
7. **Use task lists** for action items or checklists.

#### Combining with other block types

You may combine `markdown` blocks with other block types for richer layouts:

- **Divider block**: `{"type": "divider"}` between major sections if needed.
- **Context block**: Use at the bottom for attribution:
  ```json
  {"type": "context", "elements": [{"type": "mrkdwn", "text": "Sent from Claude Code | 2024-01-15"}]}
  ```

#### Content limits

- The `text` field in a `markdown` block has a **12,000 character cumulative limit per payload**.
- If the content exceeds this, truncate gracefully at a logical section boundary and append: `\n\n---\n*Message truncated due to Slack limits.*`
- Maximum 50 blocks per message.

### 3. Send the message

Write the payload to a temp file and send via curl to avoid shell escaping issues:

```bash
cat > /tmp/slack_payload.json << 'JSONEOF'
{
  "blocks": [ ... ]
}
JSONEOF

HTTP_STATUS=$(curl -s -o /tmp/slack_response.txt -w "%{http_code}" \
  -X POST -H 'Content-type: application/json' \
  -d @/tmp/slack_payload.json \
  "$SLACK_WEBHOOK_URL")

echo "HTTP status: $HTTP_STATUS"
cat /tmp/slack_response.txt
```

### 4. Report result

- If HTTP status is `200` and body is `ok`, report success.
- Otherwise, report the error. Common issues:
  - `invalid_payload`: malformed JSON — check escaping, fix, and retry once.
  - `channel_not_found`: webhook is misconfigured.
  - Missing `SLACK_WEBHOOK_URL`: tell the user to set it in `~/.claude/settings.local.json` under `env`.

## Important rules

- Always include a context block at the bottom with: `"Sent from Claude Code"` and the current date.
- Use **standard markdown** formatting, not Slack `mrkdwn` — the `markdown` block type handles the rendering.
- Do not include tool calls, file reads, or other internal actions in the message — only the final answer content.
- Sanitize the content: remove any `<system-reminder>` tags or internal metadata.
- If the answer is empty or trivial (e.g., just "ok" or "done"), tell the user there's nothing substantial to send instead of sending it.
- If `$0` is provided, use it as the `# Title` header instead of auto-detecting.
