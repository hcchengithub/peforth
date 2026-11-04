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

\ --- 3. Core AI Words: (ai) and ai: ---

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
    rest true (ai)
    ; immediate
    // ( <prompt> -- ) Stream prompt to AI assistant.
    /// Read remaining line from input buffer and send to AI with streaming enabled.
