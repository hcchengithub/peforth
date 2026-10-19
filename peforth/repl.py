#!/usr/bin/env python3
"""peforth v2 AI-first Forth REPL."""

import atexit
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from collections import deque
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

from . import ai_bridge, ai_tools
from .projectk import VM, ForthError
from .diagnostic_log import DiagnosticLog

RUNTIME_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_PATH = Path(__file__).resolve().parent
FORTH_SOURCE_ROOT = files("peforth.f")
FORTH_HOST_MODULES = {"ai_bridge": ai_bridge, "ai_tools": ai_tools}

if TYPE_CHECKING:
    from prompt_toolkit.completion import Completer as _CompleterBase
else:
    try:
        from prompt_toolkit.completion import Completer as _CompleterBase
    except ImportError:
        class _CompleterBase:
            pass


def _latest_runtime_file_info(runtime_path: Path = RUNTIME_PATH) -> dict | None:
    """Return the newest .f/.py file under the runtime package path."""
    root = Path(runtime_path).resolve()
    newest: tuple[float, str] | None = None
    try:
        for candidate in root.rglob("*"):
            if candidate.suffix.casefold() not in {".f", ".py"}:
                continue
            try:
                if not candidate.is_file():
                    continue
                modified = candidate.stat().st_mtime
            except OSError:
                continue
            relative = candidate.relative_to(root).as_posix()
            if (newest is None or modified > newest[0]
                    or (modified == newest[0] and relative < newest[1])):
                newest = (modified, relative)
    except OSError:
        return None
    if newest is None:
        return None
    modified, relative = newest
    return {
        "file": relative,
        "modified": datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S"),
    }


def _greeting_line(system_info: dict) -> str:
    """Render the concise REPL banner using runtime file metadata."""
    latest = system_info.get("runtime_latest")
    modified = latest.get("modified") if isinstance(latest, dict) else None
    if isinstance(modified, str) and modified:
        return f"peforth v2 Forth REPL | Latest runtime file modified: {modified}"
    return "peforth v2 Forth REPL"


def _reported_source_path() -> str:
    """Return the checkout path separately from the installed runtime path."""
    configured = os.environ.get("PEFORTH_SOURCE_PATH", "").strip()
    if not configured:
        return str(RUNTIME_ROOT)
    configured = os.path.expandvars(configured)
    return re.sub(
        r"%([^%]+)%",
        lambda match: os.environ.get(match.group(1), match.group(0)),
        configured,
    )


try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import CompleteEvent, Completion
    from prompt_toolkit.filters import Condition, has_completions
    from prompt_toolkit.input.ansi_escape_sequences import ANSI_SEQUENCES
    from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.layout.menus import MultiColumnCompletionMenuControl
    from prompt_toolkit.shortcuts import CompleteStyle
except ImportError:
    PromptSession = None
    CompleteEvent = None
    Completion = None
    Condition = None
    has_completions = None
    ANSI_SEQUENCES = None
    KeyBindings = None
    merge_key_bindings = None
    Keys = None
    MultiColumnCompletionMenuControl = None
    CompleteStyle = None



class ForthWordCompleter(_CompleterBase):
    """Complete the current token from the VM's live Forth dictionary."""

    def __init__(self, vm):
        self.vm = vm

    def get_completions(self, document, complete_event):
        if Completion is None or self.vm.host.get("repl_mode", "forth") == "chat":
            return

        text_before_cursor = document.text_before_cursor
        if not text_before_cursor or text_before_cursor[-1].isspace():
            return
        prefix = text_before_cursor.rsplit(None, 1)[-1]
        if not prefix:
            return

        folded_prefix = prefix.casefold()
        for name in self.vm.words:
            if isinstance(name, str) and name.casefold().startswith(folded_prefix):
                yield Completion(
                    name,
                    start_position=-len(prefix),
                    display_meta="Arrows move | Space selects | Esc cancels",
                )


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


