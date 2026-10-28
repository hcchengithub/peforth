\ Forth-facing AI words and Agent turn control. ai_bridge.py provides transport helpers.

code ai-new
    vm.host.pop("ai_active_session_id", None)
    print("A fresh AI session will be created for this Forth process on its next request.")
    end-code
    // ( -- ) Clear this Forth process's selected AI session.

code (ai-session-details)
    from peforth import ai_bridge
    import urllib.parse

    session_id = vm.pop()
    index = vm.pop()
    detail = ai_bridge._api_get(f"/sessions/{urllib.parse.quote(session_id, safe='')}")
    agent = detail.get("agent") or {}
    usage = detail.get("usage") or {}
    resolved_id = detail.get("id") or session_id
    title = ai_bridge._session_title(resolved_id) or "(untitled)"
    print(f"Session {index}: {title} [{resolved_id}]")
    print(f"Created: {ai_bridge._format_time(detail.get('created_at'))}")
    print(f"Last active: {ai_bridge._format_time(detail.get('last_active_at'))}")
    print(f"Status: {detail.get('status', 'unknown')}")
    print(f"Model: {agent.get('model', 'unknown')}")
    print(f"Usage: input={usage.get('input_tokens', 0)} output={usage.get('output_tokens', 0)} "
          f"total={usage.get('total_tokens', 0)} tokens")
    if detail.get("error"):
        print(f"Error: {detail['error']}")
    end-code
    // ( display-index session-ID -- ) Print complete details for one session.

code ai-status
    from peforth import ai_bridge

    active_id = vm.host.get("ai_active_session_id")
    if not active_id:
        print("Active AI session: none (next request creates a new session)")
    else:
        vm.push("current")
        vm.push(active_id)
        yield from vm.call(vm.tick("(ai-session-details)"))
    end-code
    // ( -- ) Show complete details for the session selected by this Forth process.

code ai-confirm
    vm.host.pop("ai_trusted", None)
    clear_task_trust = vm.host.get("ai_clear_task_trust")
    if callable(clear_task_trust):
        clear_task_trust()
    print("AI Forth programs will require approval again.")
    end-code
    // ( -- ) Revoke Runtime Trust and the current AI Task's Trust.

code ai-trust-runtime
    vm.host["ai_trusted"] = True
    print("AI Forth programs are trusted for this Forth process. Use ai-confirm to revoke.")
    end-code
    // ( -- ) Enable Runtime Trust for this Forth process until ai-confirm or process exit.

code (ai-approve-input)
    from peforth.repl import read_numbered_choice

    proposal = vm.pop()
    if not isinstance(proposal, dict):
        raise RuntimeError("ai-approve expects a proposal mapping.")
    purpose = proposal.get("purpose")
    source = proposal.get("source")
    if not isinstance(purpose, str) or not isinstance(source, str):
        raise RuntimeError("ai-approve proposal requires string purpose and source fields.")

    def terminal_safe(text):
        return "".join(
            char if char in "\n\t" or 32 <= ord(char) != 127 else f"\\x{ord(char):02x}"
            for char in text
        )

    purpose = terminal_safe(purpose)
    source = terminal_safe(source)
    green = "\x1b[38;2;135;215;135m"
    green_bold = "\x1b[1;38;2;135;215;135m"
    deep_green = "\x1b[38;2;0;100;0m"
    red = "\x1b[38;2;205;70;70m"
    dim = "\x1b[2;37m"
    reset = "\x1b[0m"
    computer_use = proposal.get("kind") == "computer_use"
    if computer_use:
        print("\n"
            f"{green_bold}Purpose: {purpose}{reset}\n\n"
            f"{dim}Computer Use operation and complete parameters:{reset}\n"
            f"{deep_green}{source}{reset}\n\n",
            end="",
            flush=True,
        )
        yield from vm.call(vm.tick("nokia"))
        choice = read_numbered_choice(
            "Choose 1-3: ",
            choices=("1", "2", "3"),
            default="2",
            labels={
                "1": "Allow this operation once",
                "2": "Deny this operation",
                "3": "Cancel this AI task",
            },
            styles={"1": green, "2": red, "3": dim},
        )
        decision = {"1": "allow_once", "2": "deny", "3": "cancel"}[choice]
    else:
        print("\n"
            f"{green_bold}Purpose: {purpose}{reset}\n\n"
            f"{dim}Forth action:{reset}\n"
            f"{deep_green}{source}{reset}\n\n",
            end="",
            flush=True,
        )
        yield from vm.call(vm.tick("nokia"))
        choice = read_numbered_choice(
            "Choose 1-4: ",
            default="1",
            labels={
                "1": "Allow Once",
                "2": "Trust this AI task",
                "3": "Deny this proposal",
                "4": "Cancel this AI task",
            },
            styles={"1": green, "2": green, "3": red, "4": dim},
        )
        decision = {
            "1": "allow_once",
            "2": "trust_task",
            "3": "deny",
            "4": "cancel",
        }[choice]
    vm.push(decision)
    end-code
    // ( proposal -- decision ) Display the appropriate AI approval prompt.
    /// Proposal mapping requires string fields purpose and source.
    /// proposal.kind chooses the flow: approval (or missing/unknown) uses the Forth proposal choices.
    /// Forth proposals offer Allow Once, Trust this AI task, Deny, or Cancel.
    /// computer_use displays exact pane operation parameters and offers Allow this operation once, Deny, or Cancel.
    /// Task Trust and Runtime Trust never approve computer_use proposals.

: ai-approve ( proposal -- decision )
    (ai-approve-input)
    ;
    // ( proposal -- decision ) Compatibility alias for ai-approve.
    /// Example: {'kind': 'computer_use', 'purpose': 'Computer Use: run on pane w2:p4', 'source': '{"arguments":"git status --short","includes_enter":true,"operation":"run","pane_id":"w2:p4"}'}

: computer-use-approve ( proposal -- decision )
    ai-approve
    ;

code chat
    from peforth import ai_bridge

    ai_bridge.set_repl_mode(vm, "chat", reason="forth_word")
    end-code
    // ( -- ) Switch the REPL to direct AI chat input.
    /// In Chat mode, the prompt is chat>; each submitted buffer is sent to the active AI session.

code forth
    from peforth import ai_bridge

    ai_bridge.set_repl_mode(vm, "forth", reason="forth_word")
    end-code
    // ( -- ) Switch the REPL to Forth input.
    /// In Forth mode, the prompt is > and submitted buffers are evaluated as Forth source.

: system_info
    py> system_info
    ;
    // ( -- info ) Return the startup System Info prepared by the Python runtime.

code list-skills
    from peforth import ai_bridge

    skills_root = ai_bridge._source_skills_dir()
    if not skills_root.is_absolute():
        skills_root = (ai_bridge.RUNTIME_ROOT / skills_root).resolve()

    skill_names = []
    for entry in sorted(skills_root.iterdir()):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue
        skill_names.append(entry.name)
        text = skill_file.read_text(encoding="utf-8")
        match = ai_bridge.re.match(r"\A---\s*\n.*?\n---\s*(?:\n|$)", text,
                                  flags=ai_bridge.re.S)
        if match:
            print(f"## {entry.name}\n{match.group(0).rstrip()}\n")
        else:
            print(f"## {entry.name}\n(no YAML header)\n")
    vm.push(chr(32).join(skill_names))
    end-code
    // ( -- names-string ) Print each skill's YAML header and push sorted names separated by spaces.

