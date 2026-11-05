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
    print("Switched to chat mode (chat>). Type 'forth' to return to Forth mode.")
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
    names, _ = ai.load_all_skills(ai.get_skills_dir(vm))
    vm.push(" ".join(names))
    end-code
    // ( -- names-string ) Return a space-separated list of sorted skill names.
    last :: safe=True


\ --- 3.5 System Info & Shell Execution Primitives ---

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
    // ( -- info ) Return host environment snapshot including OS, Python, and detected shells.
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

: ai:
    rest
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
    rest true (ai) nokia2
    ; immediate
    // ( <prompt> -- ) Stream prompt to AI and always play nokia2 chime upon completion.
last :: safe=True

\ --- 5. Interactive Proposal Approval (ai-approve) ---

code (ai-approve-input)
    import ai

    proposal = vm.pop()
    if not isinstance(proposal, dict):
        raise KernelError("ai-approve expects a proposal mapping.")
    purpose = proposal.get("purpose", "")
    source = proposal.get("source", "")

    green = "\x1b[38;2;135;215;135m"
    green_bold = "\x1b[1;38;2;135;215;135m"
    deep_green = "\x1b[38;2;0;100;0m"
    dim = "\x1b[2;37m"
    reset = "\x1b[0m"

    print(f"\n{green_bold}Purpose: {purpose}{reset}\n")
    print(f"{dim}Forth action:{reset}")
    print(f"{deep_green}{source.strip()}{reset}\n")

    yield from vm.call(vm.tick("nokia"))

    choice = ai.read_numbered_choice(
        "Choose 1-4: ",
        default="1",
        labels={
            "1": "Allow Once",
            "2": "Trust this AI task",
            "3": "Deny this proposal",
            "4": "Cancel this AI task",
        },
        styles={"1": green, "2": green, "3": dim, "4": dim},
    )
    decision = {
        "1": "allow_once",
        "2": "trust_task",
        "3": "deny",
        "4": "cancel",
    }.get(choice, "allow_once")

    vm.push(decision)
    end-code
    // ( proposal -- decision ) Display AI approval prompt and read 1-4 choice.
    last :: safe=True

: ai-approve ( proposal -- decision )
    (ai-approve-input)
    ;
    // ( proposal -- decision ) Interactive approval workflow for AI proposed code.
    last :: safe=True
