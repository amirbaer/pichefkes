---
name: send-slack
description: Send the latest answer from the conversation to Slack via a webhook. Formats the message nicely with headers, tables, code blocks, and lists. Tries the new markdown block, falls back to section/mrkdwn blocks.
argument-hint: [custom title or topic override]
allowed-tools: Read, Bash
---

# Send Latest Answer to Slack

Send the most recent assistant answer from the current conversation to Slack via a webhook, with rich formatting.

## Configuration

The Slack webhook URL is read from the `SLACK_WEBHOOK_URL` environment variable (set in `~/.claude/settings.local.json`).

## Arguments

- `$0` (optional) — A custom title or topic to override the auto-detected one.

## Steps

### 1. Identify the latest answer

Review the conversation and identify your most recent substantive answer (the one just before the user invoked `/send-slack`). This is the content to send.

### 2. Build the payload — try `markdown` block first

First, try the new `markdown` block type which supports standard markdown.

#### Primary format: `markdown` block

```json
{
  "blocks": [
    {
      "type": "markdown",
      "text": "# Title\n\nStandard markdown content...\n\n## Section\n\n| Col A | Col B |\n|-------|-------|\n| val 1 | val 2 |"
    },
    {
      "type": "context",
      "elements": [{"type": "mrkdwn", "text": "Sent from Claude Code | 2026-04-05"}]
    }
  ]
}
```

The `markdown` block supports standard markdown: `# headers`, `**bold**`, `*italic*`, `` `code` ``, triple-backtick code blocks with language tags, `> blockquotes`, `---` horizontal rules, `- lists`, `1. ordered lists`, `- [ ] task lists`, `~~strikethrough~~`, `[links](url)`, and pipe-delimited tables.

**12,000 character cumulative limit** across all `markdown` blocks in a single payload.

### 3. Send and handle fallback

```bash
cat > /tmp/slack_payload.json << 'JSONEOF'
{ ... primary payload ... }
JSONEOF

HTTP_STATUS=$(curl -s -o /tmp/slack_response.txt -w "%{http_code}" \
  -X POST -H 'Content-type: application/json' \
  -d @/tmp/slack_payload.json \
  "$SLACK_WEBHOOK_URL")

echo "HTTP status: $HTTP_STATUS"
cat /tmp/slack_response.txt
```

**If the response is `200` and `ok`**: done — report success.

**If the response is `500` or `400` (markdown block not supported)**: rebuild the payload using the fallback format below and retry.

#### Fallback format: `header` + `section`/`mrkdwn` blocks

When the `markdown` block is not supported, use legacy Block Kit:

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "Title Here", "emoji": true}
    },
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "Content in Slack mrkdwn format"}
    },
    {"type": "divider"},
    {
      "type": "section",
      "text": {"type": "mrkdwn", "text": "More content..."}
    },
    {
      "type": "context",
      "elements": [{"type": "mrkdwn", "text": "Sent from Claude Code | 2026-04-05"}]
    }
  ]
}
```

##### Slack `mrkdwn` formatting rules (different from standard markdown!)

- **Bold**: `*bold*` (single asterisk, NOT double)
- **Italic**: `_italic_`
- **Strikethrough**: `~text~` (single tilde)
- **Code inline**: `` `code` ``
- **Code block**: triple backticks (no language tag support)
- **Bullet lists**: `• item` or `- item` (with `\n` between items)
- **Numbered lists**: `1. item` (with `\n` between items)
- **Links**: `<https://url|label>`
- **Block quotes**: `> text`
- No header syntax — use `header` blocks instead
- No table syntax — see table formatting below

##### Table formatting in fallback mode

Since `mrkdwn` has no table support, convert tables using one of:

1. **Code block** (best for multi-column data):
   ```
   ```
   Column A   | Column B   | Column C
   -----------|------------|----------
   value 1    | value 2    | value 3
   ```
   ```

2. **Section fields** (best for short key-value pairs, max 10 fields):
   ```json
   {
     "type": "section",
     "fields": [
       {"type": "mrkdwn", "text": "*Label 1*\nValue 1"},
       {"type": "mrkdwn", "text": "*Label 2*\nValue 2"}
     ]
   }
   ```

3. **Bold-header list** (best for 2-column key-value):
   ```
   *Key 1:* value 1\n*Key 2:* value 2
   ```

##### Fallback block limits

- Each `text` field in a section block: **3,000 character limit**. Split longer content across multiple section blocks.
- Maximum 50 blocks per message.

### 4. Report result

- If HTTP status is `200` and body is `ok`, report success and which format was used.
- If both attempts fail, report the error. Common issues:
  - `invalid_payload`: malformed JSON — check escaping, fix, and retry once.
  - `channel_not_found`: webhook is misconfigured.
  - Missing `SLACK_WEBHOOK_URL`: tell the user to set it in `~/.claude/settings.local.json` under `env`.

## Formatting guidelines (apply to both formats)

1. **Start with a clear title**: derived from the topic or from `$0` if provided.
2. **Structure with sections**: use headers/dividers to break up content logically.
3. **Use tables for structured data**: comparisons, listings, reference data.
4. **Use code blocks for code**: with language tags when using `markdown` block.
5. **Use block quotes for callouts**: key takeaways or important notes.
6. **Separate major sections** with dividers or horizontal rules.

## Important rules

- Always include a context block at the bottom with: `"Sent from Claude Code"` and the current date.
- Do not include tool calls, file reads, or other internal actions — only the final answer content.
- Sanitize the content: remove any `<system-reminder>` tags or internal metadata.
- If the answer is empty or trivial (e.g., just "ok" or "done"), tell the user there's nothing substantial to send.
- If `$0` is provided, use it as the title instead of auto-detecting.
