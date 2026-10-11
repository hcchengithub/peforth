# Project K Python Forth quick reference

Curated from the Project K manuals, live `base.f` and `auxiliary.f` dictionaries, and AI-facing `words`.

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

Project K evaluates each input as a resumable `Task`. A host word can yield `vm.pause()` and later continue with `Task.resume()`. `Task.cancel()` closes a paused continuation, but it does not roll back work already performed. AI function calls therefore use the REPL's explicit approval boundary; cancellation is not an undo operation.

## Python bridge and side effects

`py:` and `py>>` are powerful host bridges, not sandboxes. Depending on the expression, Forth can interact with Python modules, files, processes, and other local resources. The AI CLI runs approved Forth in the active local VM and reports the actual output and resulting data stack. Review the complete proposal before approving it.

## AI words

- `ai-context <n> <count> [json|chat]` reads its arguments from the TIB and returns an object on the data stack. `count` is the positive number of latest user-initiated turns; `chat` is the default and returns user/assistant text messages, while `json` returns all API items, including tool interactions, in those turns. The API is queried newest-first and paginated only until the requested turns are found. Use `stringify .` to display the result. Refresh sequence numbers with `ai-sessions` first.
- `ai: <prompt>` sends the remaining submitted input, including multiple lines, to the current Agents API session.
- `word` reads the next token with a space delimiter; a falsy delimiter (`None`, `""`, `False`, or `0`) consumes the rest of the TIB. `ai:` uses an empty string delimiter with `word` to pass its complete prompt to `(ai)`.
- `ai:` is a Forth colon word in `ai.f`. Use `help ai:` for its prompt and approval behavior, and `see ai:` for its source.
- `(ai) ( prompt-string stream? -- [response-string] )` runs an AI turn. Use `false` to return the reply on the stack, or `true` to stream it. `ai:` uses the streaming mode. Its stack effect and behavior are available through `help (ai)`.
- `ai-status`, `ai-new`, and `ai-confirm` are directly defined in `ai.f` and can be inspected with `see`. `ai-status` shows this process's active session; each new process starts without one, and `ai-use` selects one explicitly. `ai-new` clears only this process's selection; `ai-confirm` restores per-proposal approval.
- AI application behavior and Forth word registration belong in `ai.f`: use colon definitions for Forth composition and `code` words for Python integration. `ai.f` imports `ai_tools.py` for Python-specific process, host-detection, and HTTP operations; the Python modules do not register Forth words.
- `.ai_session.json` is a title overlay with `sessions` entries containing `id` and `title`. `ai-sessions` and REPL exit refresh the session IDs while preserving titles. Session times come from the API. CLI output shortens session IDs to their final 8 characters.
- `stringify ( object -- pretty-string )` is defined directly as a `code` word in `auxiliary.f`; it converts Python values, including dicts, lists, tuples, and scalars, into indented JSON. String input is parsed as JSON or a Python literal when possible; unsupported nested values use repr.
- `system_info ( -- info )` returns cached host, Python version and venv, WSL, pwsh, bash, and curl details. It detects once per VM lifetime and stores the result in that word object's properties.
- `run_pwsh ( script-string -- result )` runs a PowerShell 7 script without profiles.
- `run_bash ( script-string -- result )` runs Bash natively on Linux/WSL or through the configured Ubuntu WSL distro on a Windows host.
- `run_curl ( argument-list -- result )` passes a list of argument strings directly to curl; include the URL.
- `run_http ( request-mapping -- response )` sends an HTTP/HTTPS request using Python urllib.request. Request fields: url (required), method (default GET), headers (optional string mapping), and body (optional string).
- Shell and curl results include `exit_code`, `stdout`, `stderr`, `timed_out`, and `truncated`; process limits are 60 seconds and 64 KiB per output stream. HTTP results include `status_code`, `headers`, `body`, and `truncated`; the response limit is 64 KiB and timeout is 30 seconds.
- Use `py>>` on its own line to push Python list or mapping values for `run_curl` and `run_http`.
- At an execution approval prompt, enter `trust`, `yes`, `no`, or `cancel`. `trust` approves later AI programs for the lifetime of the current Forth process; `yes` approves only the current proposal.