: initial-ai-model
    system_info :> ["config"] :> ["PEFORTH_AI_MODEL"]
    dup 0= if drop s" gpt-6-luna" then ;
initial-ai-model value aiModel
    // ( -- model-name ) Current AI model. Change with: s" model-name" to aiModel.

code (ai-tool-error)
    message = vm.pop()
    vm.push({"exit_code": None, "stdout": "", "stderr": "", "timed_out": False,
             "truncated": False, "error": str(message)})
    end-code
    // ( message -- result ) Build a normalized local tool error result.

code run_pwsh
    from peforth import ai_tools

    script = vm.pop()
    if not isinstance(script, str):
        vm.push("run_pwsh expects a script string.")
        yield from vm.call(vm.tick("(ai-tool-error)"))
        return
    yield from vm.call(vm.tick("system_info"))
    pwsh = vm.pop()["shells"]["pwsh"]
    if not pwsh.get("available"):
        vm.push("PowerShell 7 (pwsh) is not available in this environment.")
        yield from vm.call(vm.tick("(ai-tool-error)"))
        return
    vm.push(ai_tools._run_process(
        [pwsh["path"], "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "-"],
        input_text=script))
    end-code
    // ( script-string -- result ) Run a PowerShell 7 script without profiles.
    /// Returns exit_code, stdout, stderr, timed_out, truncated, and optional error details. Runs locally with the current user's permissions.

code run_bash
    from peforth import ai_tools

    script = vm.pop()
    if not isinstance(script, str):
        vm.push("run_bash expects a script string.")
        yield from vm.call(vm.tick("(ai-tool-error)"))
        return
    yield from vm.call(vm.tick("system_info"))
    info = vm.pop()
    if info["os"] == "Windows":
        wsl = info["wsl"]
        if not wsl.get("available") or not wsl.get("path") or not wsl.get("distro"):
            vm.push("WSL with an Ubuntu distribution is not available.")
            yield from vm.call(vm.tick("(ai-tool-error)"))
            return
        argv = [wsl["path"], "-d", wsl["distro"], "--exec", "bash", "--noprofile", "--norc", "-s"]
    else:
        bash = info["shells"]["bash"]
        if not bash.get("available") or not bash.get("path"):
            vm.push("Bash is not available in this environment.")
            yield from vm.call(vm.tick("(ai-tool-error)"))
            return
        argv = [bash["path"], "--noprofile", "--norc", "-s"]
    vm.push(ai_tools._run_process(argv, input_text=script))
    end-code
    // ( script-string -- result ) Run Bash natively or through the configured Ubuntu WSL distro.
    /// Returns exit_code, stdout, stderr, timed_out, truncated, and optional error details.

code run_curl
    from peforth import ai_tools

    arguments = vm.pop()
    if not isinstance(arguments, (list, tuple)) or not all(isinstance(item, str) for item in arguments):
        vm.push("run_curl expects a list of curl argument strings, including the URL.")
        yield from vm.call(vm.tick("(ai-tool-error)"))
        return
    yield from vm.call(vm.tick("system_info"))
    curl = vm.pop()["shells"]["curl"]
    if not curl.get("available") or not curl.get("path"):
        vm.push("curl is not available in this environment.")
        yield from vm.call(vm.tick("(ai-tool-error)"))
        return
    vm.push(ai_tools._run_process([curl["path"], *arguments]))
    end-code
    // ( argument-list -- result ) Run curl with arguments passed directly, without shell parsing.
    /// Include the URL. Returns exit_code, stdout, stderr, timed_out, truncated, and optional error details.

code run_http
    from peforth import ai_tools
    import urllib.parse

    request = vm.pop()
    if not isinstance(request, dict):
        vm.push({"error": "run_http expects a request mapping with a url field."})
        return
    url = request.get("url")
    if not isinstance(url, str):
        vm.push({"error": "run_http request url must be a string."})
        return
    try:
        parsed = urllib.parse.urlsplit(url)
    except ValueError as exc:
        vm.push({"error": str(exc)})
        return
    if parsed.scheme.casefold() not in ("http", "https") or not parsed.netloc:
        vm.push({"error": "run_http only supports absolute http:// or https:// URLs."})
        return
    method = request.get("method", "GET")
    headers = request.get("headers", {})
    body = request.get("body")
    if not isinstance(method, str) or not method:
        vm.push({"error": "run_http method must be a nonempty string."})
        return
    if not isinstance(headers, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in headers.items()
    ):
        vm.push({"error": "run_http headers must be a mapping of strings to strings."})
        return
    if body is not None and not isinstance(body, str):
        vm.push({"error": "run_http body must be a string when provided."})
        return
    vm.push(ai_tools._http_request(url, method.upper(), headers, body))
    end-code
    // ( request-mapping -- response ) Send one HTTP/HTTPS request.
    /// Request fields: url (required), method (default GET), headers (string mapping), and body (optional string).


code herdr-current-pane
    from peforth import ai_tools

    vm.push(ai_tools._herdr_current_pane())
    end-code
    // ( -- pane-id ) Resolve and verify this process's live Herdr pane context.

code herdr-screen-read
    from peforth import ai_tools

    line_count = 80
    if vm.stack and type(vm.stack[-1]) is int:
        line_count = vm.pop()
    pane_id = vm.pop()
    vm.push(ai_tools._herdr_screen_read(pane_id, "visible", line_count))
    end-code
    // ( pane-id [line-count] -- snapshot ) Read visible text; line-count defaults to 80.

code herdr-screen-tail
    from peforth import ai_tools

    line_count = 80
    if vm.stack and type(vm.stack[-1]) is int:
        line_count = vm.pop()
    pane_id = vm.pop()
    vm.push(ai_tools._herdr_screen_read(pane_id, "recent-unwrapped", line_count))
    end-code
    // ( pane-id [line-count] -- snapshot ) Read recent unwrapped output; line-count defaults to 80.

code herdr-screen-send-text
    from peforth import ai_tools

    text = vm.pop()
    pane_id = vm.pop()
    result = yield from ai_tools._herdr_forth_operation(vm, "send_text", pane_id, text)
    vm.push(result)
    end-code
    // ( pane-id text -- result ) Send text only with a live one-time Computer Use permit.

code herdr-screen-send-keys
    from peforth import ai_tools

    keys = vm.pop()
    pane_id = vm.pop()
    result = yield from ai_tools._herdr_forth_operation(vm, "send_keys", pane_id, keys)
    vm.push(result)
    end-code
    // ( pane-id keys -- result ) Send key names. Example: char w2:p4 char ctrl+a -1 slice herdr-screen-send-keys.
    /// Key names are passed through to Herdr CLI; syntax is version-specific, with no fixed peforth key list.
    /// Examples: printable characters, backspace, enter, tab, esc/escape, arrows, f12; modifiers ctrl/shift/alt/cmd/super can combine (ctrl+shift+alt+left).
    /// Named punctuation includes minus, comma, ampersand, plus, and backtick. On the tested Herdr build, backspace works; home/end/delete did not.
    /// These examples are not exhaustive; check herdr pane send-keys --help and do not assume undocumented names.
    /// For two keys: char w2:p4 char ctrl+a char enter -2 slice herdr-screen-send-keys.

code herdr-screen-run
    from peforth import ai_tools

    command = vm.pop()
    pane_id = vm.pop()
    result = yield from ai_tools._herdr_forth_operation(vm, "run", pane_id, command)
    vm.push(result)
    end-code
    // ( pane-id command -- result ) Run a command only with a live one-time Computer Use permit.

code (ai)
    from peforth import ai_bridge
    import json
    import os
    import time

    stream_response = vm.pop()
    api_stream = vm.host.pop("ai_transport_stream_once", True)
    prompt = vm.pop()
    if not isinstance(prompt, str):
        raise RuntimeError("(ai) expects a string on the data stack.")
    if not isinstance(stream_response, bool):
        raise RuntimeError("(ai) expects a Boolean output mode after the prompt string.")
    if not isinstance(api_stream, bool):
        raise RuntimeError("The one-shot API transport mode must be a Boolean.")
    prompt = prompt.strip()
    if not prompt:
        raise RuntimeError("ai: needs a prompt on the same line.")

    from peforth.repl import _print_chat_turn
    _print_chat_turn("user", prompt)

    ai_bridge.load_dotenv()
    tools = [
        {"type": "function", "name": "peforth_search_words",
         "description": "Search the current Forth dictionary and documentation.",
         "parameters": {"type": "object", "properties": {"query": {"type": "string"}},
                        "required": ["query"], "additionalProperties": False}},
        {"type": "function", "name": "peforth_tick_heartbeat",
         "description": "Record a brief self-reported progress milestone in peforth diagnostics. This cannot execute Forth.",
         "parameters": {"type": "object", "properties": {"message": {"type": "string"}},
                        "required": ["message"], "additionalProperties": False}},
        {"type": "function", "name": "peforth_run_forth",
         "description": "Propose Forth source for execution in the user's current local VM. The CLI applies its current approval mode.",
         "parameters": {"type": "object", "properties": {"source": {"type": "string"}, "purpose": {"type": "string"}},
                        "required": ["source", "purpose"], "additionalProperties": False}},
        {"type": "function", "name": "computer_read_screen",
         "description": "Read bounded text from an explicitly identified Herdr terminal pane. Read-only; requires a live Herdr-managed caller.",
         "parameters": {"type": "object", "properties": {
             "pane_id": {"type": "string"},
             "source": {"type": "string", "enum": ["visible", "recent-unwrapped"]},
             "lines": {"type": "integer", "minimum": 1, "maximum": 1000, "description": "Maximum requested lines; requests above 1000 are capped. visible reads the current viewport."}},
             "required": ["pane_id"], "additionalProperties": False}},
        {"type": "function", "name": "computer_operate",
         "description": "Request one Herdr pane operation. Every operation requires a fresh one-time approval, including when Task Trust or Runtime Trust is active.",
         "parameters": {"type": "object", "properties": {
             "operation": {"type": "string", "enum": ["send_text", "send_keys", "run"]},
             "pane_id": {"type": "string"},
             "text": {"type": "string", "minLength": 1, "maxLength": 10000},
             "keys": {"type": "array", "items": {"type": "string", "minLength": 1, "maxLength": 32}, "minItems": 1, "maxItems": 32},
             "command": {"type": "string", "minLength": 1, "maxLength": 10000}},
             "required": ["operation", "pane_id"], "additionalProperties": False}},
    ]
    if vm.host.get("_diagnostic_tick_heartbeat_word") is None:
        tools = [tool for tool in tools if tool["name"] != "peforth_tick_heartbeat"]
    session_id = ai_bridge._saved_session(vm)
    answer = []
    turn_completed = False
    message = {"type": "agent.session.input.message", "input": [{"role": "user", "content": [
        {"type": "input_text", "text": prompt}]}]}
    if session_id:
        diagnostic_turn_id = ai_bridge._diagnostic_start_turn(
            vm, prompt, session_id=session_id,
            terminal_output_stream=stream_response, api_transport_stream=api_stream,
        )
        ai_bridge._diagnostic_update_session(vm, diagnostic_turn_id, session_id)
        diagnostic_context = ai_bridge._diagnostic_context(vm, diagnostic_turn_id)
        if api_stream:
            events = ai_bridge._stream(session_id, message, diagnostic=diagnostic_context)
        else:
            events = ai_bridge._stream(
                session_id, message, diagnostic=diagnostic_context, stream=False
            )
    else:
        yield from vm.call(vm.tick("system_info"))
        runtime_info = vm.pop()
        capability_inventory = {
            "direct_agent_tools": [
                {"name": item["name"], "description": item["description"]}
                for item in tools
            ],
            "live_forth_dictionary_words": sorted(vm.words.keys()),
            "python_execution": {
                "forth_words": [
                    name for name in ("py:", "py::") if name in vm.words
                ],
                "cli_block": "<py> ... </py>",
            },
            "host": {
                "os": runtime_info.get("os"),
                "python": runtime_info.get("python"),
                "venv": runtime_info.get("venv"),
                "wsl": runtime_info.get("wsl"),
                "shells": runtime_info.get("shells"),
                "source_path": runtime_info.get("source_path"),
                "runtime_path": runtime_info.get("runtime_path"),
                "runtime_latest": runtime_info.get("runtime_latest"),
            },
        }
        instructions = (
            ai_bridge._agent_instructions()
            + chr(10) * 2 + "## Runtime capability inventory" + chr(10)
            + json.dumps(capability_inventory, ensure_ascii=False, indent=2)
        )
        if len(instructions.encode("utf-8")) > 100_000:
            raise RuntimeError("peforth runtime capability instructions are too large.")
        payload = {
            "agent": {"model": vm.tick("aiModel").value,
                      "tools": tools, "instructions": instructions},
            "environment": {"type": "none"}, "input": prompt, "stream": api_stream,
        }
        diagnostic_turn_id = ai_bridge._diagnostic_start_turn(
            vm, prompt, instructions=instructions,
            terminal_output_stream=stream_response, api_transport_stream=api_stream,
        )
        diagnostic_context = ai_bridge._diagnostic_context(vm, diagnostic_turn_id)
        try:
            if api_stream:
                events = ai_bridge._create_session(payload, diagnostic=diagnostic_context)
            else:
                events = ai_bridge._create_session(
                    payload, diagnostic=diagnostic_context, stream=False
                )
        except Exception as exc:
            output_status = "partial" if answer else "failed_before_output"
            ai_bridge._diagnostic_finish_turn(
                vm, diagnostic_turn_id, "".join(answer) if answer else None,
                output_status=output_status, status="failed", error=exc,
            )
            raise
    ai_started = False
    ai_line_start = True
    remote_turn_id = None
    chat_box_state = {"open": False}
    if stream_response:
        from peforth.repl import _chat_turn_header, _chat_turn_bottom

    def close_chat_box():
        if not chat_box_state["open"]:
            return
        if not ai_line_start:
            print()
        print(_chat_turn_bottom())
        print()
        chat_box_state["open"] = False


    def reconcile_current_turn():
        if not remote_turn_id:
            return None, False
        status, recovered = ai_bridge._reconcile_stream_turn(
            session_id, remote_turn_id, diagnostic=diagnostic_context
        )
        if status == "completed":
            had_answer = bool(answer)
            if recovered:
                answer[:] = [recovered]
                if stream_response and not had_answer:
                    print()
                    _print_chat_turn("assistant", recovered)
                    print()
            return status, True
        if status in {"failed", "cancelled", "incomplete"}:
            raise RuntimeError(
                f"Agents API turn {remote_turn_id} ended with status {status!r}."
            )
        return status, False

    try:
        for event in events:
            event_turn_id = event.get("turn_id")
            if not event_turn_id and isinstance(event.get("turn"), dict):
                event_turn_id = event["turn"].get("id")
            if isinstance(event_turn_id, str) and event_turn_id:
                remote_turn_id = event_turn_id
            if not session_id:
                session_id = ai_bridge._session_id_from_event(event)
                if session_id:
                    vm.host["ai_active_session_id"] = session_id
                    ai_bridge._diagnostic_update_session(
                        vm, diagnostic_turn_id, session_id, created=True
                    )
            kind = event.get("type", "")
            if kind == "agent.session.turn.output_text.delta":
                text = event.get("delta", "")
                answer.append(text)
                if stream_response:
                    if text and not ai_started:
                        print()
                        if not chat_box_state["open"]:
                            print(_chat_turn_header("assistant"))
                            chat_box_state["open"] = True
                        ai_started = True
                    for part in text.splitlines(keepends=True):
                        if ai_line_start:
                            print("  ", end="")
                        print(part, end="", flush=True)
                        ai_line_start = part.endswith("\n") or part.endswith("\r")
            elif kind == "agent.session.turn.output_text.done":
                final_text = event.get("text", "")
                answer[:] = [final_text]
                if stream_response:
                    if ai_started and not ai_line_start:
                        print()
                    ai_started = False
                    ai_line_start = True
            elif kind == "agent.session.requires_action":
                session_status, actions = ai_bridge._wait_for_current_actions(
                    session_id, diagnostic=diagnostic_context
                )
                if session_status in {"idle", "completed"} and not actions:
                    turn_status, completed = reconcile_current_turn()
                    if completed:
                        ai_bridge._diagnostic_event(
                            diagnostic_context, "required_action_reconciled",
                            payload={"session_status": session_status,
                                     "turn_status": turn_status,
                                     "remote_turn_id": remote_turn_id},
                        )
                        turn_completed = True
                        break
                    ai_bridge._diagnostic_event(
                        diagnostic_context, "required_action_deferred",
                        payload={"status": session_status,
                                 "required_action_count": len(actions),
                                 "remote_turn_id": remote_turn_id,
                                 "latest_turn_status": turn_status},
                    )
                    continue
                if (session_status == "in_progress" or
                        (session_status == "requires_action" and not actions)):
                    ai_bridge._diagnostic_event(
                        diagnostic_context, "required_action_deferred",
                        payload={"status": session_status,
                                 "required_action_count": len(actions)},
                    )
                    continue
                if session_status != "requires_action":
                    raise RuntimeError(
                        f"Agents API signaled required action but session status is {session_status!r}."
                    )
                for action in actions:
                    if isinstance(action.get("turn_id"), str):
                        remote_turn_id = action["turn_id"]
                    name = action.get("name")
                    call_started_ns = time.monotonic_ns()
                    raw_arguments = action.get("arguments", {})
                    raw_arguments_text = (
                        "Computer Use operation parameters omitted from persistent diagnostics."
                        if name == "computer_operate"
                        else (
                            raw_arguments if isinstance(raw_arguments, str)
                            else json.dumps(raw_arguments, ensure_ascii=False, sort_keys=True, default=str)
                        )
                    )
                    raw_arguments_id = ai_bridge._diagnostic_store_content(
                        diagnostic_context, "tool_arguments", raw_arguments_text
                    )
                    ai_bridge._diagnostic_action_event(
                        diagnostic_context, "tool_call_received", action,
                        content_id=raw_arguments_id,
                    )
                    try:
                        arguments = json.loads(raw_arguments) if isinstance(raw_arguments, str) else raw_arguments
                        if not isinstance(arguments, dict):
                            raise TypeError("tool arguments must be a JSON object")
                    except Exception as exc:
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "tool_call_failed", action,
                            error=exc, payload={"stage": "arguments_parse"},
                        )
                        raise
                    parsed_arguments_text = json.dumps(
                        {
                            "operation": arguments.get("operation"),
                            "pane_id": arguments.get("pane_id"),
                            "parameters_omitted": True,
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ) if name == "computer_operate" else json.dumps(
                        arguments, ensure_ascii=False, sort_keys=True, default=str
                    )
                    parsed_arguments_id = ai_bridge._diagnostic_store_content(
                        diagnostic_context, "tool_arguments", parsed_arguments_text
                    )
                    ai_bridge._diagnostic_action_event(
                        diagnostic_context, "tool_call_arguments_parsed", action,
                        content_id=parsed_arguments_id,
                    )
                    ai_bridge._diagnostic_action_event(
                        diagnostic_context, "tool_call_started", action,
                    )
                    if name == "peforth_tick_heartbeat":
                        heartbeat_message = arguments.get("message")
                        if not isinstance(heartbeat_message, str):
                            raise TypeError("heartbeat message must be a string")
                        heartbeat_word = vm.host.get("_diagnostic_tick_heartbeat_word")
                        if heartbeat_word is None:
                            raise RuntimeError("The trusted tickHeartbeat word is unavailable.")
                        heartbeat_context = dict(diagnostic_context or {})
                        heartbeat_context.update({
                            "session_id": session_id,
                            "remote_turn_id": remote_turn_id or action.get("turn_id"),
                            "call_id": action.get("call_id"),
                        })
                        had_previous_context = "_ai_heartbeat_context" in vm.host
                        previous_context = vm.host.get("_ai_heartbeat_context")
                        stack_depth = len(vm.stack)
                        vm.host["_ai_heartbeat_context"] = heartbeat_context
                        vm.push(heartbeat_message)
                        try:
                            yield from vm.call(heartbeat_word)
                            if len(vm.stack) != stack_depth:
                                raise RuntimeError("tickHeartbeat must consume exactly one message and return nothing.")
                        finally:
                            if had_previous_context:
                                vm.host["_ai_heartbeat_context"] = previous_context
                            else:
                                vm.host.pop("_ai_heartbeat_context", None)
                        heartbeat_logged = bool(heartbeat_context.get("_logged", False))
                        tool_result_text = (
                            "Heartbeat recorded."
                            if heartbeat_logged else
                            "Heartbeat received, but diagnostic logging is disabled or unavailable."
                        )
                        tool_result_id = ai_bridge._diagnostic_store_content(
                            diagnostic_context, "tool_result", tool_result_text
                        )
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "tool_call_completed", action,
                            content_id=tool_result_id,
                            elapsed_ms=(time.monotonic_ns() - call_started_ns) / 1_000_000,
                            payload={"heartbeat_logged": heartbeat_logged},
                        )
                        ai_bridge._tool_result(
                            session_id, action, True, tool_result_text,
                            diagnostic=diagnostic_context,
                        )
                    elif name == "peforth_search_words":
                        terms = str(arguments.get("query", "")).casefold().split()
                        matches = []
                        for word_name, word in vm.words.items():
                            help_text = str(getattr(word, "help", "") or "")
                            comment = str(getattr(word, "comment", "") or "")
                            source = str(getattr(word, "source", "") or "")
                            searchable = f"{word_name} {help_text} {comment} {source}".casefold()
                            if all(term in searchable for term in terms):
                                matches.append({"name": word_name, "help": help_text,
                                                "comment": comment, "source": source[:1200],
                                                "immediate": bool(word.immediate)})
                            if len(matches) >= 30:
                                break
                        tool_result_text = json.dumps(matches, ensure_ascii=False)
                        tool_result_id = ai_bridge._diagnostic_store_content(
                            diagnostic_context, "tool_result", tool_result_text
                        )
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "tool_call_completed", action,
                            content_id=tool_result_id,
                            elapsed_ms=(time.monotonic_ns() - call_started_ns) / 1_000_000,
                        )
                        ai_bridge._tool_result(
                            session_id, action, True, tool_result_text,
                            diagnostic=diagnostic_context,
                        )

                    elif name == "computer_read_screen":
                        from peforth import ai_tools

                        pane_id = arguments.get("pane_id")
                        source = arguments.get("source", "visible")
                        line_count = arguments.get("lines", 80)
                        if source not in {"visible", "recent-unwrapped"}:
                            raise ValueError("source must be visible or recent-unwrapped.")
                        if isinstance(line_count, bool) or not isinstance(line_count, int) or line_count < 1:
                            raise ValueError("lines must be a positive integer.")
                        pane_id = ai_tools._herdr_pane_id(pane_id)
                        word_name = "herdr-screen-read" if source == "visible" else "herdr-screen-tail"
                        word = vm.tick(word_name)
                        if word is None:
                            raise RuntimeError(f"The {word_name} Forth word is not defined.")
                        stack_depth = len(vm.stack)
                        vm.push(pane_id)
                        vm.push(line_count)
                        try:
                            yield from vm.call(word)
                            if len(vm.stack) != stack_depth + 1:
                                raise RuntimeError(f"{word_name} must return exactly one snapshot.")
                            snapshot = vm.pop()
                        finally:
                            del vm.stack[stack_depth:]
                        tool_result_text = json.dumps(snapshot, ensure_ascii=False, default=str)
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "tool_call_completed", action,
                            elapsed_ms=(time.monotonic_ns() - call_started_ns) / 1_000_000,
                            payload={
                                "pane_id": pane_id,
                                "source": source,
                                "line_count": snapshot.get("line_count") if isinstance(snapshot, dict) else None,
                                "truncated": snapshot.get("truncated") if isinstance(snapshot, dict) else None,
                                "result_persisted": False,
                            },
                        )
                        ai_bridge._tool_result(
                            session_id, action, True, tool_result_text,
                            diagnostic=diagnostic_context, persist_result=False,
                        )
                    elif name == "computer_operate":
                        from peforth import ai_tools

                        operation = arguments.get("operation")
                        pane_id = ai_tools._herdr_pane_id(arguments.get("pane_id"))
                        operation_fields = {
                            "send_text": ("text", "herdr-screen-send-text"),
                            "send_keys": ("keys", "herdr-screen-send-keys"),
                            "run": ("command", "herdr-screen-run"),
                        }
                        if operation not in operation_fields:
                            raise ValueError("operation must be send_text, send_keys, or run.")
                        argument_key, word_name = operation_fields[operation]
                        if set(arguments) != {"operation", "pane_id", argument_key}:
                            raise ValueError(
                                f"{operation} requires exactly operation, pane_id, and {argument_key}."
                            )
                        operation_arguments = arguments[argument_key]
                        ai_tools._herdr_validate_operation_arguments(operation, operation_arguments)
                        ai_tools._herdr_validate_pane(pane_id)
                        includes_enter = (
                            operation == "run"
                            or (
                                operation == "send_keys"
                                and any("enter" in key.casefold() or "return" in key.casefold()
                                        for key in operation_arguments)
                            )
                        )
                        display = {
                            "pane_id": pane_id,
                            "operation": operation,
                            "includes_enter": includes_enter,
                            argument_key: operation_arguments,
                        }
                        proposal = {
                            "kind": "computer_use",
                            "action": action,
                            "pane_id": pane_id,
                            "operation": operation,
                            "arguments": operation_arguments,
                            "purpose": f"Computer Use: {operation} on pane {pane_id}",
                            "source": json.dumps(display, ensure_ascii=False, sort_keys=True),
                            "diagnostic_context": diagnostic_context,
                        }
                        diagnostic_operation = json.dumps(
                            {
                                "kind": "computer_use",
                                "operation": operation,
                                "pane_id": pane_id,
                                "parameters_omitted": True,
                            },
                            sort_keys=True,
                        )
                        proposal["source_content_id"] = ai_bridge._diagnostic_store_content(
                            diagnostic_context, "computer_use_operation", diagnostic_operation
                        )
                        approval_started_ns = time.monotonic_ns()
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "approval_requested", action,
                            content_id=proposal["source_content_id"],
                            payload={"kind": "computer_use", "operation": operation, "pane_id": pane_id},
                        )
                        proposal["approval_started_ns"] = approval_started_ns
                        vm.host["ai_pending_approval"] = proposal
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "approval_wait_started", action,
                            content_id=proposal["source_content_id"],
                        )
                        yield vm.pause()
                        approved = bool(vm.host.pop("ai_approval_result", False))
                        decision = "allow_once" if approved else "deny"
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "approval_decision_received", action,
                            content_id=proposal["source_content_id"],
                            payload={"decision": decision},
                        )
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "approval_wait_ended", action,
                            content_id=proposal["source_content_id"],
                            elapsed_ms=(time.monotonic_ns() - approval_started_ns) / 1_000_000,
                            payload={"decision": decision},
                        )
                        if approved:
                            status, still_pending = ai_bridge._current_actions(
                                session_id, diagnostic=diagnostic_context
                            )
                            if status != "requires_action" or not any(
                                    pending.get("call_id") == action.get("call_id")
                                    for pending in still_pending):
                                ai_bridge._diagnostic_action_event(
                                    diagnostic_context, "approval_expired", action,
                                    content_id=proposal["source_content_id"],
                                )
                                raise RuntimeError(
                                    "This Computer Use approval expired before execution; "
                                    "the pane operation was not run."
                                )
                            word = vm.tick(word_name)
                            if word is None:
                                raise RuntimeError(f"The {word_name} Forth word is not defined.")
                            try:
                                token = ai_tools._herdr_activate_permit(
                                    vm, operation, pane_id, operation_arguments
                                )
                                stack_depth = len(vm.stack)
                                vm.push(pane_id)
                                vm.push(operation_arguments)
                                try:
                                    yield from vm.call(word)
                                    if len(vm.stack) != stack_depth + 1:
                                        raise RuntimeError(
                                            f"{word_name} must consume its arguments and return one result."
                                        )
                                    operation_result = vm.pop()
                                finally:
                                    del vm.stack[stack_depth:]
                                    ai_tools._herdr_deactivate_permit(vm, token)
                                tool_result_text = json.dumps(
                                    operation_result, ensure_ascii=False, default=str
                                )
                            except Exception as exc:
                                error_text = f"{type(exc).__name__}: {exc}"
                                ai_bridge._diagnostic_action_event(
                                    diagnostic_context, "tool_call_failed", action,
                                    elapsed_ms=(time.monotonic_ns() - call_started_ns) / 1_000_000,
                                    error=RuntimeError("Herdr operation result was unconfirmed."),
                                    payload={
                                        "stage": "herdr_operation",
                                        "approved": True,
                                        "operation": operation,
                                        "pane_id": pane_id,
                                    },
                                )
                                ai_bridge._tool_result(
                                    session_id, action, False,
                                    error=error_text, diagnostic=diagnostic_context,
                                    persist_result=False,
                                )
                            else:
                                ai_bridge._diagnostic_action_event(
                                    diagnostic_context, "tool_call_completed", action,
                                    elapsed_ms=(time.monotonic_ns() - call_started_ns) / 1_000_000,
                                    payload={
                                        "approved": True,
                                        "operation": operation,
                                        "pane_id": pane_id,
                                        "result_persisted": False,
                                    },
                                )
                                ai_bridge._tool_result(
                                    session_id, action, True, tool_result_text,
                                    diagnostic=diagnostic_context, persist_result=False,
                                )
                        else:
                            tool_result_text = "User declined this Computer Use operation."
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context, "tool_call_completed", action,
                                elapsed_ms=(time.monotonic_ns() - call_started_ns) / 1_000_000,
                                payload={"approved": False, "operation": operation, "pane_id": pane_id},
                            )
                            ai_bridge._tool_result(
                                session_id, action, False,
                                error=tool_result_text, diagnostic=diagnostic_context,
                            )
                    elif name == "peforth_run_forth":
                        proposal = {"kind": "approval", "action": action,
                                    "source": str(arguments.get("source", "")),
                                    "purpose": str(arguments.get("purpose", ""))}
                        proposal["source_content_id"] = ai_bridge._diagnostic_store_content(
                            diagnostic_context, "forth_source", proposal["source"]
                        )
                        approval_started_ns = time.monotonic_ns()
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "approval_requested", action,
                            content_id=proposal["source_content_id"],
                            payload={"purpose": proposal["purpose"]},
                        )
                        if vm.host.get("ai_trusted", False):
                            print("\n🤖 AI proposes this Forth program (auto-approved for this Forth run):")
                            print(f"Purpose: {proposal['purpose']}\n---\n{proposal['source']}\n---")
                            approved = True
                            approval_decision = "runtime_trust"
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context, "approval_decision_received", action,
                                content_id=proposal["source_content_id"],
                                payload={"decision": approval_decision},
                            )
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context, "approval_wait_ended", action,
                                content_id=proposal["source_content_id"], elapsed_ms=0,
                                payload={"decision": approval_decision},
                            )
                        else:
                            proposal["diagnostic_context"] = diagnostic_context
                            proposal["approval_started_ns"] = approval_started_ns
                            vm.host["ai_pending_approval"] = proposal
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context, "approval_wait_started", action,
                                content_id=proposal["source_content_id"],
                            )
                            yield vm.pause()
                            approval = vm.host.pop("ai_approval_result", False)
                            if isinstance(approval, str) and approval.casefold() == "trust":
                                vm.host["ai_trusted"] = True
                                approved = True
                                approval_decision = "runtime_trust"
                            else:
                                approved = bool(approval)
                                approval_decision = "approved" if approved else "denied"
                            approval_elapsed_ms = (time.monotonic_ns() - approval_started_ns) / 1_000_000
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context, "approval_decision_received", action,
                                content_id=proposal["source_content_id"],
                                payload={"decision": approval_decision},
                            )
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context, "approval_wait_ended", action,
                                content_id=proposal["source_content_id"],
                                elapsed_ms=approval_elapsed_ms,
                                payload={"decision": approval_decision},
                            )
                        if approved:
                            status, still_pending = ai_bridge._current_actions(
                                session_id, diagnostic=diagnostic_context
                            )
                            if status != "requires_action" or not any(
                                    pending.get("call_id") == action.get("call_id")
                                    for pending in still_pending):
                                ai_bridge._diagnostic_action_event(
                                    diagnostic_context, "approval_expired", action,
                                    content_id=proposal["source_content_id"],
                                )
                                raise RuntimeError(
                                    "This approval request expired before execution. "
                                    "The Forth program was not run; please ask AI to propose it again."
                                )
                            execution_started_ns = time.monotonic_ns()
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context, "forth_execution_started", action,
                                content_id=proposal["source_content_id"],
                            )
                            execution = ai_bridge._run(vm, proposal["source"])
                            execution_result = json.loads(execution)
                            stdout_content_id = ai_bridge._diagnostic_store_content(
                                diagnostic_context, "forth_stdout", execution_result.get("stdout", "")
                            )
                            stderr_content_id = ai_bridge._diagnostic_store_content(
                                diagnostic_context, "forth_stderr", execution_result.get("stderr", "")
                            )
                            stack_snapshot = str(execution_result.get("stack", ""))
                            stack_bytes = stack_snapshot.encode("utf-8")
                            stack_size = len(stack_bytes)
                            stack_truncated = stack_size > 4096
                            if stack_truncated:
                                stack_snapshot = stack_bytes[:4096].decode("utf-8", "ignore")
                            execution_payload = {
                                "task_status": execution_result.get("status"),
                                "stdout_content_id": stdout_content_id,
                                "stderr_content_id": stderr_content_id,
                                "stack_snapshot": stack_snapshot,
                                "stack_truncated": stack_truncated,
                                "stack_original_size": stack_size,
                            }
                            execution_elapsed_ms = (
                                time.monotonic_ns() - execution_started_ns
                            ) / 1_000_000
                            execution_succeeded = execution_result.get("status") != "error"
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context,
                                "forth_execution_completed" if execution_succeeded else "forth_execution_failed",
                                action, elapsed_ms=execution_elapsed_ms,
                                payload=execution_payload,
                                error=(RuntimeError(str(execution_result.get("error")))
                                       if not execution_succeeded else None),
                            )
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context,
                                "tool_call_completed" if execution_succeeded else "tool_call_failed",
                                action, elapsed_ms=(time.monotonic_ns() - call_started_ns) / 1_000_000,
                                payload={"stage": "local_forth_execution"},
                            )
                            try:
                                ai_bridge._tool_result(
                                    session_id, action, True, execution,
                                    diagnostic=diagnostic_context,
                                )
                            except Exception as exc:
                                raise RuntimeError(
                                    "The approved Forth program has already run locally, but the Agents API "
                                    f"did not accept its result: {exc}. Check the local VM/output before retrying. "
                                    f"Execution result: {execution}"
                                ) from None
                        else:
                            ai_bridge._diagnostic_action_event(
                                diagnostic_context, "tool_call_completed", action,
                                elapsed_ms=(time.monotonic_ns() - call_started_ns) / 1_000_000,
                                payload={"approved": False},
                            )
                            ai_bridge._tool_result(
                                session_id, action, False,
                                error="User declined execution.",
                                diagnostic=diagnostic_context,
                            )
                    else:
                        ai_bridge._diagnostic_action_event(
                            diagnostic_context, "tool_call_failed", action,
                            error=RuntimeError(f"Unknown function: {name}"),
                        )
                        ai_bridge._tool_result(
                            session_id, action, False,
                            error=f"Unknown function: {name}",
                            diagnostic=diagnostic_context,
                        )
            elif kind in ("error", "agent.session.failed", "agent.session.environment.failed",
                          "agent.session.turn.failed", "agent.session.turn.cancelled"):
                if kind == "agent.session.turn.cancelled":
                    raise RuntimeError("Agents API turn was cancelled.")
                detail = event.get("error") or event.get("turn", {}).get("error") or event
                raise RuntimeError(f"Agents API {kind}: {detail}")
            elif kind == "agent.session.turn.completed":
                turn_completed = True
                break
    except KeyboardInterrupt as exc:
        try:
            ai_bridge.cancel_turn(vm)
        except Exception:
            pass
        output_status = "partial" if answer else "failed_before_output"
        ai_bridge._diagnostic_finish_turn(
            vm, diagnostic_turn_id, "".join(answer) if answer else None,
            output_status=output_status, status="cancelled", error=exc,
        )
        close_chat_box()
        raise
    except Exception as exc:
        recoverable_sse_timeout = (
            isinstance(exc, RuntimeError)
            and str(exc).startswith("Agents API SSE stream timed out")
        )
        if recoverable_sse_timeout:
            try:
                _, turn_completed = reconcile_current_turn()
            except Exception as reconcile_error:
                exc = reconcile_error
        if not turn_completed:
            output_status = "partial" if answer else "failed_before_output"
            ai_bridge._diagnostic_finish_turn(
                vm, diagnostic_turn_id, "".join(answer) if answer else None,
                output_status=output_status, status="failed", error=exc,
            )
            close_chat_box()
            raise exc
    if not turn_completed and remote_turn_id:
        try:
            turn_status, turn_completed = reconcile_current_turn()
            if not turn_completed:
                raise RuntimeError(
                    f"Agents API SSE ended before turn {remote_turn_id} reached a terminal status "
                    f"(current status: {turn_status!r})."
                )
        except Exception as exc:
            output_status = "partial" if answer else "failed_before_output"
            ai_bridge._diagnostic_finish_turn(
                vm, diagnostic_turn_id, "".join(answer) if answer else None,
                output_status=output_status, status="failed", error=exc,
            )
            close_chat_box()
            raise
    if not session_id:
        error = RuntimeError("Agents API stream ended without returning the new session ID.")
        ai_bridge._diagnostic_finish_turn(
            vm, diagnostic_turn_id, "".join(answer) if answer else None,
            output_status="partial" if answer else "failed_before_output",
            status="failed", error=error,
        )
        close_chat_box()
        raise error
    close_chat_box()
    if turn_completed:
        output_text = "".join(answer)
        output_status = "complete" if output_text else "empty"
        ai_bridge._diagnostic_finish_turn(
            vm, diagnostic_turn_id, output_text if output_text else None,
            output_status=output_status, status="completed",
        )
    else:
        output_status = "partial" if answer else "failed_before_output"
        ai_bridge._diagnostic_finish_turn(
            vm, diagnostic_turn_id, "".join(answer) if answer else None,
            output_status=output_status, status="partial",
        )
    if not stream_response:
        vm.push("".join(answer))
    end-code
    // ( prompt-string stream? -- [response-string] ) Run one AI turn; stream or return its text.
    /// Local Forth tool calls pause for the REPL's Trust/Yes/No/Cancel approval flow.

