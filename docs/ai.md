# Project K AI support (Python CLI)

The Python REPL has an optional OpenAI Agents API integration. The bridge uses only the Python standard library; ordinary Forth use does not require a key or network access.

## Configuration

The bridge reads `py/.env` when an AI request starts. An operating-system environment variable takes precedence over a value in `.env`.

```dotenv
OPENAI_API_KEY=your-platform-api-key
PROJECTK_AI_MODEL=gpt-6-astra
PROJECTK_AI_SKILLS_DIR=skills
```

`PROJECTK_AI_MODEL` selects the Agents API model. `PROJECTK_AI_SKILLS_DIR` selects the directory containing `projectk-forth/SKILL.md`; a relative path resolves from the Python directory. The default is `py/skills`. For new sessions, the skill and Forth reference are included in agent instructions because `environment.type: "none"` has no filesystem for loading a plugin. New sessions do not provision an OpenAI-hosted sandbox/container. Existing sessions keep their original configuration.

Keep `.env` private. The local bridge sends the API key only as the HTTPS bearer credential. It does not put the key into the plugin, conversation, or tool result. The prompt and resulting conversation are sent to OpenAI's service according to the account's API data controls.

## Forth interface

- The REPL starts in Forth mode with the `> ` prompt. `chat` and `forth` are Forth words (`see chat`, `see forth`) that switch modes. In Chat mode, the prompt is `chat> ` and each submitted buffer is sent directly to the current AI session without an `ai:` prefix; `forth` switches back to the `> ` prompt. Multiline editing and submission work the same in both modes; `bye` and Ctrl-D exit the REPL.
- `ai: <prompt>` sends the complete submitted input buffer after `ai:` and streams the reply in the terminal. The buffer may contain multiple lines.
- `(ai) ( prompt-string stream? -- [response-string] )` runs one AI turn. Use `false` to push the reply as a string, for example: `s" Give me a short greeting" false (ai) . cr`; use `true` to stream the reply to the terminal. `ai:` is the convenient streaming form.
- `ai-status` displays the session selected by this running `f` process, if any. Each new `f` starts without an active session.
- `ai-sessions` fetches the remote session list, newest first, refreshes `.ai_session.json` with the current full session IDs while preserving titles, and assigns sequence numbers for management words. It shows a local title when one is set, the final 8 characters of the session ID, and the API's creation and last-active times. The displayed sequence is a snapshot; run this again to refresh it.
- `n ai-session` retrieves and displays status, model, environment, timestamps, and token usage for a listed session.
- `n ai-use` selects a listed remote session for this `f` process only, so subsequent `ai:` prompts continue that conversation. You can also run `s" <last-8-characters>" ai-use` or `s" <full-session-ID>" ai-use` directly; this looks up the remote session without requiring a prior `ai-sessions`. Other running instances are unaffected.
- `ai-context n count` returns user/assistant text for the latest `count` user-initiated turns; mode defaults to `chat`. `ai-context n count chat` is equivalent, while `ai-context n count json` returns all API items, including tool calls and results, within those turns. The API is queried newest-first and pagination stops once it has found the requested number of turns. Both forms leave the object on the Forth data stack; use `stringify .` to print it. `count` must be positive. Run `ai-sessions` first to refresh the sequence numbers.
- `ai-new` clears this process's active selection. The next `ai:` request creates a new Agents API session with no hosted sandbox; old sessions remain in the remote list.
- `ai-containers` inspects hosted environments linked to sessions in the latest `ai-sessions` snapshot. It shows environment IDs, session IDs, size, and reported status. This is not a billing meter.
- `n ai-container` shows details for an environment from the latest `ai-containers` list.
- `n ai-cleanup` asks for the exact confirmation `delete`, then removes that remote session and conversation. If it has an old hosted sandbox, deletion requests sandbox cleanup; physical cleanup may continue asynchronously. This cannot be undone. Refresh lists before another numbered operation.
- `ai-cancel` sends the Agents API cancellation event for an active turn. At the local approval prompt, `cancel` or `ai-cancel` also closes the paused VM task.

