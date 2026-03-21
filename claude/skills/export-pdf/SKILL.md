---
name: export-pdf
description: Export the current conversation to a nicely formatted PDF document. Use when the user asks to export, save, or create a PDF summary of the conversation.
argument-hint: <output-filename> [previous-pdf-path]
disable-model-invocation: true
allowed-tools: Read, Write, Bash
---

# Export Conversation to PDF

Create a nicely formatted PDF summarizing the current conversation.

## Output location

Save PDFs to `~/Downloads/claude-pdfs/`. Create the directory if it doesn't exist (`mkdir -p ~/Downloads/claude-pdfs`).

## Arguments

- `$0` — Output filename (required). Append `.pdf` if missing. Saved to `~/Downloads/claude-pdfs/`.
- `$1` — Path to a previous PDF to merge with (optional). Can be an absolute path or a filename inside `~/Downloads/claude-pdfs/`.

Examples:
- `/export-pdf backend-arch` — export current conversation to `~/Downloads/claude-pdfs/backend-arch.pdf`
- `/export-pdf backend-arch-combined ~/Downloads/claude-pdfs/backend-arch.pdf` — merge previous PDF with current conversation

## Merging with a previous PDF

If `$1` is provided:

1. **Read the previous PDF** using the Read tool. If it's large, use the `pages` parameter to read it in chunks (max 20 pages per read).
2. **Incorporate its content** into the HTML as earlier sections, preserving the original formatting (headings, tables, code blocks, question boxes, etc.). Reproduce the content faithfully — do not just link to or embed the old PDF.
3. **Add the current conversation** as subsequent sections, continuing the section numbering.
4. **Update the title page** to reflect the combined scope (e.g., "Backend Architecture Deep Dive — Parts 1 & 2").
5. **Generate a unified table of contents** covering all sections from both sources.
6. **Save as a new file** — do not overwrite the previous PDF.

## Steps

1. **Gather content**: Review the full conversation. Identify all user questions and your answers. Group them by topic into logical sections. If merging with an existing PDF, read that PDF first and incorporate its content.

2. **Write HTML**: Create an HTML file at `/tmp/conversation_export.html` using the template and styling rules below. Include ALL questions asked and ALL answers given — do not summarize or omit details.

3. **Install weasyprint** (if needed):
   ```bash
   python3 -m venv /tmp/pdfenv && /tmp/pdfenv/bin/pip install weasyprint
   ```

4. **Generate PDF**:
   ```bash
   /tmp/pdfenv/bin/python3 -c "from weasyprint import HTML; HTML('/tmp/conversation_export.html').write_pdf('/path/to/output.pdf')"
   ```

5. **Verify**: Check the PDF was created and report its location and page count.

## HTML Template

