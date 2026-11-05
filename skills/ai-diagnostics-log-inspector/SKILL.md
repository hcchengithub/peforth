---
name: ai-diagnostics-log-inspector
description: Inspect peforth AI diagnostic SQLite logs across Windows and WSL. Trace runtimes and turns, read user/agent chat, enumerate contents, find repeated instructions, and keep the caller environment separate from the log target.
---

# AI diagnostics log inspector

Use this skill to inspect peforth AI diagnostic databases. The agent using the skill and the database being inspected may be on different operating systems.

## Keep caller and target separate

- The skill's repository location identifies where the instructions are stored. It does not identify which database to inspect.
- Establish the target host and database from the user's request or supplied paths. A WSL agent may inspect a Windows database, and a Windows agent may inspect a WSL database.
- Do not silently substitute the caller's own database for the requested target. If the target is unclear, ask which host/database to inspect.
- Identify the selected runtime and turn explicitly. Do not assume the newest runtime is the target just because it is active.
- If the caller's own activity is logged in the target database, it can appear in broad queries. Exclude the caller runtime when the user wants prior activity, or use a fixed event-ID/time cutoff for a stable view. Report the scope used.
- Use read-only diagnostics and SQLite access. Do not alter, checkpoint, or delete the database or its WAL files.

## Choose an execution route

First inspect the current runtime inventory and live Forth dictionary. Look up the available shell or process words before relying on them. Run local commands through the exposed peforth execution tool and respect its approval result.

On WSL, `system_info.shells.pwsh` reports the Windows PowerShell executable path, its `execution_host`, and whether it was found on `PATH` or configured by environment. It probes `pwsh.exe` directly, then uses `PEFORTH_PWSH_PATH` from `~/.peforth/.env` if detection fails. `run_pwsh` launches the resolved path directly through `subprocess`; do not route it through `run_bash`.

Use a reader native to the database host when possible:

- For a WSL database, use that WSL Python and Linux database path.
- For a Windows database, use Windows Python and the Windows database path. If the caller is in WSL, invoke the Windows Python or PowerShell executable through WSL interop when available.
- Avoid opening an active Windows SQLite database through a WSL `/mnt/<drive>` mount if the native read reports a disk I/O error, especially when WAL/SHM files are present. Switch to a Windows-native reader; do not treat the error as a missing database.
- Convert Windows paths to WSL paths only when a WSL process needs them. Keep the database path and diagnostics-script path independent.
- Do not hard-code a particular user's home directory, virtual environment, or PowerShell installation path.

Windows output passed through WSL can garble non-ASCII text. Set PowerShell console output to UTF-8 and run Python with UTF-8 mode (for example, `-X utf8` and `PYTHONIOENCODING=utf-8`). If nested quoting is fragile, use PowerShell `-EncodedCommand` with UTF-16LE base64 input.

## Find the runtime and turn

Use the diagnostics script with the selected host's Python and paths:

```text
python ai_diagnostics.py <database> list-runtimes
python ai_diagnostics.py <database> runtime-timeline <runtime_id>
python ai_diagnostics.py <database> turn-timeline <turn_id>
python ai_diagnostics.py <database> show-turn <turn_id>
python ai_diagnostics.py <database> export-turn <turn_id>
```

Use the script's `--help` if command syntax differs. Start with `list-runtimes`; compare environment, process ID, start time, and paths. Inspect candidate runtime timelines for events such as `tool_call_received`, then use the event's local `turn_id` for `turn-timeline`, `show-turn`, or `export-turn`. Check other plausible runtimes if the newest one has no matching events.

For a chat transcript, report the turn's `prompt` as the user message and `output` as the agent's final reply. `show-turn` is usually the compact view. `export-turn` includes a timeline and can be large; filter or summarize it instead of forwarding an unbounded event dump.

## Count and list stored contents

Distinguish the entire database's `contents` table from contents linked to one turn. State which count is being reported.

The table stores `content_id`, `content_hash`, `content_type`, `content_text`, `content_size`, and `created_at`. A turn's content IDs can be linked from:

1. `turns.prompt_content_id`, `instructions_content_id`, and `output_content_id`;
2. `timeline.content_id` for events on that turn;
3. nested fields in `timeline.payload_json`, such as `stdout_content_id` and `stderr_content_id`.

To count contents for a turn, collect the distinct IDs from all three sources. Parse each payload JSON recursively and include integer values whose key ends with `content_id`; counting only the direct `content_id` columns can miss stdout/stderr records. Fetch the matching rows from `contents` and report ID, type, size, and a short preview. For a whole-database count, query the table separately and group by `content_type`.

`export-turn` provides prompt, instructions, output, and timeline data, but its `contents` object is not a substitute for fetching every content row referenced by the timeline.

## Find repeated instructions

Instructions can appear as standalone `agent_instructions` content and inside `current_actions_payload` JSON at `agent.instructions`. Extract those strings and compare their full text or SHA-256 hashes. Report:

- how many instruction-bearing records there are;
- which content IDs contain them;
- how many distinct instruction texts exist;
- whether the copies are byte-for-byte identical.

Do not confuse repeated copies with distinct instruction variants. By default, report the size and a short preview for very large instructions or payloads; include full bodies when the user asks for them. Do not dump unrelated API/tool payloads just because they are stored in `contents`.

## Report results

Give the selected target host/database, runtime ID, and turn ID so the scope is clear. Separate the global content-row count from the selected turn's content count. For chat requests, show user and agent messages plainly. For content requests, list IDs, types, sizes, and useful previews, and call out repeated instructions with exact counts.
