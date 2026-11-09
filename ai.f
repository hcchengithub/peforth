\ ai.f - AI Extension Vocabulary for Project K
\ Project K 2.1.0

\ --- 1. Install AI Security Guard ---

<py>
import ai
ai.install_security_guard(vm)
</py>

\ --- 2. Task Approval & Management Words ---

code trust-task
    tasks = vm.host.get('paused_tasks', [])
    task = vm.host.get('pending_ai_task') or (tasks[-1] if tasks else None)
    if task is None:
        raise KernelError('No pending AI task to trust')
    trusted = vm.host.setdefault('trusted_ai_tasks', set())
    trusted.add(task)
    print(f"[Security] Task {id(task):x} is now trusted for this execution.")
    end-code immediate
    // ( -- ) Trust the pending AI task for its remaining lifetime.
    /// Whitelist the task so all subsequent words execute without security review pauses.
    last :: safe=True

code cancel-task
    tasks = vm.host.get('paused_tasks', [])
    task = vm.host.get('pending_ai_task') or (tasks.pop() if tasks else None)
    if task is None:
        raise KernelError('No pending AI task to cancel')
    if task in tasks:
        tasks.remove(task)
    vm.host['pending_ai_task'] = None
    trusted = vm.host.get('trusted_ai_tasks')
    if trusted and task in trusted:
        trusted.remove(task)
    task.cancel()
    print(f"[Security] Task {id(task):x} cancelled.")
    end-code immediate
    // ( -- ) Cancel the pending AI task.
    /// Abort the task and remove it from active and trusted task tracking.
    last :: safe=True

\ --- 3. REPL Mode Switching (chat / forth) ---

code chat
    vm.host["repl_mode"] = "chat"
    print("Switched to chat mode (chat>). Type '/forth' to return to Forth mode.")
    end-code
    // ( -- ) Switch REPL to chat mode (chat>).
    last :: safe=True

code forth
    vm.host["repl_mode"] = "forth"
    print("Switched to Forth mode (>).")
    end-code
    // ( -- ) Switch REPL to Forth mode (>).
    last :: safe=True

code list-skills
    import ai
    names, _ = ai.load_skills_manifest(ai.get_skills_dir(vm))
    vm.push(" ".join(names))
    end-code
    // ( -- names-string ) Return a space-separated list of sorted skill names.
    last :: safe=True


\ --- 3.5 System Info & Shell Execution Primitives ---

code initial-ai-model
    import os
    vm.push(os.environ.get("OPENAI_MODEL") or os.environ.get("PEFORTH_AI_MODEL") or "gpt-6-luna")
    end-code
last :: safe=True

initial-ai-model value aiModel
    // ( -- model-name ) Current AI model. Change with: s" model-name" to aiModel.
last :: safe=True

code (ai-tool-error)
    message = vm.pop()
    vm.push({"exit_code": None, "stdout": "", "stderr": "", "timed_out": False,
             "truncated": False, "error": str(message)})
    end-code
    // ( message -- result ) Build a normalized local tool error result.
    last :: safe=True

code system_info
    import ai
    info = vm.host.get("system_info")
    if not info:
        info = ai.detect_system_info(vm)
        vm.host["system_info"] = info
    vm.push(info)
    end-code
    // ( -- info ) Return host environment snapshot including OS, paths, Python/venv, shells, and peforth config env vars.
    /// Includes cwd, source_path (PEFORTH_SOURCE_PATH repo checkout), runtime_path, runtime_latest, python, venv, shells, wsl, and config (PEFORTH_*, OPENAI_*, HERDR_*).
    last :: safe=True

