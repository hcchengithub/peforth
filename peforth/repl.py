#!/usr/bin/env python3
"""peforth v2 AI-first Forth REPL."""

import os
import re
import sys
from collections import deque
from importlib.resources import files
from pathlib import Path

from . import ai_bridge, ai_tools
from .projectk import VM, ForthError

SOURCE_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = files("peforth.data")
FORTH_HOST_MODULES = {"ai_bridge": ai_bridge, "ai_tools": ai_tools}

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.input.ansi_escape_sequences import ANSI_SEQUENCES
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys
except ImportError:
    PromptSession = None
    ANSI_SEQUENCES = None
    KeyBindings = None
    Keys = None



class Constant:
    """A callable object used by the Forth constant defining word."""

    def __init__(self, value):
        self.value = value

    def __call__(self, vm):
        vm.push(self.value)

    def __repr__(self):
        return f"Constant({self.value!r})"


class Value:
    """A callable object used by the Forth value defining word."""

    def __init__(self, value):
        self.value = value

    def __call__(self, vm):
        vm.push(self.value)

    def __repr__(self):
        return f"Value({self.value!r})"


BASE_F_PATH = DATA_ROOT.joinpath("base.f")
AI_F_PATH = DATA_ROOT.joinpath("ai.f")
AUXILIARY_F_PATH = DATA_ROOT.joinpath("auxiliary.f")


def _comment_line(vm: VM) -> None:
    vm.input._ensure_split()
    curr = vm.input.tib[vm.input.itib] if vm.input.itib < len(vm.input.tib) else ""
    pos = curr.find("\n")
    if pos < 0:
        vm.input.consume(len(curr))
    else:
        vm.input.consume(pos + 1)


def _comment_paren(vm: VM) -> None:
    vm.input.read(until=")")


def create_vm(base_file: str | None = None) -> VM:
    vm = VM(host={"Constant": Constant, "Value": Value, "ForthError": ForthError})
    vm.host.update(FORTH_HOST_MODULES)
    vm.host.update({
        "vm": vm,
        "push": vm.push,
        "pop": vm.pop,
        "tos": vm.peek,
        "stack": vm.stack,
        "comma": vm.comma,
    })
    # Comments support
    vm.define("\\", _comment_line, immediate=True)
    vm.define("(", _comment_paren, immediate=True)

    target_base = base_file or BASE_F_PATH
    if hasattr(target_base, "read_text"):
        bootstrap = target_base.read_text(encoding="utf-8")
        vm.dictate(bootstrap)
    elif os.path.isfile(target_base):
        with open(target_base, "r", encoding="utf-8") as f:
            vm.dictate(f.read())
    else:
        raise ForthError(f"Bootstrap file not found: {target_base}")
    vm.dictate(AUXILIARY_F_PATH.read_text(encoding="utf-8"))
    vm.dictate(AI_F_PATH.read_text(encoding="utf-8"))
    return vm


def _process_one_line(vm: VM, line: str, state: dict) -> None:
    """Process one submitted editor buffer, which may contain multiple lines."""

    line = line.rstrip("\r\n")

    # Continue a host code block submitted over multiple editor buffers.
    if state["in_code_block"]:
        state["code_buffer"].append(line)
        block = "\n".join(state["code_buffer"])
        start_pos, _ = vm._find_code_terminator(block)
        if start_pos is not None:
            state["in_code_block"] = False
            state["code_buffer"] = []
            task = vm.dictate(block)
            if task.status == "paused":
                print("Task: paused")
            else:
                print(" ok")
        return

    # Check if this line starts a host code definition
    if re.match(r"^\s*code\b", line):
        start_pos, _ = vm._find_code_terminator(line)
        if start_pos is None:
            state["in_code_block"] = True
            state["code_buffer"] = [line]
            return

    # Blank line in normal mode
    if not line.strip() and not vm.compiling:
        return

    task = vm.dictate(line)
    if task.status == "paused":
        if vm.host.get("ai_pending_approval") or vm.host.get("ai_cleanup_pending"):
            state["ai_task"] = task
        else:
            print("Task: paused")
    elif not vm.compiling:
        print(" ok")


