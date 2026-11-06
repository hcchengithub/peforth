# peforth v2 Python Forth quick reference

Curated from the peforth manuals, live `base.f` and `auxiliary.f` dictionaries, and AI-facing `words`.

## Input and definitions

- Enter a word or number at the REPL prompt; values are pushed onto the data stack.
- `: square dup * ;` defines a colon word. `12 square` leaves 144 on the stack.
- `words` lists available names; `words <terms>` filters names. `help <terms>` searches word help and comments. `see <name>` displays documentation and a word definition.
- `code <name> ... end-code` defines a Python-host word. Python names used in that code come from the VM host environment.
- `s" text"` pushes a string. `(ai)` takes a prompt and a stream flag; use `false` to push the AI response or `true` to stream it to the terminal.
- Python value words: `true`/`True`, `false`/`False`, `none`/`None`, and `""` push `True`, `False`, `None`, and an empty string. `inf`/`infinity`, `-inf`/`-infinity`, and `nan` push Python floating-point special values.
- `int ( value -- integer )` and `float ( value -- float )` convert the top stack value with Python's built-in conversions.
- `' word alias Name` defines `Name` as an alias of `word`; `alias` preserves the original word's behavior and help text.
- `last ( -- word )` pushes the most recently defined word; `execute ( word -- ... )` runs a word from the stack. Use `last execute` to run the latest definition.

## VM tasks

peforth evaluates each input as a resumable `Task`. A host word can yield `vm.pause()` and later continue with `Task.resume()`. `Task.cancel()` closes a paused continuation, but it does not roll back work already performed. AI function calls therefore use the REPL's explicit approval boundary; cancellation is not an undo operation.

## Herdr screen and pane words

In peforth, Herdr words provide terminal multi-pane access:
- `herdr-current-pane ( -- pane-id )`: Get current caller pane ID (safe, no approval).
- `herdr-screen-read ( pane-id [lines] -- text )`: Read visible screen text (safe, no approval).
- `herdr-screen-tail ( pane-id [lines] -- text )`: Read recent screen text tail (safe, no approval).
- `herdr-show-pane-id ( -- )`: Show pane IDs in border titles (safe, no approval).
- `herdr-clear-pane-id ( -- )`: Clear custom border titles (safe, no approval).
- `herdr-screen-send-text ( pane-id text -- result )`: Send text to pane (unsafe, triggers approval).
- `herdr-screen-send-keys ( pane-id keys -- result )`: Send keys to pane (unsafe, triggers approval).
- `herdr-screen-run ( pane-id command -- result )`: Run command in pane (unsafe, triggers approval).

Rule: Always use the safe Forth words directly to read or inspect panes. Never use inline Python or bash checks.

## Python bridge and side effects

`<py> ... </py>` is a powerful host bridge, not a sandbox:
- `<py> print('hello world') </py>` executes Python statements directly.
- `<py> x = 123 + 456; vm.push(x) </py>` computes in Python and pushes the result onto the Forth data stack.
- `<py> vm.pop().foo(123) </py>` pops the top stack item and invokes a Python method on it.
- `<py> vm.latest.properties['safe'] = True </py>` sets a property on the most recently defined word.
Depending on the Python code, Forth can interact with Python modules, files, processes, and other local resources. The AI CLI runs approved Forth in the active local VM and reports the actual output and resulting data stack. Review the complete proposal before approving it.

## AI words

