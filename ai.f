\ ai.f - AI Extension Vocabulary for Project K
\ Project K 2.1.0

\ --- 1. Install AI Security Guard ---

code (setup-ai)
    import ai
    ai.install_security_guard(vm)
    end-code
(setup-ai)

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

\ --- 4. Core AI Words: (ai), ai:, AI: ---

code (ai-monotonic-time)
    import time
    vm.push(time.monotonic())
    end-code
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
