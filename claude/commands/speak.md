---
description: Read the previous response (or given text) out loud with a neural voice
allowed-tools: Bash(edge-tts:*), Bash(afplay:*), Bash(nohup:*), Bash(pkill:*), Bash(say:*), Write
---

Speak a response out loud.

VOICE: en-US-AvaNeural (edge-tts — Microsoft neural TTS; synthesizes over the network)
FALLBACK VOICE: Samantha (macOS say — offline; always pass `-v` explicitly, this Mac's default system voice is broken and plain `say` produces silence)

Match the FIRST word of the arguments (case-insensitively) against the sub-commands below. Arguments: $ARGUMENTS

**Playback control** — do the action, confirm in one line, and do nothing else:
- `stop` → `pkill -x afplay; pkill -x say; pkill -f edge-tts` (stop playback/synthesis in progress).
- `pause` → `pkill -STOP -x afplay; pkill -STOP -x say` (freezes playback in place; resume with `continue`).
- `continue` (or `resume`) → `pkill -CONT -x afplay; pkill -CONT -x say` (resume paused playback).

**Summary modes** — produce a summary of your most recent assistant response before this command, in the named style, then BOTH show the summary in your reply AND speak it (steps 1–4 below; for these modes the user wants to see it as well as hear it, so do repeat it in step 4):
- `eli5` → explain it like I'm five: plain words, no jargon, short sentences, an everyday analogy if it helps. Optimize for "someone with zero background now gets it."
- `executive` → an executive summary: lead with the bottom line (status / decision / outcome), then only the few facts that change a decision; omit mechanism and detail. Optimize for "a busy decision-maker gets the signal in twenty seconds."
- `tldr` (also `tl;dr`, `tltr`) → the single most important takeaway in one or two sentences. Optimize for brevity above all.

**Otherwise, speak text** — then continue to step 1:
- No arguments → the full text of your most recent assistant response before this command.
- Arguments present → they are either literal text to speak, or a description of which earlier response/section to speak (e.g. "the caveats part", "your answer about hooks"). Use judgment.

For summary modes and speak-text:

1. Take the text to speak (the summary you just wrote, or the response/arguments above).
2. Rewrite the text for listening, not reading: drop fenced code blocks and tables (replace each with a one-sentence summary), drop URLs, file paths in parentheses, and markdown formatting marks. Read headings as plain sentences.
3. Write the cleaned text to /tmp/claude-speak.txt using the Write tool, then run:
   `edge-tts --voice en-US-AvaNeural --file /tmp/claude-speak.txt --write-media /tmp/claude-speak.mp3 && nohup afplay /tmp/claude-speak.mp3 >/dev/null 2>&1 &`
   Notes: edge-tts needs network access — if it fails inside the sandbox, run it outside the sandbox. Playback is backgrounded so it doesn't block the session.
4. If edge-tts fails (offline, service down), fall back to:
   `nohup say -v Samantha -f /tmp/claude-speak.txt >/dev/null 2>&1 &`
5. Reply with one short line confirming it's speaking. Do not repeat the spoken text — EXCEPT for the summary modes (eli5 / executive / tldr), where you should include the summary text in your reply since the user asked to be given it.
