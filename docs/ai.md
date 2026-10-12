# peforth v2 AI support

The Python REPL optionally connects to the OpenAI Agents API. Transport helpers use Python's standard library; ordinary Forth use needs no API key or network access.

## Configuration

The bridge reads `~/.peforth/.env` (Windows: `$HOME\.peforth\.env`) when an AI request starts. Process environment variables take precedence.

```dotenv
OPENAI_API_KEY=your-platform-api-key
PEFORTH_AI_MODEL=gpt-6-luna
PEFORTH_AI_SKILLS_DIR=skills
PEFORTH_CONFIG_DIR=~/.peforth
PEFORTH_WSL_DISTRO=Ubuntu
```

`PEFORTH_AI_MODEL` is read at VM startup into the Forth `aiModel` value. The value is the current model used by new AI sessions and can be changed immediately with `s" model-name" to aiModel`; inspect it with `aiModel`.

Keep `.env` private. The local bridge sends the API key only as an HTTPS bearer credential. It does not put the key into the plugin, conversation, or tool result. Prompts and resulting conversation are sent to OpenAI according to the account's API data controls.

## Forth interface

- The REPL starts in Forth mode with the `> ` prompt. `chat` and `forth` switch modes (`see chat`, `see forth`). Chat mode uses `chat> ` and sends each submitted buffer to the current AI session. Multiline editing works in both modes; `bye` and Ctrl-D exit.
- `ai: <prompt>` sends the complete submitted buffer after `ai:` and streams the reply. The buffer may contain multiple lines.
- `(ai) ( prompt-string stream? -- [response-string] )` runs one turn. Use `false` to push the reply as a string, e.g. `s" Give me a short greeting" false (ai) . cr`; use `true` to stream it.
- `ai-status` shows the session selected by this running `f` process. Each new process starts without an active session.
- `ai-sessions` fetches remote sessions newest-first and refreshes `~/.peforth/.ai_session.json`, preserving local titles. The API provides creation and last-active times; CLI output shows only the final 8 ID characters.
- `n ai-session` shows details for a listed session. `n ai-use` selects a listed session for this process; alternatively use `s" <last-8-characters>" ai-use` or the full ID.
- `ai-context n count [chat|json]` returns recent user-initiated turns on the data stack; `chat` returns user/assistant text and `json` includes tool calls/results. `count` must be positive. Run `ai-sessions` before numbered words; print results with `stringify .`.
- `ai-new` clears this process's selection. `ai-containers` and `n ai-container` inspect hosted environments linked to listed sessions. This is not a billing meter.
- `n ai-cleanup` requires the exact confirmation `delete` and permanently removes the selected remote session/conversation. If an old hosted sandbox exists, cleanup may continue asynchronously. This cannot be undone.
- `ai-cancel` requests cancellation of an active API turn and can close the locally paused task. Already completed local side effects are not undone.

## Session state

`~/.peforth/.ai_session.json` is a local title overlay and session index, not an active-session resume mechanism. `ai-sessions` and REPL exit refresh its session list from the remote API while preserving titles. The active selection is held only in the current VM. Writes are atomic; simultaneous refreshes/manual edits are last-writer-wins. Separate devices syncing this file may conflict. Session state never restores the local VM stack, dictionary, or files.

`PEFORTH_CONFIG_DIR` selects the local config/session directory. Its default is `~/.peforth`; keep it separate from the source checkout and Forth resources. `PEFORTH_SKILLS_DIR` can select a custom skill directory. The repository's `skills/` and `plugins/` are source assets; they are not automatically installed into another AI CLI's global directories.

## Local Forth tools and approval

The AI can search the current dictionary. To run Forth it must request `peforth_run_forth`; the REPL displays the complete source and purpose, then enforces the approval mode: `trust` approves later AI programs for this Forth process, `yes` approves only this proposal, `no` declines, and `cancel` cancels the AI task. `ai-confirm` restores per-proposal approval. Trust resets when the process exits. If API submission fails after local execution, inspect the VM before retrying.

Approved code runs in the active local VM with the user's permissions; Python bridges can access files, processes, and network. Review every proposal. Network requests currently run synchronously, so the REPL cannot queue input while waiting for an API response; queueing is available at the local approval prompt.

## Troubleshooting and implementation

- Missing key: add `OPENAI_API_KEY` to the config `.env` or process environment.
- Skill not found: ensure `PEFORTH_AI_SKILLS_DIR` points to a directory containing `peforth-forth/SKILL.md`; use `ai-new` after changing skill instructions.
- Invalid API access/model: check the Platform project, model access, and API limits.
- Network interruption: inspect `ai-status`; use `ai-new` only when deliberately starting a new conversation.

`ai.f` owns Forth words and AI flow. It imports `ai_tools.py` for process and HTTP helpers; `repl.py` prepares runtime host information before loading the Forth AI dictionary. `ai_bridge.py` provides Agents API transport, response helpers, session-index operations, skill loading, and local output capture. No OpenAI SDK is required. Model usage is billed at the selected model's API rate.