def _process_repl_input(vm: VM, line: str, state: dict) -> None:
    """Route one submitted buffer according to the active REPL mode."""

    command = line.strip().casefold()
    if command in {"chat", "forth"} and vm.tick(command):
        _process_one_line(vm, command, state)
        return
    if command == "bye":
        _process_one_line(vm, line, state)
        return
    if vm.host.get("repl_mode", "forth") == "chat":
        if not line.strip():
            return
        _process_one_line(vm, "ai: " + line, state)
    else:
        _process_one_line(vm, line, state)


def _farewell(vm: VM) -> None:
    try:
        ai_bridge.refresh_session_index(vm)
    except Exception as err:
        print(f"Could not refresh the local AI session list: {err}")

    session_id = ai_bridge._saved_session(vm)
    if session_id:
        title = ai_bridge._session_title(session_id) or "(untitled)"
        short_id = ai_bridge._short_id(session_id)
        print(f'To resume it in a future Forth run, enter: s" {session_id}" ai-use\n')
    else:
        print("No AI session is selected in this Forth run.\n")


def _latest_idle_session(rows):
    candidates = []
    for index, row in enumerate(rows):
        if row.get("status") not in (None, "idle"):
            continue
        try:
            last_active = float(row.get("last_active_at"))
        except (TypeError, ValueError, OverflowError):
            last_active = float("-inf")
        candidates.append((last_active, -index, row))
    return max(candidates, default=(None, None, None))[2]


def _refresh_quiet_session_index(vm: VM) -> None:
    rows = vm.host.get("ai_session_rows")
    if rows is None:
        ai_bridge.refresh_session_index(vm)
        return
    session_id = ai_bridge._saved_session(vm)
    if session_id and not any(row.get("id") == session_id for row in rows):
        rows.insert(0, {"id": session_id})
    ai_bridge._sync_session_index(rows)


def _make_multiline_key_bindings(bindings_type=None):
    bindings_type = bindings_type or KeyBindings
    bindings = bindings_type()

    @bindings.add("c-m")
    def _submit(event):
        event.current_buffer.validate_and_handle()

    @bindings.add("escape", "c-m")
    def _newline_with_escape_enter(event):
        event.current_buffer.insert_text("\n")

    @bindings.add("c-j")
    def _newline_with_control_j(event):
        event.current_buffer.insert_text("\n")

    return bindings


def _map_extended_enter_sequences(sequence_map, newline_key):
    if sequence_map is None or newline_key is None:
        return
    for sequence in ("\x1b[27;2;13~", "\x1b[13;2u"):
        sequence_map[sequence] = newline_key