- `ai-context <n> <count> [json|chat]` reads its arguments from the TIB and returns an object on the data stack. `count` is the positive number of latest user-initiated turns; `chat` is the default and returns user/assistant text messages, while `json` returns all API items, including tool interactions, in those turns. The API is queried newest-first and paginated only until the requested turns are found. Use `stringify .` to display the result. Refresh sequence numbers with `ai-sessions` first.
- `ai: <prompt>` sends the remaining submitted input, including multiple lines, to `(ai)` in streaming mode.
- `word` reads the next token with a space delimiter; a falsy delimiter (`None`, `""`, `False`, or `0`) consumes the rest of the TIB. `ai:` uses an empty string delimiter with `word` to pass its complete prompt to `(ai)`.
- `ai:` is a Forth colon word in `ai.f`. Use `help ai:` for its prompt and approval behavior, and `see ai:` for its source.
- `(ai) ( prompt-string stream? -- [response-string] )` runs an AI turn. Use `false` to return the reply on the stack, or `true` to stream it. `ai:` uses the streaming mode. By default (`ai_active_session_id` is `None`), `(ai)` runs in Stateless mode via `/chat/completions` using local `vm.host["ai_messages"]`, automatically tagged with a `local_<16-hex>` ID (`vm.host["ai_local_session_id"]`) in `ai-diagnostics.sqlite3`. When a remote session is selected via `ai-use` or created via `ai-promote`, `(ai)` routes turns to the Stateful OpenAI Agents API (`/v1/agents/sessions/{id}/events`).
- `ai-status`, `ai-new`, `ai-promote`, and `ai-confirm` are directly defined in `ai.f` and can be inspected with `see`. `ai-status` shows this process's active session (local Stateless mode with `[local_<16-hex>]` or selected remote Stateful session `[sess_...]`). `ai-promote` distills the current local `ai_messages` conversation (removing lookup and error noise), previews the cleaned transcript for confirmation, promotes it to a new remote Agents API session, and logs `ai_session_promoted` in `ai-diagnostics.sqlite3`. `ai-use` selects a remote session explicitly for Stateful follow-up chat. `ai-new` clears this process's session, logs `ai_session_reset`, and returns to fresh local Stateless mode; `ai-confirm` restores per-proposal approval.
- AI application behavior and Forth word registration belong in `ai.f`: use colon definitions for Forth composition and `code` words for Python integration. `ai.f` imports `ai.py` for transport, security guard, and host operations; the interactive REPL is implemented in `repl.f`. The Python modules do not register Forth words.
- `sessions/sessions.sqlite3` under `PEFORTH_CONFIG_DIR` is a local SQLite mirror of remote sessions and their items. `ai-sessions` and `ai-sync` incrementally synchronize remote sessions into SQLite while preserving session descriptions. `ai-sessions`, `ai-status`, `ai-session`, `ai-use`, `ai-cleanup`, `ai-export-session`, and `ai-search` display full Session IDs. `ai-session`, `ai-cleanup`, and `ai-export-session` accept either a list number or full ID; `ai-use` also keeps unambiguous suffix matching for compatibility.
- `stringify ( object -- pretty-string )` is defined directly as a `code` word in `auxiliary.f`; it converts Python values, including dicts, lists, tuples, and scalars, into indented JSON. String input is parsed as JSON or a Python literal when possible; unsupported nested values use repr.
- `system_info ( -- info )` returns the host and configuration snapshot. It includes Python/venv, WSL, pwsh, bash, curl, and non-secret configuration details; the Forth word returns the VM's bound snapshot.
- `run_pwsh ( script-string -- result )` runs a PowerShell 7 script without profiles.
- `run_bash ( script-string -- result )` runs Bash natively on Linux/WSL or through the configured Ubuntu WSL distro on a Windows host.
- `run_curl ( argument-list -- result )` passes a list of argument strings directly to curl; include the URL.
- `run_http ( request-mapping -- response )` sends an HTTP/HTTPS request using Python urllib.request. Request fields: url (required), method (default GET), headers (optional string mapping), and body (optional string).
- Shell and curl results include `exit_code`, `stdout`, `stderr`, `timed_out`, and `truncated`; process limits are 60 seconds and 64 KiB per output stream. HTTP results include `status_code`, `headers`, `body`, and `truncated`; the response limit is 64 KiB and timeout is 30 seconds.
- Use `<py> vm.push([...]) </py>` or `<py> vm.push({...}) </py>` to push Python list or mapping values onto the stack for `run_curl` and `run_http`.
- At an execution approval prompt, choose `1` (Allow Once), `2` (Trust this AI task), `3` (Deny this proposal), or `4` (Cancel this AI task).