The ignored file `py/.ai_session.json` is a local index and title overlay. Every `ai-sessions` call and REPL exit replaces its session list with the current remote IDs, preserving each matching title and setting new titles to an empty string. The file does not store active sessions or timestamps. Example: `{"sessions":[{"id":"full-remote-session-id","title":"Project K design"}]}`. Edit titles directly in this file; the full ID matches a remote session, while CLI output shows only its final 8 characters. Session creation and last-active times come from the API and are displayed only. Legacy fields such as `active_session_id` are ignored and removed on refresh. The update is written atomically to prevent partial JSON; if multiple processes update concurrently, the last completed write wins. Sessions do not restore the local VM's stack, dictionary, or files. Run `ai-sessions` before numbered session words and `ai-containers` before `n ai-container`.

### Session state decision

Multiple `f` processes previously shared one saved active session ID. One process could change another process's next AI destination, and every turn rewrote a common JSON file, creating avoidable write collisions. Each process now keeps its explicit `ai-use` selection in its own VM memory; a new process never resumes automatically. The shared JSON file is refreshed when `ai-sessions` is run and when the REPL exits; it stores the current remote IDs and editable titles, never active selection or timestamps. Cloud `created_at` and `last_active_at` remain authoritative for time display. Atomic replacement prevents a partially written file; simultaneous refreshes or manual edits can still have a last-writer-wins conflict, and separate-device edits can conflict through OneDrive sync. On exit, the REPL prints the selected session's short ID and a directly runnable `s" <full-ID>" ai-use` command so numeric ID suffixes also work.

## Local Forth tools and confirmation

The agent can search the active VM's Forth dictionary. To run a program, it must request `projectk_run_forth`. The REPL refreshes the session's pending actions before displaying the proposal, then checks again before execution. It displays the complete Forth source and its stated purpose. At each approval prompt, `trust` executes the proposal and automatically approves later AI programs for the lifetime of the current Forth process; `yes` executes only this proposal; `no` declines this proposal; and `cancel` cancels this AI task. Run `ai-confirm` to restore per-proposal approval. Trust is held only in memory and resets when the Forth process exits. If an API result submission fails after local execution, the error reports that the Forth program already ran; inspect the VM before retrying.

Network requests currently run synchronously in the REPL. While the agent is waiting for an API response, the REPL cannot yet accept and queue new input; queueing is available while the local execution confirmation is open.

Approved source runs in the current local VM and can use Project K's Python host bridges. Review it for file, process, and other machine side effects. The bridge returns the actual status, standard output, standard error, and resulting data stack to the agent. Cancellation closes the local task; already completed side effects are not undone.

## Troubleshooting

- **Missing API key:** Add `OPENAI_API_KEY` to `py/.env` or the process environment, then restart the REPL.
- **Invalid key, model, or API access:** Read the Agents API error printed by the REPL; check the Platform project, model access, and API billing/limits.
- **Skill not found:** Ensure `PROJECTK_AI_SKILLS_DIR` points to a directory containing `projectk-forth/SKILL.md`.
- **Skill changes do not take effect:** Use `ai-new` and make another request to create a session with fresh instructions.
- **Choose a prior conversation:** Run `ai-sessions`, then select the intended entry with `n ai-use` in this `f` process.
- **Remove a session and request hosted sandbox cleanup:** Run `ai-sessions`, then `n ai-cleanup` and type `delete` only if you intend to permanently remove that session and its conversation.
- **Network interrupted:** The bridge reports a connection or stream error. Retry the prompt; if the turn's state is unclear, use `ai-status` and `ai-new` to deliberately start a fresh conversation.

## API flow

`ai.f` defines the user-facing AI words and owns the turn flow, tool dispatch, local execution approval, session management, conversation formatting, and the AI host-tool words. It imports `ai_tools.py` only where Python-specific operating-system and HTTP helpers are needed. `ai_bridge.py` supplies standard-library Agents API HTTP/SSE transport, API response helpers, session-index file operations, skill loading, and local Forth output capture. New sessions use `environment.type: "none"`; the first prompt is sent during creation, while later turns subscribe before submitting input. The active session lives only in that VM; the shared index is refreshed by `ai-sessions` and on REPL exit. No OpenAI SDK is required. Model token usage is still billed at the selected model's API rates; no OpenAI-hosted sandbox/container is provisioned for new sessions.

`ai-containers` derives the environment list from remote sessions and retrieves each linked hosted environment by ID. The separate environments-list endpoint may require prewarming beta access, so this word does not rely on it and may not show environments no longer linked to a listed session. Environment status does not establish billable usage; use the API usage dashboard for charges.