code run_pwsh
    import ai
    script = vm.pop()
    if not isinstance(script, str):
        vm.push("run_pwsh expects a script string.")
        yield from vm.call(vm.tick("(ai-tool-error)"))
        return
    yield from vm.call(vm.tick("system_info"))
    pwsh = vm.pop()["shells"]["pwsh"]
    if not pwsh.get("available") or not pwsh.get("path"):
        vm.push("PowerShell (pwsh or powershell) is not available in this environment.")
        yield from vm.call(vm.tick("(ai-tool-error)"))
        return
    vm.push(ai._run_process(
        [pwsh["path"], "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "-"],
        input_text=script))
    end-code
    // ( script-string -- result ) Run a PowerShell script without profiles.
    last :: safe=False

code run_bash
    import ai
    script = vm.pop()
    if not isinstance(script, str):
        vm.push("run_bash expects a script string.")
        yield from vm.call(vm.tick("(ai-tool-error)"))
        return
    yield from vm.call(vm.tick("system_info"))
    info = vm.pop()
    if info.get("os") == "Windows":
        wsl = info.get("wsl", {})
        if not wsl.get("available") or not wsl.get("path"):
            vm.push("WSL with an Ubuntu/Linux distribution is not available.")
            yield from vm.call(vm.tick("(ai-tool-error)"))
            return
        distro_args = ["-d", wsl["distro"]] if wsl.get("distro") else []
        argv = [wsl["path"], *distro_args, "--exec", "bash", "--noprofile", "--norc", "-s"]
    else:
        bash = info.get("shells", {}).get("bash", {})
        if not bash.get("available") or not bash.get("path"):
            vm.push("Bash is not available in this environment.")
            yield from vm.call(vm.tick("(ai-tool-error)"))
            return
        argv = [bash["path"], "--noprofile", "--norc", "-s"]
    vm.push(ai._run_process(argv, input_text=script))
    end-code
    // ( script-string -- result ) Run a Bash script.
    last :: safe=False

code run_curl
    import ai
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
    vm.push(ai._run_process([curl["path"], *arguments]))
    end-code
    // ( argument-list -- result ) Run curl with arguments passed directly.
    last :: safe=False

code run_http
    import ai
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
    vm.push(ai._http_request(url, method=method, headers=headers, body=body))
    end-code
    // ( request-mapping -- response ) Send an HTTP/HTTPS request using urllib.
    last :: safe=False


\ --- 4. Core AI Words: (ai), ai:, AI: ---

code (ai-monotonic-time)
    import time
    vm.push(time.monotonic())
    end-code
    // ( -- timestamp ) Push monotonic clock in fractional seconds.
    /// Used for turn elapsed time measurement and nokia2 threshold notification.
    last :: safe=True

code (ai)
    import ai
    stream_response = vm.pop()
    prompt = vm.pop()
    if not isinstance(prompt, str):
        raise KernelError("(ai) expects a prompt string on stack")
    if not isinstance(stream_response, bool):
        raise KernelError("(ai) expects a boolean stream flag on stack")
    yield from ai.ai_turn(vm, prompt, stream_response)
    end-code
    // ( prompt stream? -- [response] ) Core AI turn generator.
    /// Send prompt to AI assistant. If stream? is True, stream reply to stdout.
    /// If stream? is False, push the full reply string onto the data stack.
last :: safe=True

: ai:
    "" word
    (ai-monotonic-time) >t
    true (ai)
    (ai-monotonic-time) t> -
    [ last literal ] :> nokia2_after_seconds
    > if nokia2 then
    ; immediate
    // ( <prompt> -- ) Stream prompt to AI; play nokia2 if duration exceeds nokia2_after_seconds.
' ai: :: nokia2_after_seconds=30
last :: safe=True

: AI:
    "" word true (ai) nokia2
    ; immediate
    // ( <prompt> -- ) Stream prompt to AI and always play nokia2 chime upon completion.
last :: safe=True

\ --- 6. Vision & Desktop Capture Words ---

code desktop-capture
    import ai
    import json
    meta = ai.capture_desktop(vm=vm)
    print(json.dumps(meta, ensure_ascii=False))
    vm.push(meta["path"])
    end-code
    // ( -- path-string ) Capture a DPI-aware live Windows desktop screenshot sized for AI inspection.
    /// Saves a unique JPEG in TEMP, prints capture metadata JSON, and pushes the file path.
    last :: safe=True

code desktop-capture-region
    import ai
    import json
    height = vm.pop()
    width = vm.pop()
    y = vm.pop()
    x = vm.pop()
    meta = ai.capture_desktop(region=(x, y, width, height), vm=vm)
    print(json.dumps(meta, ensure_ascii=False))
    vm.push(meta["path"])
    end-code
    // ( x y width height -- path-string ) Capture a pixel or normalized (0.0..1.0) region of the live Windows desktop.
    /// Saves a unique JPEG in TEMP, prints capture metadata JSON, and pushes the file path.
    last :: safe=True

code ai-image-url
    from urllib.parse import urlsplit
    stream_response = vm.pop()
    image_url = vm.pop()
    prompt = vm.pop()
    if not isinstance(prompt, str):
        raise KernelError("ai-image-url expects prompt text.")
    if not isinstance(image_url, str) or not image_url.strip():
        raise KernelError("ai-image-url expects a non-empty HTTPS URL.")
    image_url = image_url.strip()
    parsed = urlsplit(image_url)
    if parsed.scheme.casefold() != "https" or not parsed.netloc:
        raise KernelError("ai-image-url only accepts absolute HTTPS URLs.")
    if type(stream_response) is not bool:
        raise KernelError("ai-image-url expects a Boolean output mode.")
    vm.host["ai_image_url_once"] = image_url
    vm.host["ai_isolated_session_once"] = True
    vm.push(prompt)
    vm.push(stream_response)
    try:
        yield from vm.call(vm.tick("(ai)"))
    finally:
        vm.host.pop("ai_image_url_once", None)
        vm.host.pop("ai_isolated_session_once", None)
    end-code
    // ( prompt-string image-url-string stream? -- [response-string] ) Send a remote image URL to AI.
    last :: safe=True

code ai-image-file
    import ai
    stream_response = vm.pop()
    file_path = vm.pop()
    prompt = vm.pop()
    if not isinstance(prompt, str):
        raise KernelError("ai-image-file expects prompt text.")
    if not isinstance(file_path, str) or not file_path.strip():
        raise KernelError("ai-image-file expects a valid file path.")
    if type(stream_response) is not bool:
        raise KernelError("ai-image-file expects a Boolean output mode.")
    data_uri = ai.encode_image_file_data_uri(file_path, vm=vm)
    vm.host["ai_image_url_once"] = data_uri
    vm.host["ai_isolated_session_once"] = True
    vm.push(prompt)
    vm.push(stream_response)
    try:
        yield from vm.call(vm.tick("(ai)"))
    finally:
        vm.host.pop("ai_image_url_once", None)
        vm.host.pop("ai_isolated_session_once", None)
    end-code
    // ( prompt-string file-path-string stream? -- [response-string] ) Send a local image file as a Data URI to AI.
    last :: safe=True

code ai-screen
    import ai
    import json
    top = vm.pop()
    if type(top) is bool:
        stream_response = top
        prompt = vm.pop()
    else:
        prompt = top
        stream_response = not bool(vm.host.get("in_ai_task"))
    if not isinstance(prompt, str):
        raise KernelError("ai-screen expects prompt text.")
    meta = ai.capture_desktop(vm=vm)
    print(json.dumps(meta, ensure_ascii=False))
    vm.push(prompt)
    vm.push(meta["path"])
    vm.push(stream_response)
    yield from vm.call(vm.tick("ai-image-file"))
    end-code
    // ( prompt-string [stream?] -- [response-string] ) Capture the live Windows desktop and inspect it with ai-image-file in one step.
    /// Captures full DPI-aware virtual desktop as TEMP JPEG, prints metadata JSON, and passes to vision model.
    last :: safe=True

code ai-screen-region
    import ai
    import json
    top = vm.pop()
    if type(top) is bool:
        stream_response = top
        height = vm.pop()
    else:
        height = top
        stream_response = not bool(vm.host.get("in_ai_task"))
    width = vm.pop()
    y = vm.pop()
    x = vm.pop()
    prompt = vm.pop()
    if not isinstance(prompt, str):
        raise KernelError("ai-screen-region expects prompt text.")
    meta = ai.capture_desktop(region=(x, y, width, height), vm=vm)
    print(json.dumps(meta, ensure_ascii=False))
    vm.push(prompt)
    vm.push(meta["path"])
    vm.push(stream_response)
    yield from vm.call(vm.tick("ai-image-file"))
    end-code
    // ( prompt-string x y width height [stream?] -- [response-string] ) Capture a live desktop region and inspect it with ai-image-file in one step.
    /// Coordinates (x y width height) accept pixel integers or normalized floats (0.0..1.0).
    /// Captures DPI-aware region as TEMP JPEG, prints metadata JSON, and passes to vision model.
    last :: safe=True

\ --- 7. Session Store & Local SQLite Mirror Words ---

code (ai-sessions)
    import ai
    ai.sync_sessions(vm)
    end-code
    // ( -- ) Incrementally synchronize remote sessions into the local SQLite mirror and update the VM snapshot.
    /// Fetches remote session metadata, downloads items only for new or updated sessions, and stores session rows in vm.host.
    /// Prints nothing and leaves the data stack unchanged.
    last :: safe=True

code (ai-sessions-list)
    import ai
    rows = vm.host.get("ai_session_rows")
    if rows is None:
        rows = ai.list_local_sessions(vm)
    if not rows:
        print("No remote sessions found.")
    else:
        active_id = ai._saved_session(vm)
        print(f"Remote sessions: {len(rows)} (newest first)")
        for index, row in enumerate(rows, 1):
            session_id = row.get("id") or row.get("session_id") or ""
            title = (
                row.get("description")
                or ai._session_title(session_id)
                or "(untitled)"
            )
            marker = " *" if session_id == active_id else ""
            model = row.get("model") or (row.get("agent") or {}).get("model") or "unknown"
            print(f"{index:>3}. {title}{marker}")
            print(f"     Started: {ai._format_time(row.get('created_at'))}  "
                  f"Last active: {ai._format_time(row.get('last_active_at'))}")
            print(f"     {row.get('status') or 'unknown'}  {model}\t{session_id}\n")
    end-code
    // ( -- ) Print the session snapshot prepared by (ai-sessions).
    last :: safe=True

: ai-sessions
    (ai-sessions)
    (ai-sessions-list)
    ;
    // ( -- ) Synchronize remote AI sessions into the local SQLite mirror and list them.
    /// Fetches remote session index metadata, performs differential item synchronization, and prints the numbered session list.
    last :: safe=True

code ai-sync
    import ai
    stats = ai.sync_sessions(vm)
    print(
        f"Synced AI sessions: {stats['synced']} updated, "
        f"{stats['skipped']} unchanged, "
        f"{stats['deleted']} marked remote-deleted "
        f"({stats['total']} remote)."
    )
    end-code
    // ( -- ) Incrementally synchronize remote AI sessions into the local SQLite mirror.
    /// Fetches remote session metadata, downloads items only for new or updated sessions, and prints a brief sync summary.
    last :: safe=True

code (ai-session-details)
    import ai
    import urllib.parse

    session_id = vm.pop()
    index = vm.pop()
    detail = ai._api_get(f"/sessions/{urllib.parse.quote(session_id, safe='')}")
    agent = detail.get("agent") or {}
    usage = detail.get("usage") or {}
    resolved_id = detail.get("id") or session_id
    title = ai._session_title(resolved_id) or "(untitled)"
    print(f"Session {index}: {title} [{resolved_id}]")
    print(f"Created: {ai._format_time(detail.get('created_at'))}")
    print(f"Last active: {ai._format_time(detail.get('last_active_at'))}")
    print(f"Status: {detail.get('status', 'unknown')}")
    print(f"Model: {agent.get('model', 'unknown')}")
    print(f"Usage: input={usage.get('input_tokens', 0)} output={usage.get('output_tokens', 0)} "
          f"total={usage.get('total_tokens', 0)} tokens")
    if detail.get("error"):
        print(f"Error: {detail['error']}")
    end-code
    // ( index session_id -- ) Show complete details for the session selected by this Forth process.
    last :: safe=True

code ai-session
    import ai

    selector = vm.pop()
    rows = vm.host.get("ai_session_rows")
    if rows is None or (isinstance(selector, str) and
                        not any((row.get("id") or row.get("session_id")) == selector for row in rows)):
        rows = ai._list_remote_sessions()
        vm.host["ai_session_rows"] = rows
    index, row = ai._resolve_session_selector(rows, selector)
    vm.push(index)
    vm.push(row.get("id") or row.get("session_id"))
    yield from vm.call(vm.tick("(ai-session-details)"))
    end-code
    // ( session-number | full-session-ID -- ) Show remote session details.
    last :: safe=True

code ai-use
    import ai
    import urllib.parse

    choice = vm.pop()
    if isinstance(choice, int) and not isinstance(choice, bool):
        snapshot = vm.host.get("ai_session_rows") or []
        if 1 <= choice <= len(snapshot):
            row = snapshot[choice - 1]
            label = str(choice)
        else:
            matches = [row for row in ai._list_remote_sessions()
                       if ai._short_id(row.get("id")) == str(choice)]
            if len(matches) != 1:
                if not matches:
                    raise RuntimeError(f"No session number or ID suffix matches {choice!r}.")
                raise RuntimeError(f"Session ID suffix {choice!r} is ambiguous; use the full ID.")
            row = matches[0]
            label = str(choice)
    elif isinstance(choice, str) and choice:
        matches = [row for row in ai._list_remote_sessions()
                   if row.get("id") == choice or ai._short_id(row.get("id")) == choice]
        if len(matches) != 1:
            if not matches:
                raise RuntimeError(f"No remote session matches ID {choice!r}.")
            raise RuntimeError(f"Session ID suffix {choice!r} is ambiguous; use the full ID.")
        row = matches[0]
        label = ai._short_id(row["id"])
    else:
        raise RuntimeError("ai-use expects a session number or session ID.")
    ai._api_get(f"/sessions/{urllib.parse.quote(row['id'], safe='')}")
    vm.host["ai_active_session_id"] = row["id"]
    vm.host.pop("ai_local_session_id", None)
    vm.host.pop("ai_messages", None)
    title = ai._session_title(row["id"]) or "(untitled)"
    print(f"Using session {label}: {title} [{row['id']}]")
    end-code
    // ( session-number | session-ID -- ) Select a remote session for follow-up chat in Stateful Agents API mode.
    last :: safe=True

code ai-new
    import ai
    prev_id = vm.host.pop("ai_active_session_id", None) or vm.host.pop("ai_local_session_id", None)
    vm.host.pop("ai_local_session_id", None)
    vm.host.pop("ai_messages", None)
    if prev_id:
        ai._log_event(vm, "ai_session_reset", session_id=prev_id, payload={"previous_session_id": prev_id})
    print("A fresh AI session will be created for this Forth process on its next request.")
    end-code
    // ( -- ) Clear this Forth process's selected AI session and return to local Stateless mode.
    last :: safe=True

code ai-promote
    import ai
    yield from ai.promote_local_session(vm)
    end-code
    // ( -- ) Distill current local conversation, ask for confirmation, and promote to a new remote Agents API session.
    /// Cleans lookup/error noise from vm.host['ai_messages'], previews the distilled context, and creates a remote session on approval.
    last :: safe=False

code ai-status
    import ai
    import os

    active_id = vm.host.get("ai_active_session_id")
    if active_id:
        print("Mode: Stateful (remote Agents API session)")
        vm.push("current")
        vm.push(active_id)
        yield from vm.call(vm.tick("(ai-session-details)"))
        messages = vm.host.get("ai_messages") or []
        user_turns = [m for m in messages if isinstance(m, dict) and m.get("role") == "user"]
        if user_turns:
            print(f"Local turns: {len(user_turns)} user turn(s) active in memory ({len(messages)} messages)")
    else:
        ctx = ai.get_ai_context(vm)
        messages = ctx.get("items") or []
        user_turns = [m for m in messages if isinstance(m, dict) and m.get("role") == "user"]
        if user_turns:
            first_content = user_turns[0].get("content")
            first_text = ""
            if isinstance(first_content, str):
                first_text = first_content
            elif isinstance(first_content, list):
                for part in first_content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        first_text = part.get("text", "")
                        break
            first_sentence = ai.extract_first_sentence(first_text, max_chars=80)
            model = os.environ.get("OPENAI_MODEL", "gpt-6-luna").strip()
            runtime_id = vm.host.get("diagnostic_runtime_id")
            local_id = ctx.get("session_id") or vm.host.get("ai_local_session_id") or ai._ensure_local_session_id(vm)
            print(f"Active AI session: local (in-memory) [{local_id}]")
            print("Mode: Stateless (/chat/completions; use 'ai-promote' to promote to a remote session)")
            if first_sentence:
                print(f"Topic: {first_sentence}")
            print(f"Model: {model}")
            print(f"Turns: {len(user_turns)} user turn(s) ({len(messages)} messages in context)")
            if runtime_id:
                print(f"Runtime: {runtime_id}")
        else:
            print("Active AI session: none (next request starts a fresh local conversation)")
    end-code
    // ( -- ) Show complete details for the session selected by this Forth process.
    last :: safe=True

code ai-cleanup
    import ai
    import urllib.parse
    selector = vm.pop()
    rows = vm.host.get("ai_session_rows")
    if rows is None:
        raise RuntimeError("Run ai-sessions first to refresh the remote list and its sequence numbers.")
    index, row = ai._resolve_session_selector(rows, selector)
    session_id = row.get("id") or row.get("session_id")
    print(f"This permanently deletes session {index}: {session_id} and its conversation.")
    result = ai._api_delete(f"/sessions/{urllib.parse.quote(session_id, safe='')}")
    if result.get("deleted") is not True:
        raise RuntimeError("Agents API did not confirm session deletion.")
    db_path = ai._session_db_path()
    if db_path.is_file():
        with ai._open_session_store() as store:
            store.mark_remote_deleted(session_id, True)
    if vm.host.get("ai_active_session_id") == session_id:
        vm.host.pop("ai_active_session_id", None)
    vm.host.pop("ai_session_rows", None)

    print("AI session deleted from the API.")
    end-code
    // ( session-number | session-ID -- ) Delete the selected remote session immediately.
    /// Permanently deletes the selected session from the remote API without prompting, and marks it remote_deleted in the local SQLite mirror.
    /// Run ai-sessions first to refresh the session list. Cached session rows are cleared after deletion.
    last :: safe=False

code ai-export-session
    import ai

    if not vm.dstack:
        raise RuntimeError("ai-export-session expects a session number or session ID.")
    top = vm.pop()
    output_path = None
    if (
        isinstance(top, str)
        and vm.dstack
        and (top.endswith(".json") or "/" in top or "\\" in top)
        and isinstance(vm.peek(), (int, str))
        and not isinstance(vm.peek(), bool)
    ):
        output_path = top
        selector = vm.pop()
    else:
        selector = top
    exported = ai.export_session_json(selector, output_path, vm=vm)
    print(f"Exported session to {exported}")
    end-code
    // ( session-number | session-ID [output-path] -- ) Export a session's items from the local SQLite mirror to a JSON file.
    /// Reconstructs the full JSON array of session items in ascending sequence order (default: ai-session-full-YYYYMMDD-HHMMSS.json).
    last :: safe=True

code ai-search
    import ai

    if vm.dstack and isinstance(vm.peek(), str):
        query = vm.pop().strip()
    elif vm.input is not None and vm.input.remaining.strip():
        query = (
            vm.input.read(until=chr(10))
            if chr(10) in vm.input.remaining
            else vm.input.rest()
        ).strip()
    else:
        raise RuntimeError("ai-search expects a search query string.")
    if not query:
        raise RuntimeError("ai-search expects a non-empty search query.")
    results = ai.search_local_sessions(query)
    if not results:
        print(f"No local sessions matched {query!r}.")
    else:
        print(f"Matched {len(results)} local session(s) for {query!r}:")
        for index, row in enumerate(results, 1):
            session_id = row.get("id") or row.get("session_id") or ""
            title = row.get("description") or "(untitled)"
            deleted_tag = " [remote-deleted]" if row.get("remote_deleted") else ""
            print(f"{index:>3}. {title} [{session_id}]{deleted_tag}")
            for snippet in row.get("matches") or []:
                print(f"     {snippet}")
    end-code
    // ( "query" | <query> -- ) Search session descriptions and item contents in the local SQLite mirror.
    last :: safe=True

code ai-cancel
    # Cancel pending AI task if any
    tasks = vm.host.get('paused_tasks', [])
    task = vm.host.get('pending_ai_task') or (tasks.pop() if tasks else None)
    if task:
        if task in tasks:
            tasks.remove(task)
        vm.host['pending_ai_task'] = None
        task.cancel()
        print("Cancelled pending AI task.")
    else:
        print("No active AI task to cancel.")
    end-code
    // ( -- ) Cancel active AI task.
    last :: safe=True

code (ai-context)
    import ai
    vm.push(ai.get_ai_context(vm))
    end-code
    // ( -- dict ) Push the current AI session context dict.
    /// In Stateful mode, checks freshness, syncs with remote if needed, and returns ordered raw items from local mirror.
    /// In Stateless mode, returns the active in-memory messages list.
    last :: safe=True

: ai-context
    (ai-context)
    ;
    // ( -- dict ) Push the current AI session context dict.
    /// In Stateful mode, checks freshness, syncs with remote if needed, and returns ordered raw items from local mirror.
    /// In Stateless mode, returns the active in-memory messages list.
    last :: safe=True