code (ai-monotonic-time)
    import time
    vm.push(time.monotonic())
    end-code
    /// stream? true prints the reply; false pushes it as a string. This controls terminal output, not HTTP/SSE transport.

: ai: // ( <prompt> -- ) Send the remaining input as a prompt; play Nokia 2 if the completed turn exceeds the configured threshold.
    "" word
    (ai-monotonic-time) >t
    true (ai)
    (ai-monotonic-time) t> -
    [ last literal ] :> nokia2_after_seconds
    > if nokia2 then
    ; immediate
    ' ai: :: nokia2_after_seconds=30
    /// Configure the delay in seconds with: ' ai: :: nokia2_after_seconds=<seconds>
    /// The AI response streams to the terminal. Nokia 2 plays only when turn time exceeds the threshold. Proposed Forth programs pause for approval.
    /// Trust approves later proposals for this Forth process; ai-confirm restores per-proposal approval.

: AI: s" " word true (ai) nokia2 ; immediate // ( <prompt> -- ) Send an AI prompt and play Nokia 2 after successful completion.
    /// Like ai:, but opts into a completion chime. The chime starts asynchronously.

code (ai-sessions)
    from peforth import ai_bridge
    rows = ai_bridge._list_remote_sessions()
    titles = ai_bridge._sync_session_index(rows)
    vm.host["ai_session_rows"] = rows
    vm.host["ai_session_titles"] = titles
    end-code
    // ( -- ) Refresh the session snapshot silently.
    /// Fetches remote sessions, synchronizes the local title index, and updates the VM snapshot.
    /// Stores session rows and titles in vm.host. Prints nothing and leaves the data stack unchanged.