_OUTPUT_LIMIT = 64 * 1024
_PROCESS_TIMEOUT = 60


def _clip(value):
    value = value or ""
    return value[:_OUTPUT_LIMIT], len(value) > _OUTPUT_LIMIT


def _run_process(argv, input_text=None, timeout=_PROCESS_TIMEOUT):
    try:
        completed = subprocess.run(argv, input=input_text, capture_output=True,
                                   text=True, encoding="utf-8", errors="replace",
                                   timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"exit_code": None, "stdout": "", "stderr": str(exc),
                "timed_out": isinstance(exc, subprocess.TimeoutExpired),
                "truncated": False, "error": str(exc)}
    stdout, stdout_truncated = _clip(completed.stdout)
    stderr, stderr_truncated = _clip(completed.stderr)
    return {"exit_code": completed.returncode, "stdout": stdout, "stderr": stderr,
            "timed_out": False, "truncated": stdout_truncated or stderr_truncated}


BASE_F_PATH = FORTH_SOURCE_ROOT.joinpath("base.f")
AI_F_PATH = FORTH_SOURCE_ROOT.joinpath("ai.f")
AUXILIARY_F_PATH = FORTH_SOURCE_ROOT.joinpath("auxiliary.f")


def _comment_line(vm: VM) -> None:
    curr = vm.input.remaining
    pos = curr.find("\n")
    if pos < 0:
        vm.input.consume(len(curr))
    else:
        vm.input.consume(pos + 1)


def _comment_paren(vm: VM) -> None:
    vm.input.read(until=")")


def _program_info(name, version_args):
    path = shutil.which(name)
    if not path:
        return {"available": False, "path": None, "version": None}
    result = _run_process([path, *version_args], timeout=8)
    version_text = result.get("stdout", "").strip() or result.get("stderr", "").strip()
    version = next((line.strip() for line in version_text.splitlines() if line.strip()), None)
    return {"available": True, "path": path, "version": version}


def _pwsh_info(is_windows, is_wsl):
    version_args = [
        "-NoLogo", "-NoProfile", "-NonInteractive", "-Command",
        "$PSVersionTable.PSVersion.ToString()",
    ]
    if is_windows:
        info = _program_info("pwsh.exe", version_args)
        execution_host = "windows"
        source = "path"
    elif is_wsl:
        execution_host = "windows"
        info = _program_info("pwsh.exe", version_args)
        source = "path"
        if not info.get("available"):
            configured = os.environ.get("PEFORTH_PWSH_PATH", "").strip()
            if configured:
                configured = os.path.expanduser(os.path.expandvars(configured))
                info = _program_info(configured, version_args)
                source = "env"
    else:
        info = _program_info("pwsh", version_args)
        execution_host = "linux"
        source = "path"
    info = dict(info)
    info["execution_host"] = execution_host
    info["source"] = source if info.get("available") else None
    return info


def _windows_wsl_info():
    wsl_path = shutil.which("wsl.exe") or shutil.which("wsl")
    if not wsl_path:
        return {"available": False, "path": None, "distro": None, "distros": []}
    listed = _run_process([wsl_path, "--list", "--quiet"], timeout=10)
    raw = (listed.get("stdout") or "").replace("\x00", "").replace("\ufeff", "")
    distros = [line.strip() for line in raw.splitlines() if line.strip()]
    configured = os.environ.get("PEFORTH_WSL_DISTRO", "Ubuntu")
    distro = next((item for item in distros if item.casefold() == configured.casefold()), None)
    if distro is None and configured.casefold() == "ubuntu":
        distro = next((item for item in distros if item.casefold().startswith("ubuntu")), None)
    info = {"available": bool(distro), "path": wsl_path, "distro": distro, "distros": distros}
    if listed.get("exit_code") not in (0, None):
        info["error"] = listed.get("stderr") or "Could not list WSL distributions."
    return info


