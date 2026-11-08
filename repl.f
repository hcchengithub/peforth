\ repl.f - Interactive Multiline REPL for Project K (v2.1.0)

<py>
try:
    from prompt_toolkit.completion import Completer, Completion
    class ForthWordCompleter(Completer):
        def __init__(self, vm_ref):
            self.vm = vm_ref

        def get_completions(self, document, complete_event=None):
            text = document.text_before_cursor
            if not text or text[-1].isspace():
                return
            prefix = text.rsplit(None, 1)[-1]
            has_slash = prefix.startswith("/") and len(prefix) > 1
            search = prefix[1:] if has_slash else prefix
            folded = search.casefold()
            for name in self.vm.words:
                if isinstance(name, str) and name.casefold().startswith(folded):
                    yield Completion(
                        name,
                        start_position=-len(search) if has_slash else -len(prefix),
                        display_meta="← ↑ ↓ → move | Space selects | Esc cancels",
                    )
    vm.host["ForthWordCompleter"] = ForthWordCompleter
except ImportError:
    vm.host["ForthWordCompleter"] = None
</py>

code repl
    import re
    import sys

    vm.host.pop("exit_requested", None)
    paused_tasks = vm.host.setdefault('paused_tasks', [])
    code_buffer = []

    import ai
    runtime_latest = (ai.detect_system_info(vm).get("runtime_latest") or {})
    runtime_modified = runtime_latest.get("modified")
    try:
        from prompt_toolkit.formatted_text import FormattedText
        from prompt_toolkit.shortcuts import print_formatted_text
        from prompt_toolkit.styles import Style
        print_formatted_text(
            FormattedText([("class:greeting.title", "\np e f o r t h   v 2")]),
            style=Style.from_dict({"greeting.title": "bold #5fd7ff"}),
        )
    except Exception:
        print("\np e f o r t h   v 2")
    if isinstance(runtime_modified, str) and runtime_modified:
        print(f"2.1.0 - Runtime modified: {runtime_modified}")
    else:
        print("2.1.0")
    # Keep the rest of the startup guidance in the Forth greeting word.
    vm.dictate("greeting")

    # Try prompt_toolkit for modern CLI multiline & tab completion support if connected to an interactive TTY
    pt_session = None
    if sys.stdin.isatty():
        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.filters import has_completions
            from prompt_toolkit.input.ansi_escape_sequences import ANSI_SEQUENCES
            from prompt_toolkit.key_binding import KeyBindings
            from prompt_toolkit.keys import Keys
            from prompt_toolkit.layout.menus import MultiColumnCompletionMenuControl
            from prompt_toolkit.shortcuts import CompleteStyle
            from prompt_toolkit.styles import Style

            completer_cls = vm.host.get("ForthWordCompleter")
            completer = completer_cls(vm) if completer_cls else None

            repl_style = Style.from_dict({
                "completion-menu.completion.current": "bold fg:#006400 bg:#ffffff noreverse",
                "completion-menu.multi-column-meta": "fg:default bg:default noreverse",
            })

            bindings = KeyBindings()

            @bindings.add("c-m")
            def _submit(event):
                buf = event.current_buffer
                if buf.complete_state is not None:
                    buf.cancel_completion()
                buf.validate_and_handle()

            @bindings.add("c-j")
            def _newline(event):
                buf = event.current_buffer
                if buf.complete_state is not None:
                    buf.cancel_completion()
                buf.insert_text("\n")

            @bindings.add("escape", "c-m")
            def _newline_alt_enter(event):
                buf = event.current_buffer
                if buf.complete_state is not None:
                    buf.cancel_completion()
                buf.insert_text("\n")

            # Map Shift+Enter / Ctrl+Enter terminal sequences to ControlJ
            for seq in ("\x1b[27;2;13~", "\x1b[13;2u"):
                ANSI_SEQUENCES[seq] = Keys.ControlJ

            # --- Tab Completion Controls (Unified for all modes) ---

            @bindings.add("c-i", eager=True)
            def _tab_complete(event):
                buf = event.current_buffer
                if buf.complete_state is None:
                    buf.start_completion(select_first=True)

            def _move_vertical(event, step):
                buf = event.current_buffer
                state = buf.complete_state
                if state is None or state.complete_index is None:
                    return
                rows = 1
                for window in event.app.layout.visible_windows:
                    if isinstance(window.content, MultiColumnCompletionMenuControl):
                        rows = max(1, getattr(window.content, "_rendered_rows", 1))
                        break
                current_idx = state.complete_index
                next_idx = current_idx + step
                if 0 <= next_idx < len(state.completions) and (next_idx // rows == current_idx // rows):
                    buf.go_to_completion(next_idx)

            @bindings.add(Keys.Up, filter=has_completions, eager=True)
            def _prev_completion(event):
                _move_vertical(event, -1)

            @bindings.add(Keys.Down, filter=has_completions, eager=True)
            def _next_completion(event):
                _move_vertical(event, 1)

            @bindings.add(" ", filter=has_completions, eager=True)
            def _accept_completion_with_space(event):
                buf = event.current_buffer
                state = buf.complete_state
                completion = state.current_completion if state is not None else None
                if completion is not None:
                    buf.apply_completion(completion)
                buf.cancel_completion()
                buf.insert_text(" ")

            @bindings.add("escape", filter=has_completions, eager=True)
            def _cancel_completion_esc(event):
                event.current_buffer.cancel_completion()

            @bindings.add("escape", filter=~has_completions)
            def _cancel_input_esc(event):
                buf = event.current_buffer
                if buf.text or code_buffer or vm.compiling:
                    event.app.exit(exception=KeyboardInterrupt)

            @bindings.add("backspace", filter=has_completions, eager=True)
            def _backspace_completion(event):
                buf = event.current_buffer
                buf.cancel_completion()
                buf.delete_before_cursor()

            @bindings.add(Keys.Delete, filter=has_completions, eager=True)
            def _delete_without_completion(event):
                buf = event.current_buffer
                buf.cancel_completion()
                buf.delete()

            @bindings.add(Keys.Any, filter=has_completions)
            def _type_without_completion(event):
                if event.data == " ":
                    _accept_completion_with_space(event)
                    return
                buf = event.current_buffer
                buf.cancel_completion()
                if event.data and event.data.isprintable():
                    buf.insert_text(event.data)

            pt_session = PromptSession(
                multiline=True,
                key_bindings=bindings,
                completer=completer,
                complete_while_typing=False,
                complete_style=CompleteStyle.MULTI_COLUMN,
                style=repl_style,
                prompt_continuation=lambda width, line_number, is_soft_wrap: (
                    "  " if vm.host.get("repl_mode", "forth") == "chat" else "... "
                ),
            )


        except Exception:
            pt_session = None


    try:
        while True:
            is_continuing = bool(code_buffer) or vm.compiling
            mode = vm.host.get("repl_mode", "forth")
            if is_continuing:
                prompt_str = "... "
            elif mode == "chat":
                prompt_str = "chat> "
            else:
                prompt_str = "> "

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
                import ai
                monitor_ctx = ai.TaskInterruptMonitor(vm)
            except Exception:
                import contextlib
                monitor_ctx = contextlib.nullcontext()

            try:
                with monitor_ctx:
                    if mode == "chat" and not is_continuing:
                        if clean_text.startswith("/"):
                            task = vm.dictate(clean_text[1:])
                        else:
                            task = vm.dictate(f"ai: {clean_text}")
                    else:
                        task = vm.dictate(clean_text)
                if vm.host.get("exit_requested"):
                    break
                if task.status == "paused":
                    if task not in paused_tasks:
                        paused_tasks.append(task)
                    if not vm.host.get("pending_ai_task"):
                        print("Task paused. Type 'resume' to continue.")
            except KeyboardInterrupt:
                print("\n<interrupted>")
                code_buffer.clear()
                if vm.compiling:
                    vm._discard()
                continue
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

code ?cli
    import os
    import sys

    if vm.host.get("headless", False):
        return

    args = list(vm.host.get("argv", []))

    def _print_cli_help(file=None):
        print("""Usage: f [-h] [-i] [-id <session-id>] [-l, --load <path>]... [-e <Forth tokens...> | -c <prompt tokens...>]

Run peforth Forth source or start the interactive REPL.

Options:
  -h, --help         Show this help message and exit
  -i, --interactive  Enter the REPL after executing source or completing chat
  -id <session-id>   Continue the conversation in this session
  -l, --load <path>  Include a Forth source file (may be repeated; before -e or -c)
  -e <tokens...>     Execute all remaining command-line tokens as one TIB,
                     joined with one space between tokens
                     Example: f -e run-monitor
  -c <tokens...>     Submit all remaining command-line tokens as an AI prompt

Each -c run writes SESSION_ID=<session-id> to stderr after completion.

With no source argument, the REPL starts. Loaded files run in order before -e
or -c. Put -i before -e or -c when you want to continue interactively; all
tokens after -e or -c belong to that Forth input or AI prompt.""", file=file)

    if not args:
        yield from vm.call(vm.tick("repl"))
        return

    interactive = False
    source = None
    chat_prompt = None
    session_id = None
    load_files = []
    index = 0

    while index < len(args):
        arg = args[index]
        if arg in ("-h", "--help"):
            _print_cli_help()
            return
        if arg in ("-i", "--interactive"):
            interactive = True
            index += 1
            continue
        if arg == "-id":
            if session_id is not None:
                print("Error: -id may be specified only once.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                sys.exit(2)
            if index + 1 >= len(args) or not args[index + 1] or args[index + 1].startswith("-"):
                print("Error: -id requires a session ID before -c.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                sys.exit(2)
            session_id = args[index + 1]
            index += 2
            continue
        if arg in ("-l", "--load"):
            if index + 1 >= len(args) or not args[index + 1] or args[index + 1].startswith("-"):
                print(f"Error: {arg} requires a source file path.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                sys.exit(2)
            load_files.append(args[index + 1])
            index += 2
            continue
        if arg in ("-e", "--execute"):
            source = " ".join(args[index + 1:])
            if not source:
                print("Error: -e requires Forth input.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                sys.exit(2)
            index = len(args)
            break
        if arg in ("-c", "--chat"):
            chat_prompt = " ".join(args[index + 1:])
            if not chat_prompt:
                print("Error: -c requires an AI prompt.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                sys.exit(2)
            index = len(args)
            break
        if arg.startswith("-"):
            print(f"Unknown option: {arg}", file=sys.stderr)
            _print_cli_help(sys.stderr)
            sys.exit(2)
        print(f"Unexpected argument: {arg}", file=sys.stderr)
        _print_cli_help(sys.stderr)
        sys.exit(2)

    if session_id is not None and chat_prompt is None:
        print("Error: -id applies only to -c/--chat.", file=sys.stderr)
        _print_cli_help(sys.stderr)
        sys.exit(2)

    for path in load_files:
        if not os.path.isfile(path):
            print(f"Forth source file not found: {path}", file=sys.stderr)
            sys.exit(2)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            yield from vm.evaluate(content)
        except Exception as err:
            print(f"Error loading {path}: {err}", file=sys.stderr)
            sys.exit(1)

    if chat_prompt is not None:
        if session_id is not None:
            vm.host["ai_active_session_id"] = session_id
        try:
            vm.push(chat_prompt)
            vm.push(True)
            yield from vm.call(vm.tick("(ai)"))
        except Exception as err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        active_session = vm.host.get("ai_active_session_id")
        if active_session:
            print(f"SESSION_ID={active_session}", file=sys.stderr)
        if interactive:
            yield from vm.call(vm.tick("repl"))
        return

    if source is not None:
        try:
            yield from vm.evaluate(source)
        except Exception as err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        if interactive:
            yield from vm.call(vm.tick("repl"))
        return

    if interactive or not load_files:
        yield from vm.call(vm.tick("repl"))
    end-code
    // ( -- ) Dispatch command-line arguments or start interactive REPL.
    /// Parses vm.host['argv'] for -h, -i, -l, -e, -c, and starts REPL if requested.
    last :: safe=True

