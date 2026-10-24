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
PEFORTH_PWSH_PATH=
```

On WSL, PowerShell uses Windows `pwsh.exe`: `system_info` first discovers it on the WSL `PATH`, then uses `PEFORTH_PWSH_PATH` if discovery fails. Set that optional value to a WSL-accessible executable path (for example, `/mnt/c/.../pwsh.exe`). `system_info.shells.pwsh` reports the resolved `path`, `execution_host`, and `source` (`path` or `env`); `run_pwsh` launches that path directly through `subprocess`.

`PEFORTH_AI_MODEL` is read at VM startup into the Forth `aiModel` value. The value is the current model used by new AI sessions and can be changed immediately with `s" model-name" to aiModel`; inspect it with `aiModel`.

Keep `.env` private. The local bridge sends the API key only as an HTTPS bearer credential. It does not put the key into the plugin, conversation, or tool result. Prompts and resulting conversation are sent to OpenAI according to the account's API data controls.

## Forth interface

- The REPL starts in Forth mode with the `> ` prompt. `chat` and `forth` switch modes (`see chat`, `see forth`). Chat mode uses `chat> ` and sends each submitted buffer to the current AI session. Multiline editing works in both modes; `bye` and Ctrl-D exit.
- `ai: <prompt>` sends the complete submitted buffer after `ai:` and streams the reply. The buffer may contain multiple lines.
- `(ai) ( prompt-string stream? -- [response-string] )` runs one turn. Use `false` to push the reply as a string, e.g. `s" Give me a short greeting" false (ai) . cr`; use `true` to stream it.
- The `(ai)` `stream?` flag controls terminal output versus returning the reply on the Forth stack; it does not select HTTP/SSE transport. The CLI selects transport separately.
- `f -c <prompt>` is a one-shot command that starts a new session, submits with the non-streaming Agents API, polls session/turn state, and retrieves the saved final answer. It writes `SESSION_ID=<id>` to stderr after completion. To continue an existing session, put `-id <session-id>` before `-c`, e.g. `f -id sess_... -c <prompt>`. There is no implicit “latest idle session” selection. Interactive `ai:` keeps SSE streaming.

Transport timeouts are configurable in seconds: `PEFORTH_AI_REQUEST_TIMEOUT` (default 30) bounds each HTTP request and each finite HTTP response-body read; `PEFORTH_AI_STREAM_TIMEOUT` (default 300) bounds SSE connection/read inactivity; and `PEFORTH_AI_POLL_INTERVAL` (default 0.5) sets the non-streaming poll interval. There is no overall AI-turn timeout. An SSE stream that continues receiving keepalives can stay open indefinitely; the Watchdog may warn about no objective progress but does not close it. A timed-out prompt POST may have been accepted; its outcome is reported as uncertain, and peforth does not retry the prompt automatically. After a timeout, inspect the session before retrying.

### Progress Watchdog

Run `python tools/peforth_logging_monitor.py --watchdog` from the source repository to enable read-only progress monitoring for that environment's diagnostics database. It uses Windows Message Box alerts (also via Windows PowerShell from WSL), not LINE. The fixed no-objective-progress threshold is five minutes. The monitor also alerts for recently active runtimes that ended unexpectedly, using `--orphan-lookback-hours` (default 24; any positive finite value is accepted). It does not alert on approval waits, cancel a turn, kill a process, or resend a prompt. One popup is shown at a time; after dismissal the same unresolved warning repeats every five minutes. Recovery stops future reminders but does not close an open popup or show an all-clear message. On monitor restart, current qualifying issues are reevaluated without replaying the historical timeline.

Objective progress means an actual remote-turn state change, a new tool/action/call ID, an accepted tool result, or assistant output growth. Repeated polling, SSE keepalives, and free-text heartbeat messages do not reset the timer. Alerts show only short IDs and whitespace-collapsed previews of up to 60 prompt/heartbeat characters; diagnostic SQLite and desktop previews may contain sensitive text. `PEFORTH_AI_LOG_MODE=disabled` leaves runtime behavior unchanged but disables diagnostics and Watchdog coverage.

AI-created sessions receive the fixed-scope `peforth_tick_heartbeat` tool. It only records a diagnostic message; arbitrary Forth continues through the existing approval flow. Agents API tools are fixed when a remote session is created, so an older session will not gain the heartbeat tool; objective progress monitoring still works for its recorded events.
- `ai-status` shows the current process's selected session and its full ID. Each new process starts without an active session.
- `ai-sessions` fetches remote sessions newest-first and refreshes `~/.peforth/.ai_session.json`, preserving local titles. It displays each full Session ID along with creation and last-active times.
- `n ai-session` shows details for a listed session; it also accepts `s" <full-session-id>" ai-session`. `n ai-use` selects a listed session for this process; it accepts the full ID and retains support for an unambiguous ID suffix.
- `ai-context n count [chat|json]` returns recent user-initiated turns on the data stack; `chat` returns user/assistant text and `json` includes tool calls/results. `count` must be positive. Run `ai-sessions` before numbered words; print results with `stringify .`.
- `n ai-cleanup` accepts either a list number or full ID and immediately, permanently removes that remote session and conversation without a confirmation prompt. This cannot be undone.
- `ai-cancel` requests cancellation of an active API turn and can close the locally paused task. Already completed local side effects are not undone.

## Session state

`~/.peforth/.ai_session.json` is a local title overlay and session index, not an active-session resume mechanism. `ai-sessions` and REPL exit refresh its session list from the remote API while preserving titles. The active selection is held only in the current VM. Writes are atomic; simultaneous refreshes/manual edits are last-writer-wins. Separate devices syncing this file may conflict. Session state never restores the local VM stack, dictionary, or files.

`PEFORTH_CONFIG_DIR` selects the local config/session directory. Its default is `~/.peforth`; keep it separate from the source checkout and Forth resources. `PEFORTH_SKILLS_DIR` can select a custom skill directory. The repository's `skills/` and `plugins/` are source assets; they are not automatically installed into another AI CLI's global directories.

## Local Forth tools and approval

The AI can search the current dictionary. To run Forth it must request `peforth_run_forth`; the REPL routes pending proposals through the editable `ai-approve` Forth word. `allow_once` approves one proposal; `trust_task` covers later proposals in the same AI Task only and expires when that Task completes, fails, or is cancelled; `deny` declines; and `cancel` cancels the AI Task. Runtime-wide Trust is enabled explicitly with `ai-trust-runtime` and revoked with `ai-confirm`, which also clears any active Task Trust. Runtime Trust ends at `ai-confirm` or process exit. If API submission fails after local execution, inspect the VM before retrying.

Approved code runs in the active local VM with the user's permissions; Python bridges can access files, processes, and network. Review every proposal. Network requests currently run synchronously, so the REPL cannot queue input while waiting for an API response; queueing is available at the local approval prompt.

## Troubleshooting and implementation

- Missing key: add `OPENAI_API_KEY` to the config `.env` or process environment.
- Skill not found: ensure `PEFORTH_AI_SKILLS_DIR` points to a directory containing `peforth-forth/SKILL.md`; use `ai-new` after changing skill instructions.
- Invalid API access/model: check the Platform project, model access, and API limits.
- Network interruption: inspect `ai-status`; use `ai-new` only when deliberately starting a new conversation.

`ai.f` owns Forth words and AI flow. It imports `ai_tools.py` for process and HTTP helpers; `repl.py` prepares runtime host information before loading the Forth AI dictionary. `ai_bridge.py` provides Agents API transport, response helpers, session-index operations, skill loading, and local output capture. No OpenAI SDK is required. Model usage is billed at the selected model's API rate.

The one-shot polling path follows the Agents API's non-streaming session creation and input-event endpoints, then reads session state, turns, and saved items. See [Run and continue sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions) and [Events and items](https://developers.openai.com/api/docs/guides/agents-api/sessions/events). The API's streaming guide requires subscribing before submitting work; streams do not replay missed events, which is why this path avoids SSE for `f -c` rather than racing a GET against the POST.