def repl(vm: VM | None = None, initial_task=None, *, exit_when_idle: bool = False,
         show_greeting: bool = True) -> None:
    if vm is None:
        vm = create_vm()

    if PromptSession is None:
        print("Interactive REPL requires prompt_toolkit. Install it with: "
              f'{sys.executable} -m pip install prompt_toolkit', file=sys.stderr)
        return

    # Modified Enter is reported distinctly only by terminals with extended
    # key support. Map the common xterm and Kitty encodings to the newline key.
    _map_extended_enter_sequences(ANSI_SEQUENCES, Keys.ControlJ if Keys is not None else None)

    prompt_session = PromptSession(
        multiline=True,
        key_bindings=_make_multiline_key_bindings(),
        prompt_continuation=lambda width, line_number, is_soft_wrap: "... ",
    )
    confirmation_session = PromptSession(multiline=False)

    if show_greeting:
        print("peforth Forth REPL")
        print("Enter submits; Ctrl+J or Esc then Enter adds a line. Shift+Enter depends on terminal support.")
        print("Type 'chat' for direct AI chat, 'forth' for Forth, or 'bye'/Ctrl-D to exit.\n")

    vm.host.setdefault("repl_mode", "forth")
    state = {"in_code_block": False, "code_buffer": [], "ai_task": initial_task,
             "queued": deque(), "displayed_approval": None}

    while True:
        try:
            pending = vm.host.get("ai_pending_approval")
            cleanup = vm.host.get("ai_cleanup_pending")
            task = state.get("ai_task")
            if (exit_when_idle and not pending and not cleanup and not state["queued"]
                    and (task is None or task.status in {"done", "aborted", "failed"})):
                try:
                    _refresh_quiet_session_index(vm)
                except Exception as err:
                    print(f"Could not refresh the local AI session list: {err}", file=sys.stderr)
                break
            if pending:
                call_id = pending["action"].get("call_id")
                if state["displayed_approval"] != call_id:
                    print("\nAI requests permission to run this Forth action:")
                    print(f"Purpose: {pending['purpose']}\n---\n{pending['source']}\n---")
                    state["displayed_approval"] = call_id
                print("Trust: run this action and automatically approve future AI-requested Forth actions for this Forth run.")
                print("Yes (press Enter): run this action once.")
                print("No: decline this action.")
                print("Cancel: cancel this AI request.")
                prompt = "Run this action? Press Enter for yes, or type trust, no, or cancel: "
            elif cleanup:
                prompt = (f"Delete session {cleanup['index']} ({ai_bridge._short_id(cleanup['session_id'])})? "
                          "Type delete or cancel: ")
            elif state["queued"]:
                raw_input = state["queued"].popleft()
                _process_repl_input(vm, raw_input, state)
                continue
            else:
                if state["in_code_block"] or vm.compiling:
                    prompt = "... "
                elif vm.host.get("repl_mode", "forth") == "chat":
                    prompt = "chat> "
                else:
                    prompt = "> "
            active_prompt = confirmation_session if pending or cleanup else prompt_session
            raw_input = active_prompt.prompt(prompt)

            clean_input = raw_input.replace("\r\n", "\n").replace("\r", "\n")

            pending = vm.host.get("ai_pending_approval")
            cleanup = vm.host.get("ai_cleanup_pending")
            if cleanup and not pending:
                choice = clean_input.strip().casefold()
                if choice == "delete":
                    vm.host["ai_cleanup_result"] = True
                elif choice == "cancel":
                    vm.host["ai_cleanup_result"] = False
                else:
                    if clean_input.strip():
                        state["queued"].append(clean_input)
                    continue
                vm.host.pop("ai_cleanup_pending", None)
                task = state.get("ai_task")
                state["ai_task"] = None
                if task:
                    task.resume()
                    if task.status == "paused" and (vm.host.get("ai_pending_approval") or vm.host.get("ai_cleanup_pending")):
                        state["ai_task"] = task
                    elif task.status == "done":
                        print(" ok")
                vm.host.pop("ai_cleanup_result", None)
                continue
            if pending:
                choice = clean_input.strip().casefold()
                if choice in {"", "trust", "yes", "y"}:
                    vm.host["ai_approval_result"] = "trust" if choice == "trust" else True
                elif choice in {"no", "n"}:
                    vm.host["ai_approval_result"] = False
                elif choice in {"cancel", "ai-cancel"}:
                    task = state.get("ai_task")
                    try:
                        ai_bridge.cancel_turn(vm)
                    except Exception as err:
                        print(f"Could not cancel remote turn: {err}")
                    if task:
                        task.cancel()
                    state["ai_task"] = None
                    vm.host.pop("ai_pending_approval", None)
                    vm.host.pop("ai_approval_result", None)
                    state["displayed_approval"] = None
                    print("AI task cancelled locally.")
                    continue
                else:
                    if clean_input.strip():
                        state["queued"].append(clean_input)
                    continue
                vm.host.pop("ai_pending_approval", None)
                state["displayed_approval"] = None
                task = state.get("ai_task")
                state["ai_task"] = None
                if task:
                    task.resume()
                    if task.status == "paused" and vm.host.get("ai_pending_approval"):
                        state["ai_task"] = task
                    elif task.status == "done":
                        print(" ok")
                continue
            if state["queued"]:
                state["queued"].append(clean_input)
            else:
                _process_repl_input(vm, clean_input, state)

        except ForthError as err:
            print(f"Error: {err}")
            state["in_code_block"] = False
            state["code_buffer"] = []
            if vm.compiling:
                vm._discard_definition()
        except KeyboardInterrupt:
            print("\n<interrupted>")
            if vm.host.get("ai_pending_approval"):
                try:
                    ai_bridge.cancel_turn(vm)
                except Exception as err:
                    print(f"Could not cancel remote turn: {err}")
            if vm.host.get("ai_pending_approval") or vm.host.get("ai_cleanup_pending"):
                task = state.get("ai_task")
                if task:
                    task.cancel()
                state["ai_task"] = None
                vm.host.pop("ai_pending_approval", None)
                vm.host.pop("ai_approval_result", None)
                vm.host.pop("ai_cleanup_pending", None)
                vm.host.pop("ai_cleanup_result", None)
                state["displayed_approval"] = None
            state["in_code_block"] = False
            state["code_buffer"] = []
            if vm.compiling:
                vm._discard_definition()
        except (EOFError, SystemExit):
            _farewell(vm)
            break