def _system_cache_path() -> Path:
    return ai_bridge._runtime_config_path() / ".system_cache.json"


def _system_cache_ttl() -> float:
    raw = os.environ.get("PEFORTH_CACHE_TTL")
    if raw is not None:
        try:
            return max(0.0, float(raw.strip()))
        except ValueError:
            pass
    return 604800.0  # 7 days


def _load_system_cache(cache_path: Path, environment: str, fingerprint: dict, ttl: float) -> dict | None:
    if ttl <= 0:
        return None
    try:
        if not cache_path.is_file():
            return None
        age = time.time() - cache_path.stat().st_mtime
        if age < 0 or age > ttl:
            return None
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        if data.get("schema_version") != 1:
            return None
        if data.get("environment") != environment:
            return None
        if data.get("config_fingerprint") != fingerprint:
            return None
        if not isinstance(data.get("shells"), dict) or not isinstance(data.get("wsl"), dict):
            return None
        return data
    except Exception:
        return None


def _save_system_cache(cache_path: Path, data: dict) -> None:
    temp_path = None
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = cache_path.with_name(f"{cache_path.name}.tmp.{os.getpid()}")
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(cache_path)
    except Exception:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _detect_system_info(cache_path: Path | None = None) -> dict:
    """Detect base host information before loading Forth AI words."""
    is_windows = os.name == "nt"
    release = platform.release()
    is_wsl = bool(os.environ.get("WSL_DISTRO_NAME")) or "microsoft" in release.casefold()
    wsl_distro = os.environ.get("WSL_DISTRO_NAME") if is_wsl else None
    prefix = os.path.normcase(os.path.abspath(sys.prefix))
    base_prefix = os.path.normcase(os.path.abspath(sys.base_prefix))
    venv_active = prefix != base_prefix
    environment = "windows" if is_windows else ("wsl" if is_wsl else "linux")
    fingerprint = {
        "PEFORTH_PWSH_PATH": os.environ.get("PEFORTH_PWSH_PATH", "").strip(),
        "PEFORTH_WSL_DISTRO": os.environ.get("PEFORTH_WSL_DISTRO", "Ubuntu").strip(),
    }
    ttl = _system_cache_ttl()
    resolved_cache = cache_path if cache_path is not None else _system_cache_path()
    cached = _load_system_cache(resolved_cache, environment, fingerprint, ttl)
    if cached is not None:
        shells = cached.get("shells", {})
        wsl = cached.get("wsl", {})
    else:
        pwsh = _pwsh_info(is_windows, is_wsl)
        if is_windows:
            wsl = _windows_wsl_info()
            if wsl.get("available"):
                bash_probe = _run_process(
                                [wsl["path"], "-d", wsl["distro"], "--exec", "bash", "--version"], timeout=10)
                version_text = bash_probe.get("stdout", "").strip() or bash_probe.get("stderr", "").strip()
                bash = {
                    "available": bash_probe.get("exit_code") == 0,
                    "path": wsl["path"], "distro": wsl["distro"],
                    "version": next((line.strip() for line in version_text.splitlines() if line.strip()), None),
                }
            else:
                bash = {"available": False, "path": None, "distro": None, "version": None}
        else:
            wsl = {"available": is_wsl, "path": None, "distro": wsl_distro, "distros": []}
            bash = _program_info("bash", ["--version"])
        curl_name = "curl.exe" if is_windows else "curl"
        curl = _program_info(curl_name, ["--version"])
        if is_windows and not curl["available"]:
            curl = _program_info("curl", ["--version"])
        shells = {"pwsh": pwsh, "bash": bash, "curl": curl}
        if ttl > 0:
            _save_system_cache(resolved_cache, {
                "schema_version": 1,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "environment": environment,
                "config_fingerprint": fingerprint,
                "shells": shells,
                "wsl": wsl,
            })
    return {
        "os": platform.system(), "platform": sys.platform,
        "source_path": _reported_source_path(),
        "runtime_path": str(RUNTIME_PATH),
        "runtime_latest": _latest_runtime_file_info(RUNTIME_PATH),
        "python": {"executable": sys.executable, "version": platform.python_version()},
        "venv": {"active": venv_active, "path": sys.prefix if venv_active else None},
        "wsl": {"active": is_wsl, "available": wsl.get("available", False),
                "distro": wsl.get("distro") or wsl_distro, "path": wsl.get("path"),
                "distros": wsl.get("distros", [])},
        "shells": shells,
        "config": {
            "PEFORTH_AI_MODEL": os.environ.get("PEFORTH_AI_MODEL", ""),
            "PEFORTH_CONFIG_DIR": os.environ.get("PEFORTH_CONFIG_DIR", ""),
            "PEFORTH_SOURCE_PATH": os.environ.get("PEFORTH_SOURCE_PATH", ""),
            "PEFORTH_AI_SKILLS_DIR": os.environ.get("PEFORTH_AI_SKILLS_DIR", ""),
            "PEFORTH_WSL_DISTRO": os.environ.get("PEFORTH_WSL_DISTRO", ""),
            "PEFORTH_PWSH_PATH": os.environ.get("PEFORTH_PWSH_PATH", ""),
            "PEFORTH_CACHE_TTL": os.environ.get("PEFORTH_CACHE_TTL", ""),
        },
    }


