---
description: Read the previous response (or given text) out loud with a neural voice
allowed-tools: Bash(edge-tts:*), Bash(afplay:*), Bash(nohup:*), Bash(pkill:*), Bash(say:*), Write
---

Speak a response out loud.

VOICE: en-US-AvaNeural (edge-tts — Microsoft neural TTS; synthesizes over the network)
FALLBACK VOICE: Samantha (macOS say — offline; always pass `-v` explicitly, this Mac's default system voice is broken and plain `say` produces silence)

If the arguments are exactly "stop": run `pkill -x afplay; pkill -x say; pkill -f edge-tts` to stop any playback or synthesis in progress, confirm in one line, and do nothing else.

Otherwise:

1. Determine what to speak:
   - No arguments → the full text of your most recent assistant response before this command.
   - Arguments present → they are either literal text to speak, or a description of which earlier response/section to speak (e.g. "the caveats part", "your answer about hooks"). Use judgment. Arguments: $ARGUMENTS
2. Rewrite the text for listening, not reading: drop fenced code blocks and tables (replace each with a one-sentence summary), drop URLs, file paths in parentheses, and markdown formatting marks. Read headings as plain sentences.
3. Write the cleaned text to /tmp/claude-speak.txt using the Write tool, then run:
   `edge-tts --voice en-US-AvaNeural --file /tmp/claude-speak.txt --write-media /tmp/claude-speak.mp3 && nohup afplay /tmp/claude-speak.mp3 >/dev/null 2>&1 &`
   Notes: edge-tts needs network access — if it fails inside the sandbox, run it outside the sandbox. Playback is backgrounded so it doesn't block the session.
4. If edge-tts fails (offline, service down), fall back to:
   `nohup say -v Samantha -f /tmp/claude-speak.txt >/dev/null 2>&1 &`
5. Reply with one short line confirming it's speaking. Do not repeat the spoken text in your reply.