code (ai-sessions-list)
    from peforth import ai_bridge
    rows = vm.host.get("ai_session_rows")
    titles = vm.host.get("ai_session_titles") or {}
    if not rows:
        print("No remote sessions found.")
    else:
        active_id = ai_bridge._saved_session(vm)
        print(f"Remote sessions: {len(rows)} (newest first)")
        for index, row in enumerate(rows, 1):
            session_id = row.get("id") or ""
            title = titles.get(session_id) or "(untitled)"
            marker = " *" if session_id == active_id else ""
            print(f"{index:>3}. {title} [{session_id}]{marker}")
            print(f"     Started: {ai_bridge._format_time(row.get('created_at'))}  "
                  f"Last active: {ai_bridge._format_time(row.get('last_active_at'))}")
            print(f"     {row.get('status', 'unknown')}  "
                  f"{(row.get('agent') or {}).get('model', 'unknown')}")
    end-code
    // ( -- ) Print the session snapshot prepared by (ai-sessions).

: ai-sessions
    (ai-sessions)
    (ai-sessions-list)
    ;
    // ( session-number | full-session-ID -- ) Show remote session details.
    /// Fetches and displays timestamps, status, model, usage, and any API error.
    /// Refreshes the remote list when needed; numeric selectors use its current ordering.