def _diagnostic_log_mode() -> str:
    mode = os.environ.get("PEFORTH_AI_LOG_MODE", "normal").strip().casefold()
    if mode not in {"disabled", "normal", "verbose"}:
        raise ValueError("PEFORTH_AI_LOG_MODE must be disabled, normal, or verbose")
    return mode


def _diagnostic_environment(system_info: dict) -> str:
    if os.name == "nt":
        return "windows"
    if (system_info.get("wsl") or {}).get("active"):
        return "wsl"
    raise RuntimeError("AI diagnostics supports Windows and WSL runtimes only")


def _close_diagnostic_log(logger: DiagnosticLog, runtime_id: str | None = None) -> None:
    if runtime_id is not None:
        try:
            logger.finish_runtime(runtime_id)
        except Exception as exc:
            print(f"Could not finish AI diagnostic runtime: {exc}", file=sys.stderr)
    try:
        logger.close()
    except Exception as exc:
        print(f"Could not close AI diagnostic log: {exc}", file=sys.stderr)


def create_vm(base_file: str | None = None) -> VM:
    ai_bridge.load_dotenv()
    system_info = _detect_system_info()
    diagnostic_mode = _diagnostic_log_mode()
    config = system_info.setdefault("config", {})
    config["PEFORTH_AI_LOG_MODE"] = diagnostic_mode
    diagnostic_log = None
    diagnostic_runtime_id = None
    if diagnostic_mode != "disabled":
        try:
            environment = _diagnostic_environment(system_info)
            database_path = ai_bridge._runtime_config_path() / "ai-diagnostics.sqlite3"
            diagnostic_log = DiagnosticLog(database_path, environment=environment)
            diagnostic_runtime_id = diagnostic_log.start_runtime(
                source_path=system_info.get("source_path"),
                runtime_path=system_info.get("runtime_path"),
                runtime_version=system_info.get("python", {}).get("version"),
            )
            atexit.register(_close_diagnostic_log, diagnostic_log, diagnostic_runtime_id)
        except Exception as exc:
            if diagnostic_log is not None:
                _close_diagnostic_log(diagnostic_log)
            diagnostic_log = None
            diagnostic_runtime_id = None
            print(f"AI diagnostics unavailable: {exc}", file=sys.stderr)
    vm = VM(host={"Constant": Constant, "Value": Value, "ForthError": ForthError,
             "system_info": system_info})
    vm.host["diagnostic_log_mode"] = diagnostic_mode
    if diagnostic_log is not None:
        vm.host["diagnostic_log"] = diagnostic_log
        vm.host["diagnostic_runtime_id"] = diagnostic_runtime_id
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
        if vm.host.get("ai_pending_approval"):
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