Use this structure:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  /* Page setup */
  @page {
    size: A4;
    margin: 2cm 1.8cm;
    @bottom-center {
      content: "Page " counter(page) " of " counter(pages);
      font-size: 9px;
      color: #888;
    }
  }

  /* Base */
  body {
    font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif;
    font-size: 11px;
    line-height: 1.55;
    color: #1a1a2e;
  }

  /* Headings */
  h1 {
    font-size: 26px;
    color: #0f3460;
    border-bottom: 3px solid #e94560;
    padding-bottom: 10px;
    margin-top: 40px;
    page-break-after: avoid;
  }
  h1:first-of-type { margin-top: 0; }
  h2 {
    font-size: 18px;
    color: #16213e;
    border-bottom: 2px solid #0f3460;
    padding-bottom: 6px;
    margin-top: 28px;
    page-break-after: avoid;
  }
  h3 {
    font-size: 14px;
    color: #e94560;
    margin-top: 20px;
    page-break-after: avoid;
  }
  h4 {
    font-size: 12px;
    color: #533483;
    margin-top: 14px;
    page-break-after: avoid;
  }

  /* Text */
  p, li { margin-bottom: 4px; }
  ul, ol { padding-left: 22px; }

  /* Tables */
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 10px;
    page-break-inside: avoid;
  }
  th {
    background: #0f3460;
    color: white;
    padding: 7px 10px;
    text-align: left;
    font-weight: 600;
  }
  td {
    padding: 6px 10px;
    border-bottom: 1px solid #ddd;
  }
  tr:nth-child(even) { background: #f0f4ff; }

  /* Code */
  code {
    background: #f0f0f5;
    padding: 1px 5px;
    border-radius: 3px;
    font-family: 'Menlo', 'Consolas', monospace;
    font-size: 10px;
    color: #533483;
  }
  pre {
    background: #1a1a2e;
    color: #e0e0e0;
    padding: 14px;
    border-radius: 6px;
    font-size: 9.5px;
    line-height: 1.5;
    overflow-x: auto;
    page-break-inside: avoid;
  }
  pre code {
    background: none;
    color: #e0e0e0;
    padding: 0;
  }

  /* Title page */
  .title-page {
    text-align: center;
    padding-top: 180px;
    page-break-after: always;
  }
  .title-page h1 {
    font-size: 36px;
    border: none;
    color: #0f3460;
  }
  .title-page .subtitle {
    font-size: 18px;
    color: #e94560;
    margin-top: 10px;
  }
  .title-page .date {
    font-size: 13px;
    color: #888;
    margin-top: 30px;
  }
  .title-page .meta {
    font-size: 12px;
    color: #533483;
    margin-top: 8px;
    font-family: monospace;
  }

  /* Question callout box */
  .q-box {
    background: #fff3e6;
    border-left: 4px solid #e94560;
    padding: 10px 14px;
    margin: 16px 0 10px 0;
    font-style: italic;
    color: #333;
    page-break-after: avoid;
  }

  /* Flow diagram box */
  .flow-box {
    background: #f7f7ff;
    border: 1px solid #c0c0e0;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 10px 0;
    font-family: monospace;
    font-size: 9.5px;
    line-height: 1.6;
    page-break-inside: avoid;
  }

  /* Section dividers */
  .section-divider {
    border: none;
    border-top: 2px solid #e94560;
    margin: 30px 0;
  }

  /* Highlight span */
  .highlight {
    background: #ffe0e6;
    padding: 2px 5px;
    border-radius: 3px;
  }

  /* Table of contents */
  .toc { margin: 20px 0; }
  .toc a { color: #0f3460; text-decoration: none; }
  .toc li { margin-bottom: 6px; font-size: 12px; }
</style>
</head>
<body>
  <!-- TITLE PAGE -->
  <div class="title-page">
    <h1>Document Title</h1>
    <div class="subtitle">Comprehensive Q&A Summary</div>
    <div class="meta">optional metadata line</div>
    <div class="date">Date</div>
  </div>

  <!-- TABLE OF CONTENTS -->
  <h1>Table of Contents</h1>
  <ol class="toc">
    <li><a href="#section-1">Section 1 Title</a></li>
    <!-- ... -->
  </ol>

  <!-- CONTENT SECTIONS -->
  <hr class="section-divider">
  <h1 id="section-1">1. Section Title</h1>
  <div class="q-box">Q: The user's question goes here</div>
  <p>Answer content with <strong>bold</strong>, <code>code</code>, tables, lists, etc.</p>

  <!-- Use tables for structured data -->
  <table>
    <tr><th>Column 1</th><th>Column 2</th></tr>
    <tr><td>Data</td><td>Data</td></tr>
  </table>

  <!-- Use flow-box for sequential processes -->
  <div class="flow-box">
    1. Step one<br>
    &nbsp;&nbsp;&nbsp;&rarr; Sub-step<br>
    2. Step two
  </div>
</body>
</html>
```

## Formatting rules

- **Title page**: Derive the title from the conversation topic. Include the current date. Include the working directory or repo path as metadata if relevant.
- **Table of contents**: List all sections with anchor links.
- **Question callout boxes** (`q-box`): Show each user question before its answer section.
- **Tables**: Use for all structured comparisons, listings, and reference data.
- **Flow boxes** (`flow-box`): Use for sequential processes and data flows. Use `&rarr;` for arrows and `&nbsp;` for indentation.
- **Code blocks** (`pre`): Use for code snippets, config examples, and file contents.
- **Section dividers** (`hr.section-divider`): Place between major sections.
- **Highlight spans**: Use `<span class="highlight">` to call attention to critical details.
- Group related Q&A into single sections when they cover the same topic.
- Preserve all detail from the conversation — do not summarize or drop content.