code ai-session
    from peforth import ai_bridge

    selector = vm.pop()
    rows = vm.host.get("ai_session_rows")
    if rows is None or (isinstance(selector, str) and
                        not any(row.get("id") == selector for row in rows)):
        rows = ai_bridge._list_remote_sessions()
        titles = ai_bridge._sync_session_index(rows)
        vm.host["ai_session_rows"] = rows
        vm.host["ai_session_titles"] = titles
    index, row = ai_bridge._resolve_session_selector(rows, selector)
    vm.push(index)
    vm.push(row["id"])
    yield from vm.call(vm.tick("(ai-session-details)"))
    end-code
    // ( session-number | full-session-ID -- ) Show remote session details.

code ai-use
    from peforth import ai_bridge
    import urllib.parse

    choice = vm.pop()
    if isinstance(choice, int) and not isinstance(choice, bool):
        snapshot = vm.host.get("ai_session_rows") or []
        if 1 <= choice <= len(snapshot):
            row = snapshot[choice - 1]
            label = str(choice)
        else:
            matches = [row for row in ai_bridge._list_remote_sessions()
                       if ai_bridge._short_id(row.get("id")) == str(choice)]
            if len(matches) != 1:
                if not matches:
                    raise RuntimeError(f"No session number or ID suffix matches {choice!r}.")
                raise RuntimeError(f"Session ID suffix {choice!r} is ambiguous; use the full ID.")
            row = matches[0]
            label = str(choice)
    elif isinstance(choice, str) and choice:
        matches = [row for row in ai_bridge._list_remote_sessions()
                   if row.get("id") == choice or ai_bridge._short_id(row.get("id")) == choice]
        if len(matches) != 1:
            if not matches:
                raise RuntimeError(f"No remote session matches ID {choice!r}.")
            raise RuntimeError(f"Session ID suffix {choice!r} is ambiguous; use the full ID.")
        row = matches[0]
        label = ai_bridge._short_id(row["id"])
    else:
        raise RuntimeError("ai-use expects a session number or session ID.")
    ai_bridge._api_get(f"/sessions/{urllib.parse.quote(row['id'], safe='')}")
    vm.host["ai_active_session_id"] = row["id"]
    title = ai_bridge._session_title(row["id"]) or "(untitled)"
    print(f"Using session {label}: {title} [{row['id']}]")
    end-code
    // ( session-number | session-ID -- ) Select a remote session for follow-up chat.