def _make_completion_key_bindings(vm, bindings_type=None):
    """Create completion controls that are active only in Forth mode."""
    bindings_type = bindings_type or KeyBindings
    if (bindings_type is None or Condition is None or has_completions is None
            or Keys is None or CompleteEvent is None):
        raise RuntimeError("Forth completion requires prompt_toolkit.")

    complete_event_type = CompleteEvent
    bindings = bindings_type()
    forth_mode = Condition(lambda: vm.host.get("repl_mode", "forth") != "chat")
    menu_open = has_completions & forth_mode

    def move_vertical(event, step):
        buffer = event.current_buffer
        state = buffer.complete_state
        if state is None or state.complete_index is None:
            return
        rows = 1
        if MultiColumnCompletionMenuControl is not None:
            for window in event.app.layout.visible_windows:
                if isinstance(window.content, MultiColumnCompletionMenuControl):
                    rows = max(1, window.content._rendered_rows)
                    break
        current_index = state.complete_index
        next_index = current_index + step
        if (0 <= next_index < len(state.completions)
                and next_index // rows == current_index // rows):
            buffer.go_to_completion(next_index)

    @bindings.add(Keys.ControlI, filter=forth_mode, eager=True)
    def _show_completions(event):
        buffer = event.current_buffer
        if buffer.complete_state is None:
            buffer.start_completion(
                select_first=True,
                complete_event=complete_event_type(completion_requested=True),
            )

    @bindings.add(Keys.Up, filter=menu_open, eager=True)
    def _previous_completion(event):
        move_vertical(event, -1)

    @bindings.add(Keys.Down, filter=menu_open, eager=True)
    def _next_completion(event):
        move_vertical(event, 1)

    @bindings.add(Keys.ControlJ, filter=menu_open, eager=True)
    def _newline_without_completion(event):
        buffer = event.current_buffer
        buffer.cancel_completion()
        buffer.insert_text("\n")

    @bindings.add(Keys.ControlC, filter=menu_open, eager=True)
    def _interrupt_with_completion_open(event):
        event.current_buffer.cancel_completion()
        event.app.exit(exception=KeyboardInterrupt(), style="class:aborting")

    @bindings.add(Keys.ControlD, filter=menu_open, eager=True)
    def _delete_forward_with_completion_open(event):
        buffer = event.current_buffer
        buffer.cancel_completion()
        buffer.delete()

    @bindings.add(Keys.ControlM, filter=menu_open, eager=True)
    def _submit_without_completion(event):
        buffer = event.current_buffer
        buffer.cancel_completion()
        buffer.validate_and_handle()

    @bindings.add(Keys.Backspace, filter=menu_open, eager=True)
    def _backspace_without_completion(event):
        buffer = event.current_buffer
        buffer.cancel_completion()
        buffer.delete_before_cursor()

    @bindings.add(Keys.Delete, filter=menu_open, eager=True)
    def _delete_without_completion(event):
        buffer = event.current_buffer
        buffer.cancel_completion()
        buffer.delete()

    @bindings.add(" ", filter=menu_open, eager=True)
    def _accept_completion(event):
        buffer = event.current_buffer
        state = buffer.complete_state
        completion = state.current_completion if state is not None else None
        if completion is None:
            buffer.cancel_completion()
            buffer.insert_text(" ")
            return
        buffer.apply_completion(completion)
        buffer.insert_text(" ")

    @bindings.add("escape", filter=menu_open, eager=True)
    def _cancel_completion(event):
        event.current_buffer.cancel_completion()

    @bindings.add(Keys.Any, filter=menu_open)
    def _type_without_completion(event):
        if event.data == " ":
            _accept_completion(event)
            return
        buffer = event.current_buffer
        buffer.cancel_completion()
        if event.data.isprintable():
            buffer.insert_text(event.data)

    return bindings


def _make_repl_key_bindings(vm):
    """Combine line-editor controls with the Forth completion controls."""
    if merge_key_bindings is None:
        raise RuntimeError("Interactive REPL requires prompt_toolkit.")
    return merge_key_bindings([
        _make_completion_key_bindings(vm),
        _make_multiline_key_bindings(),
    ])


def read_numbered_choice(prompt: str, choices=("1", "2", "3", "4"), default="1", *, input=None, output=None) -> str:
    """Return a permitted single-character choice, displaying it inline."""
    if PromptSession is None or KeyBindings is None:
        raise RuntimeError("Single-key choices require prompt_toolkit.")
    choices = tuple(choices)
    if (not choices or any(not isinstance(choice, str) or len(choice) != 1 for choice in choices)
            or len(set(choices)) != len(choices)):
        raise ValueError("choices must be distinct single-character strings.")
    if default not in choices:
        raise ValueError("default must be one of the permitted choices.")

    bindings = KeyBindings()

    @bindings.add("c-m", eager=True)
    def _enter(event):
        event.current_buffer.text = default
        event.current_buffer.validate_and_handle()

    for choice in choices:
        def _select(event, selected=choice):
            event.current_buffer.text = selected
            event.current_buffer.validate_and_handle()
        bindings.add(choice, eager=True)(_select)

    session_options = {"multiline": False, "key_bindings": bindings}
    if input is not None:
        session_options["input"] = input
    if output is not None:
        session_options["output"] = output
    formatted_prompt = prompt
    if "\x1b[" in prompt:
        from prompt_toolkit.formatted_text import ANSI
        formatted_prompt = ANSI(prompt)
    return PromptSession(**session_options).prompt(formatted_prompt)


_AI_APPROVAL_DECISIONS = {"allow_once", "trust_task", "deny", "cancel"}
_TERMINAL_TASK_STATES = {"done", "aborted", "failed"}


def _expire_ai_task_trust(state):
    task = state.get("trusted_ai_task")
    if task is not None and task.status in _TERMINAL_TASK_STATES:
        state["trusted_ai_task"] = None


def _resolve_ai_approval_decision(vm: VM, state: dict, task, proposal: dict) -> str:
    """Resolve a pending proposal through Runtime Trust, Task Trust, or ai-approve."""
    _expire_ai_task_trust(state)
    if vm.host.get("ai_trusted") or (task is not None and state.get("trusted_ai_task") is task):
        return "allow_once"
    if task is None:
        raise ForthError("An AI approval proposal has no active Task.")
    approval_word = vm.tick("ai-approve")
    if approval_word is None:
        raise ForthError("The ai-approve Forth word is not defined.")

    stack_depth = len(vm.stack)
    vm.push(proposal)
    try:
        approval_task = vm.execute(approval_word)
        if approval_task.status != "done":
            if approval_task.status in {"ready", "paused"}:
                approval_task.cancel()
            raise ForthError("The ai-approve word must finish without pausing.")
        if len(vm.stack) != stack_depth + 1:
            raise ForthError("The ai-approve word must return one decision.")
        decision = vm.pop()
    finally:
        del vm.stack[stack_depth:]

    if decision not in _AI_APPROVAL_DECISIONS:
        raise ForthError(f"ai-approve returned an invalid decision: {decision!r}")
    if decision == "trust_task":
        state["trusted_ai_task"] = task
    return decision


def _clear_ai_task_trust(state, task=None):
    if task is None or state.get("trusted_ai_task") is task:
        state["trusted_ai_task"] = None


def _map_extended_enter_sequences(sequence_map, newline_key):
    if sequence_map is None or newline_key is None:
        return
    for sequence in ("\x1b[27;2;13~", "\x1b[13;2u"):
        sequence_map[sequence] = newline_key


def repl(vm: VM | None = None, initial_task=None, *, exit_when_idle: bool = False,
         show_greeting: bool = True) -> None:
    if vm is None:
        vm = create_vm()

    if PromptSession is None or CompleteStyle is None:
        print("Interactive REPL requires prompt_toolkit. Install it with: "
              f'{sys.executable} -m pip install prompt_toolkit', file=sys.stderr)
        return

    # Modified Enter is reported distinctly only by terminals with extended
    # key support. Map the common xterm and Kitty encodings to the newline key.
    _map_extended_enter_sequences(ANSI_SEQUENCES, Keys.ControlJ if Keys is not None else None)

    prompt_session = PromptSession(
        multiline=True,
        key_bindings=_make_repl_key_bindings(vm),
        completer=ForthWordCompleter(vm),
        complete_while_typing=False,
        complete_style=CompleteStyle.MULTI_COLUMN,
        prompt_continuation=lambda width, line_number, is_soft_wrap: "... ",
    )

    if show_greeting:
        print(_greeting_line(vm.host.get("system_info") or {}))
        print("Enter submits; Ctrl+J or Esc then Enter adds a line. Shift+Enter depends on terminal support.")
        print("Type 'chat' for direct AI chat, 'forth' for Forth, or 'bye'/Ctrl-D to exit.\n")

    vm.host.setdefault("repl_mode", "forth")
    state = {"in_code_block": False, "code_buffer": [], "ai_task": initial_task,
             "queued": deque(), "trusted_ai_task": None}
    previous_task_trust_clear = vm.host.get("ai_clear_task_trust")

    def clear_ai_task_trust():
        _clear_ai_task_trust(state)
        if callable(previous_task_trust_clear):
            previous_task_trust_clear()

    vm.host["ai_clear_task_trust"] = clear_ai_task_trust

    while True:
        _expire_ai_task_trust(state)
        try:
            pending = vm.host.get("ai_pending_approval")
            task = state.get("ai_task")
            if (exit_when_idle and not pending and not state["queued"]
                    and (task is None or task.status in {"done", "aborted", "failed"})):
                try:
                    _refresh_quiet_session_index(vm)
                except Exception as err:
                    print(f"Could not refresh the local AI session list: {err}", file=sys.stderr)
                break
            if pending:
                try:
                    if task is None:
                        raise ForthError("An AI approval request has no active Task.")
                    decision = _resolve_ai_approval_decision(vm, state, task, pending)
                except Exception as err:
                    print(f"AI approval failed; cancelling the task: {err}")
                    ai_bridge._diagnostic_cancel_approval(
                        pending, reason="approval_resolution_failed"
                    )
                    try:
                        ai_bridge.cancel_turn(vm)
                    except Exception as cancel_err:
                        print(f"Could not cancel remote turn: {cancel_err}")
                    if task is not None and task.status in {"ready", "paused"}:
                        task.cancel()
                    state["ai_task"] = None
                    vm.host.pop("ai_pending_approval", None)
                    vm.host.pop("ai_approval_result", None)
                    _clear_ai_task_trust(state, task)
                    continue
                if state.get("trusted_ai_task") is task and decision == "allow_once":
                    print("\nAI Forth proposal auto-approved for this AI task:")
                    print(f"Purpose: {pending['purpose']}\n---\n{pending['source']}\n---")
                if decision in {"allow_once", "trust_task"}:
                    vm.host["ai_approval_result"] = True
                elif decision == "deny":
                    vm.host["ai_approval_result"] = False
                elif decision == "cancel":
                    ai_bridge._diagnostic_cancel_approval(
                        pending, reason="user_cancel"
                    )
                    try:
                        ai_bridge.cancel_turn(vm)
                    except Exception as err:
                        print(f"Could not cancel remote turn: {err}")
                    task.cancel()
                    state["ai_task"] = None
                    vm.host.pop("ai_pending_approval", None)
                    vm.host.pop("ai_approval_result", None)
                    _clear_ai_task_trust(state, task)
                    print("AI task cancelled locally.")
                    continue
                else:
                    raise ForthError(f"Invalid AI approval decision: {decision!r}")
                vm.host.pop("ai_pending_approval", None)
                state["ai_task"] = None
                task.resume()
                if task.status == "paused" and vm.host.get("ai_pending_approval"):
                    state["ai_task"] = task
                elif task.status == "done":
                    print(" ok")
                _expire_ai_task_trust(state)
                continue
            if state["queued"]:
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
            raw_input = prompt_session.prompt(prompt)

            clean_input = raw_input.replace(chr(13) + chr(10), chr(10)).replace(chr(13), chr(10))

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
                ai_bridge._diagnostic_cancel_approval(
                    vm.host["ai_pending_approval"], reason="keyboard_interrupt"
                )
                try:
                    ai_bridge.cancel_turn(vm)
                except Exception as err:
                    print(f"Could not cancel remote turn: {err}")
            if vm.host.get("ai_pending_approval"):
                task = state.get("ai_task")
                if task:
                    task.cancel()
                _clear_ai_task_trust(state, task)
                state["ai_task"] = None
                vm.host.pop("ai_pending_approval", None)
                vm.host.pop("ai_approval_result", None)
            state["in_code_block"] = False
            state["code_buffer"] = []
            if vm.compiling:
                vm._discard_definition()
        except (EOFError, SystemExit):
            _farewell(vm)
            break

    _clear_ai_task_trust(state)
    if vm.host.get("ai_clear_task_trust") is clear_ai_task_trust:
        if previous_task_trust_clear is None:
            vm.host.pop("ai_clear_task_trust", None)
        else:
            vm.host["ai_clear_task_trust"] = previous_task_trust_clear


def _print_cli_help(file=None) -> None:
    print("""Usage: f [-h] [-i] [-e <Forth tokens...> | [-id <session-id>] -c <prompt tokens...> | <file.f>]

Run peforth Forth source or start the interactive REPL.

Options:
  -h, --help         Show this help message and exit
  -i, --interactive  Enter the REPL after executing source or completing chat
  -e <tokens...>     Execute all remaining command-line tokens as one TIB,
                     joined with one space between tokens
  -c, --chat         Send all remaining command-line tokens as one prompt to AI,
                     joined with one space; start a new session unless -id is given
  -id <session-id>   Continue this existing session; must appear before -c

Each -c run writes SESSION_ID=<session-id> to stderr after completion.

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
    session_id = None
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
        if arg == "-id":
            if session_id is not None:
                print("Error: -id may be specified only once.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                return 2
            if index + 1 >= len(args) or not args[index + 1] or args[index + 1].startswith("-"):
                print("Error: -id requires a session ID before -c.", file=sys.stderr)
                _print_cli_help(sys.stderr)
                return 2
            session_id = args[index + 1]
            index += 2
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

    if session_id is not None and chat_prompt is None:
        print("Error: -id applies only to -c/--chat.", file=sys.stderr)
        _print_cli_help(sys.stderr)
        return 2

    vm = create_vm()
    if chat_prompt is not None:
        vm.host["ai_transport_stream_once"] = False
        vm.host["repl_mode"] = "chat"
        if session_id is not None:
            vm.host["ai_active_session_id"] = session_id
        try:
            vm.push(chat_prompt)
            vm.push(True)
            task = vm.execute(vm.tick("(ai)"))
        except ForthError as err:
            print(f"Error: {err}", file=sys.stderr)
            return 1
        repl(vm, initial_task=task, exit_when_idle=not interactive, show_greeting=False)
        active_session_id = ai_bridge._saved_session(vm)
        if active_session_id:
            print(f"SESSION_ID={active_session_id}", file=sys.stderr)
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