def _print_cli_help(file=None) -> None:
    print("""Usage: f [-h] [-i] [-e <Forth tokens...> | -c <prompt tokens...> | <file.f>]

Run peforth Forth source or start the interactive REPL.

Options:
  -h, --help         Show this help message and exit
  -i, --interactive  Enter the REPL after executing source or completing chat
  -e <tokens...>     Execute all remaining command-line tokens as one TIB,
                     joined with one space between tokens
  -c, --chat         Send all remaining command-line tokens as one prompt to AI,
                     joined with one space; continue the most recently active idle session
  -new, --new-session Start a new session instead of continuing one with -c

With no source argument, the REPL starts. A .f file is executed as one source
buffer. Put -i before -e or -c when you want to continue interactively; all
tokens after -e or -c belong to that Forth input or AI prompt.""", file=file)


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        repl(create_vm())
        return 0

    interactive = False
    source = None
    chat_prompt = None
    force_new_session = False
    source_file = None
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in ("-h", "--help"):
            _print_cli_help()
            return 0
        if arg in ("-i", "--interactive"):
            interactive = True
            index += 1
            continue
        if arg in ("-new", "--new-session"):
            force_new_session = True
            index += 1
            continue
        if arg in ("-e", "--execute"):
            if source_file is not None:
                print("Error: -e cannot be combined with a source file.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                return 2
            source = " ".join(args[index + 1:])
            if not source:
                print("Error: -e requires Forth input.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                return 2
            index = len(args)
            break
        if arg in ("-c", "--chat"):
            if source_file is not None:
                print("Error: -c cannot be combined with a source file.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                return 2
            chat_prompt = " ".join(args[index + 1:])
            if not chat_prompt:
                print("Error: -c requires an AI prompt.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                return 2
            index = len(args)
            break
        if arg.startswith("-"):
            print(f"Unknown option: {arg}", file=sys.stderr)
            _print_cli_help(sys.stderr)
            return 2
        if source_file is not None:
            print(f"Unexpected argument: {arg}", file=sys.stderr)
            _print_cli_help(sys.stderr)
            return 2
        source_file = arg
        index += 1

    if source is None and source_file is not None:
        if not os.path.isfile(source_file):
            print(f"Forth source file not found: {source_file}", file=sys.stderr)
            return 2
        try:
            with open(source_file, "r", encoding="utf-8") as source_handle:
                source = source_handle.read()
        except OSError as err:
            print(f"Could not read {source_file}: {err}", file=sys.stderr)
            return 1

    if force_new_session and chat_prompt is None:
        print("Error: -new applies only to -c/--chat.", file=sys.stderr)
        _print_cli_help(sys.stderr)
        return 2

    vm = create_vm()
    if chat_prompt is not None:
        vm.host["repl_mode"] = "chat"
        if not force_new_session:
            try:
                sessions = ai_bridge._list_remote_sessions()
            except RuntimeError as err:
                print(f"Error: {err}", file=sys.stderr)
                return 1
            vm.host["ai_session_rows"] = sessions
            if sessions:
                latest = _latest_idle_session(sessions)
                if latest is None:
                    print("Error: No idle AI session is available to continue. "
                          "Use -new -c to start a fresh session.", file=sys.stderr)
                    return 1
                vm.host["ai_active_session_id"] = latest["id"]
        try:
            vm.push(chat_prompt)
            vm.push(True)
            task = vm.execute(vm.tick("(ai)"))
        except ForthError as err:
            print(f"Error: {err}", file=sys.stderr)
            return 1
        repl(vm, initial_task=task, exit_when_idle=not interactive, show_greeting=False)
        return 0
    if source is None:
        repl(vm)
        return 0

    try:
        vm.dictate(source)
    except ForthError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    if interactive:
        repl(vm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