code ai-cleanup
    from peforth import ai_bridge
    import urllib.parse
    selector = vm.pop()
    rows = vm.host.get("ai_session_rows")
    if rows is None:
        raise RuntimeError("Run ai-sessions first to refresh the remote list and its sequence numbers.")
    index, row = ai_bridge._resolve_session_selector(rows, selector)
    session_id = row["id"]
    print(f"This permanently deletes session {index}: {session_id} and its conversation.")
    result = ai_bridge._api_delete(f"/sessions/{urllib.parse.quote(session_id, safe='')}")
    if result.get("deleted") is not True:
        raise RuntimeError("Agents API did not confirm session deletion.")
    if vm.host.get("ai_active_session_id") == session_id:
        vm.host.pop("ai_active_session_id", None)
    vm.host.pop("ai_session_rows", None)
    vm.host.pop("ai_session_titles", None)

    print("AI session deleted from the API.")
    end-code
    // ( session-number | session-ID -- ) Delete the selected remote session immediately.
    /// Permanently deletes the selected session and its conversation without prompting.
    /// Run ai-sessions first to refresh the session list. Cached session rows and titles are cleared after deletion.
    /// Example: keep the 20 newest sessions (requires more than 20 sessions):
    ///   (ai-sessions)
    ///   py> len(ai_session_rows) (length) 20 - [for]
    ///       t@ . space 21 ai-cleanup (ai-sessions)
    ///   [next]
    /// [for] runs once for a zero count, so use the example only when there are more than 20 sessions.

