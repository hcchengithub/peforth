\ repl.f - Interactive Multiline REPL for Project K (v2.1.0)

code repl
    import re
    import sys

    vm.host.pop("exit_requested", None)
    paused_tasks = vm.host.setdefault('paused_tasks', [])
    code_buffer = []

    print("peforth 2.1.0 (with AI support)")
    print("Type 'help' for instructions, 'ai: <prompt>' for AI assistance, 'bye' to exit.")
    if sys.stdin.isatty():
        print("Keys: [Enter] submit, [Ctrl+J] or [Shift+Enter] multiline newline.")

    # Try prompt_toolkit for modern CLI multiline support if connected to an interactive TTY
    pt_session = None
    if sys.stdin.isatty():
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.key_binding import KeyBindings
            from prompt_toolkit.input.ansi_escape_sequences import ANSI_SEQUENCES
            from prompt_toolkit.keys import Keys

            bindings = KeyBindings()

            @bindings.add("c-m")
            def _submit(event):
                event.current_buffer.validate_and_handle()

            @bindings.add("c-j")
            def _newline(event):
                event.current_buffer.insert_text("\n")

            @bindings.add("escape", "c-m")
            def _newline_alt_enter(event):
                event.current_buffer.insert_text("\n")

            # Map Shift+Enter / Ctrl+Enter terminal sequences to ControlJ
            for seq in ("\x1b[27;2;13~", "\x1b[13;2u"):
                ANSI_SEQUENCES[seq] = Keys.ControlJ

            pt_session = PromptSession(
                multiline=True,
                key_bindings=bindings,
                prompt_continuation=lambda width, line_number, is_soft_wrap: "... ",
            )
        except ImportError:
            pt_session = None

    try:
        while True:
            is_continuing = bool(code_buffer) or vm.compiling
            prompt_str = "... " if is_continuing else "forth> "

            try:
                if pt_session:
                    text = pt_session.prompt(prompt_str)
                else:
                    text = input(prompt_str if sys.stdin.isatty() else "")
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n<interrupted>")
                code_buffer.clear()
                if vm.compiling:
                    vm._discard()
                continue

            clean_text = text.replace("\r\n", "\n").replace("\r", "\n").rstrip()
            if not clean_text and not is_continuing:
                continue

            # Check if we are accumulating a host code block
            if code_buffer:
                code_buffer.append(clean_text)
                combined = "\n".join(code_buffer)
                if vm.host_boundary(combined) is not None:
                    code_buffer.clear()
                    clean_text = combined
                else:
                    continue
            elif re.match(r"^\s*code\b", clean_text):
                if vm.host_boundary(clean_text) is None:
                    code_buffer.append(clean_text)
                    continue

            try:
                task = vm.dictate(clean_text)
                if vm.host.get("exit_requested"):
                    break
                if task.status == "paused":
                    if task not in paused_tasks:
                        paused_tasks.append(task)
                    if not vm.host.get("pending_ai_task"):
                        print("Task paused. Type 'resume' to continue.")
            except Exception as error:
                print(f"{type(error).__name__}: {error}")
                code_buffer.clear()
                if vm.compiling:
                    vm._discard()
    except KeyboardInterrupt:
        print()
    finally:
        for t in list(paused_tasks):
            if t.status in ("ready", "paused"):
                t.cancel()
    end-code
    // ( -- ) Start interactive Forth REPL loop.
    /// Run Forth prompt loop (forth>) until bye or EOF.
    last :: safe=True