code ai-cancel
    from peforth import ai_bridge

    if vm.host.get("ai_pending_approval"):
        ai_bridge.cancel_turn(vm)
        print("Sent an Agents API cancel request.")
    else:
        print("No AI task is waiting for local approval; use cancel at its confirmation prompt.")
    end-code
    // ( -- ) Cancel the active Agents API turn.

code (ai-context)
    from peforth import ai_bridge
    import urllib.parse

    mode = vm.pop()
    if mode not in {None, "json", "chat"}:
        raise RuntimeError("ai-context mode must be json, chat, or None.")
    count = vm.pop()
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise RuntimeError("ai-context count must be a positive integer.")
    index = vm.pop()
    rows = vm.host.get("ai_session_rows")
    if rows is None:
        raise RuntimeError("Run ai-sessions first to refresh the remote list and its sequence numbers.")
    if not isinstance(index, int) or isinstance(index, bool) or index < 1 or index > len(rows):
        raise RuntimeError(f"No item {index}; the current list has {len(rows)} entries.")
    session_id = rows[index - 1]["id"]
    items = []
    after = ""
    limit = min(100, max(2, count * 2))
    user_messages = 0
    while True:
        query = urllib.parse.urlencode({"limit": limit, "order": "desc",
                                        **({"after": after} if after else {})})
        page = ai_bridge._api_get(
            f"/sessions/{urllib.parse.quote(session_id, safe='')}/items?{query}")
        page_items = page.get("data") or []
        items.extend(page_items)
        user_messages += sum(1 for item in page_items
                             if item.get("type") == "message" and item.get("role") == "user")
        if user_messages >= count:
            recent = []
            found = 0
            for item in items:
                recent.append(item)
                if item.get("type") == "message" and item.get("role") == "user":
                    found += 1
                    if found == count:
                        break
            items = list(reversed(recent))
            break
        if not page.get("has_more") or not page.get("last_id") or page["last_id"] == after:
            items.reverse()
            break
        after = page["last_id"]

    if mode == "json":
        vm.push(items)
    else:
        messages = []
        for item in items:
            if item.get("type") != "message" or item.get("role") not in {"user", "assistant"}:
                continue
            parts = []
            for part in item.get("content") or []:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    parts.append(part["text"])
                elif isinstance(part, str):
                    parts.append(part)
            text = "".join(parts).strip()
            if text:
                messages.append({"role": item["role"], "text": text})
        vm.push(messages)
    end-code
    // ( session-number count mode -- object ) Return recent API items or chat messages for a session.
    /// Count is the number of most recent user-initiated chat turns. Mode is "json", "chat", or None.
    /// json returns all API items in those turns; chat and None return user/assistant text messages.

: ai-context BL word int BL word int BL word dup "" = if drop none then (ai-context) ; immediate
    // ( <session-number> <count> [mode] -- object ) Fetch recent context for a listed session.
    /// Count is a positive number of latest user-initiated chat turns. Mode defaults to chat.
    /// Run ai-sessions first. Example: ai-context 1 5 json stringify .
