\ auxiliary.f - Auxiliary words and system utilities for peforth
\ peforth 2.1.0

\ --- 1. Terminal Utilities ---

code cls
    print('\033[2J\033[3J\033[H')
    end-code
    // ( -- ) Clear terminal screen, scrollback buffer, and move cursor to top-left.
    last :: safe=True

code stringify
    import json
    val = vm.pop()
    try:
        vm.push(json.dumps(val, indent=2, ensure_ascii=False))
    except Exception:
        vm.push(str(val))
    end-code
    // ( object -- pretty-string ) Convert a Python or JSON object to indented string.
    last :: safe=True


\ --- 2. Audio Chimes & Notifications ---

code (play-notes)
    import subprocess
    import shutil
    import os
    notes = vm.pop()
    if not isinstance(notes, list):
        raise KernelError("(play-notes) expects a list of [freq, duration_ms] pairs")
    ps = shutil.which("powershell.exe") or shutil.which("powershell") or shutil.which("pwsh.exe") or shutil.which("pwsh")
    if ps:
        script = "; ".join([f"[Console]::Beep({f}, {d}); Start-Sleep -Milliseconds 25" for f, d in notes])
        try:
            kwargs = {}
            if os.name == "nt":
                kwargs["creationflags"] = 0x08000000 # CREATE_NO_WINDOW
            subprocess.Popen([ps, "-NoProfile", "-NonInteractive", "-Command", script], **kwargs)
        except Exception:
            pass
    end-code
    // ( notes-list -- ) Asynchronously play notes via PowerShell Console::Beep.
    last :: safe=True

: nokia ( -- )
    py> [[659,120],[587,120],[370,240],[415,240]] (play-notes)
    ;
    // ( -- ) Play the gentle first Nokia Tune phrase (4 notes) asynchronously.
    last :: safe=True

: nokia2 ( -- )
    py> [[494,120],[440,120],[277,240],[330,240],[440,880]] (play-notes)
    ;
    // ( -- ) Play the gentle final Nokia Tune phrase (5 notes, long finish) asynchronously.
    last :: safe=True

: nokia-full ( -- )
    py> [[659,120],[587,120],[370,240],[415,240],[554,120],[494,120],[294,240],[330,240],[494,120],[440,120],[277,240],[330,240],[440,880]] (play-notes)
    ;
    // ( -- ) Play the complete gentle Nokia Tune (13 notes) asynchronously.
    last :: safe=True

\ --- 3. Diagnostics & System Tools ---

code run-monitor
    import os
    import subprocess
    import sys
    from pathlib import Path

    base = Path(vm.host.get("__file__dir__", "."))
    monitor = base / "tools" / "peforth_logging_monitor.py"
    if not monitor.is_file():
        monitor = Path(sys.prefix).parent / "tools" / "peforth_logging_monitor.py"
    if not monitor.is_file():
        raise RuntimeError(f"Monitor script not found: {monitor}")

    env = os.environ.copy()
    subprocess.run([sys.executable, str(monitor)], env=env, check=False)
    end-code
    // ( -- ) Run the peforth diagnostic logging monitor in the foreground.
    /// Uses the current Python VENV and configured SQLite diagnostics database.
    /// Press Ctrl-C to stop the monitor and return to Forth.
    last :: safe=True

\ --- 4. Python Object Inspection & Key Utilities ---

code dir
    obj = vm.pop()
    vm.push([name for name in dir(obj) if not name.startswith("_") and not name.endswith("_")])
    end-code
    // ( object -- names ) List public member names.
    /// Filters names beginning or ending with an underscore.
last :: safe=True

code _dir_
    vm.push(dir(vm.pop()))
    end-code
    // ( object -- names ) Return Python's complete dir() result.
    /// Includes private and special names.
last :: safe=True

code dict>keys
    vm.push(list(vm.pop().keys()))
    end-code
    // ( dict -- keys ) Return dictionary keys as a list.
    /// The result is a list, not a dict_keys view.
last :: safe=True

code keys
    obj = vm.pop()
    if isinstance(obj, dict):
        vm.push(list(obj.keys()))
    else:
        vm.push([name for name in dir(obj) if not name.startswith("_") and not name.endswith("_")])
    end-code
    // ( object -- keys ) Return dict keys or public members as a list.
    /// Both input cases return a list.
last :: safe=True


\ --- 5. Multi-line Text, Comments & Command Line Echo ---

code <text>
    import re
    chunks = []
    depth = 1
    boundary = re.compile(r"</text>|<text>")
    while depth:
        remaining = vm.input.remaining
        match = boundary.search(remaining)
        if match is None:
            raise KernelError("Unclosed <text>")
        chunk = vm.input.read(until=boundary)
        tag = remaining[len(chunk):match.end()]
        chunks.append(chunk)
        if tag == "<text>":
            depth += 1
            chunks.append(tag)
        else:
            depth -= 1
            if depth:
                chunks.append(tag)
    text = "".join(chunks)
    if text.startswith(" "):
        text = text[1:]
    if vm.compiling:
        vm.literal(text)
    else:
        vm.push(text)
    end-code immediate
    // ( <text> -- string ) Read a possibly nested text block.
    /// Inner <text> tags are retained.
last :: safe=True

code </text>
    end-code immediate
    // ( -- ) Closing delimiter consumed by <text>.
last :: safe=True

code <comment>
    import re
    depth = 1
    boundary = re.compile(r"<comment>|</comment>")
    while depth:
        remaining = vm.input.remaining
        match = boundary.search(remaining)
        if match is None:
            raise KernelError("Unclosed <comment>")
        vm.input.read(until=boundary)
        tag = remaining[match.start():match.end()]
        if tag == "<comment>":
            depth += 1
        else:
            depth -= 1
    end-code immediate
    // ( <comment> -- ) Skip a possibly nested comment block.
last :: safe=True

code </comment>
    end-code immediate
    // ( -- ) Closing delimiter consumed by <comment>.
last :: safe=True

code -->
    value = vm.pop()
    source = vm.input.tib
    line_start = source.rfind("\n", 0, vm.input.itib) + 1
    command = source[line_start:vm.input.itib].strip()
    print(f"{command} {value} ({type(value)})")
    end-code
    // ( result -- ) Print command line, and result.
    /// Includes the Python type.
last :: safe=True

code ==>
    value = vm.pop()
    source = vm.input.tib
    line_start = source.rfind("\n", 0, vm.input.itib) + 1
    command = source[line_start:vm.input.itib].strip()
    print(f"\n{command} {value} ({type(value)})")
    end-code
    // ( result -- ) Print a blank line, command line, and result.
    /// Includes the Python type.
last :: safe=True


\ --- 6. Debugging & Small Primitives ---

code (space)
    vm.push(" ")
    end-code
    // ( -- string ) Push one space.
last :: safe=True

code (')
    name = vm.pop()
    word = vm.tick(name) if isinstance(name, str) else None
    if word is None:
        raise KernelError(f"Unknown word: {name}")
    vm.push(word)
    end-code
    // ( name -- word ) Look up the word named by the string on TOS.
    /// Unlike tick, it takes the name from the stack.
last :: safe=True

code sleep
    import time
    milliseconds = vm.pop()
    if isinstance(milliseconds, bool) or not isinstance(milliseconds, int):
        raise KernelError("sleep expects an integer number of milliseconds")
    if milliseconds < 0:
        raise KernelError("sleep milliseconds must be non-negative")
    time.sleep(milliseconds / 1000)
    end-code
    // ( milliseconds -- ) Suspend the current Forth task for the given number of milliseconds.
last :: safe=True

code *debug*
    breakpoint()
    end-code
    // ( -- ) Enter Python interactive breakpoint debugger.
    /// Call Python's built-in breakpoint() to inspect VM state.
last :: safe=False


\ --- 7. Interpretation-Time Flow Control ---

code (itib@)
    vm.push(vm.input.itib)
    end-code
    // ( -- offset ) Return current TIB reading offset.
last :: safe=True

code (itib!)
    offset = vm.pop()
    if not isinstance(offset, int) or isinstance(offset, bool) or not 0 <= offset <= len(vm.input.tib):
        raise KernelError("Invalid TIB input offset")
    vm.input.itib = offset
    end-code
    // ( offset -- ) Set current TIB reading offset.
last :: safe=True

code (interpret-only)
    if vm.compiling:
        raise KernelError("This flow-control word can only be used while interpreting")
    end-code
    // ( -- ) Raise KernelError if currently compiling.
last :: safe=True

code (skip-conditional)
    stop_at_else = bool(vm.pop())
    vm.tstack.append(1)
    try:
        while True:
            token = vm.input.read()
            if token is None:
                end = "[else] or [then]" if stop_at_else else "[then]"
                raise KernelError(f"Unmatched conditional; expected {end}")
            if token in ('s"', "s'", "s`", "s|", "s^", "s/"):
                quoted = vm.tick(token)
                delim = quoted.body[0] if hasattr(quoted, "body") and quoted.body else token[1]
                vm.input.read(until=delim)
                continue
            if token in ('."', ".'", ".`", ".|", ".^", "./"):
                quoted = vm.tick(token)
                delim = quoted.body[0] if hasattr(quoted, "body") and quoted.body else token[1]
                vm.input.read(until=delim)
                continue
            if token == "(":
                vm.input.read(until=")")
                continue
            if token in ("\\", "//", "///"):
                if "\n" in vm.input.remaining:
                    vm.input.read(until="\n")
                else:
                    vm.input.rest()
                continue
            if token == "[if]":
                vm.tstack[-1] += 1
            elif token == "[then]":
                vm.tstack[-1] -= 1
                if vm.tstack[-1] == 0:
                    return
            elif token == "[else]" and stop_at_else and vm.tstack[-1] == 1:
                return
    finally:
        vm.tstack.pop()
    end-code
    // ( stop-at-else? -- ) Skip conditional branch until matching [else] or [then].
last :: safe=True

code [if]
    if not vm.pop():
        vm.push(True)
        yield from vm.call(vm.tick("(skip-conditional)"))
    end-code immediate
    // ( flag -- ) Interpret the true arm; skip to matching [else] or [then] when false.
last :: safe=True

code [else]
    vm.push(False)
    yield from vm.call(vm.tick("(skip-conditional)"))
    end-code immediate
    // ( -- ) Skip to matching [then].
last :: safe=True

: [then] ; immediate
    // ( -- ) End a bracketed conditional group.
last :: safe=True

: [begin] (interpret-only) (itib@) >t ; immediate
    // ( -- ) Save current TIB offset as start of an interpretation-time loop.
last :: safe=True

: [again] (interpret-only) t@ (itib!) ; immediate
    // ( -- ) Repeat the current [begin] loop unconditionally.
last :: safe=True

: [until]
    (interpret-only)
    if t> drop else t@ (itib!) then
    ; immediate
    // ( flag -- ) Repeat the current [begin] loop while flag is false.
last :: safe=True

: [for] (interpret-only) (itib@) >t >t ; immediate
    // ( count -- ) Start an interpretation-time counted loop; [next] checks after each pass.
last :: safe=True

: [next]
    (interpret-only)
    t> 1- dup >t 0 >
    if
        t> t> dup (itib!) >t >t
    else
        t> t> drop drop
    then
    ; immediate
    // ( -- ) Decrement loop counter; rewind to [for] body if > 0.
last :: safe=True


\ --- 8. Interactive Shell & Sudo Commands ---

code (pwsh)
    import os
    import shutil

    command_line = vm.pop()
    if not isinstance(command_line, str):
        vm.push({
            "exit_code": None,
            "output": "",
            "truncated": False,
            "error": "(pwsh) expects a command line string.",
        })
        return

    if not command_line.strip():
        vm.push({
            "exit_code": 2,
            "output": "",
            "truncated": False,
            "error": "empty command line",
        })
        return

    pwsh_path = shutil.which("pwsh") or shutil.which("pwsh.exe") or shutil.which("powershell.exe") or "powershell"

    output_limit = 65536
    captured = bytearray()
    truncated = [False]

    try:
        import pty
        has_pty = True
    except ImportError:
        has_pty = False

    if has_pty:
        def read_master(fd):
            try:
                chunk = os.read(fd, 1024)
            except OSError:
                return b""

            room = max(0, output_limit - len(captured))
            if room:
                captured.extend(chunk[:room])
            if len(chunk) > room:
                truncated[0] = True

            return chunk

        status = pty.spawn(
            [pwsh_path, "-NoLogo", "-Command", command_line],
            master_read=read_master,
        )
        exit_code = os.waitstatus_to_exitcode(status)
    else:
        import subprocess
        import sys

        proc = subprocess.Popen(
            [pwsh_path, "-NoLogo", "-Command", command_line],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        while True:
            chunk = proc.stdout.read(1024)
            if not chunk:
                break
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            room = max(0, output_limit - len(captured))
            if room:
                captured.extend(chunk[:room])
            if len(chunk) > room:
                truncated[0] = True
        proc.wait()
        exit_code = proc.returncode

    vm.push({
        "exit_code": exit_code,
        "output": captured.decode("utf-8", errors="replace"),
        "truncated": truncated[0],
    })
    end-code
    // ( command-line -- result-dict ) Execute a command script in PowerShell.
last :: safe=False

: pwsh "" word (pwsh) ;
    // ( <command> -- result-dict ) Run remaining TIB text in PowerShell.
last :: safe=False

code (bash)
    import os
    import shutil

    command_line = vm.pop()
    if not isinstance(command_line, str):
        vm.push({
            "exit_code": None,
            "output": "",
            "truncated": False,
            "error": "(bash) expects a command line string.",
        })
        return

    if not command_line.strip():
        vm.push({
            "exit_code": 2,
            "output": "",
            "truncated": False,
            "error": "empty command line",
        })
        return

    output_limit = 65536
    captured = bytearray()
    truncated = [False]

    try:
        import pty
        has_pty = True
    except ImportError:
        has_pty = False

    if has_pty:
        def read_master(fd):
            try:
                chunk = os.read(fd, 1024)
            except OSError:
                return b""

            room = max(0, output_limit - len(captured))
            if room:
                captured.extend(chunk[:room])
            if len(chunk) > room:
                truncated[0] = True

            return chunk

        status = pty.spawn(
            ["bash", "-i", "-c", command_line],
            master_read=read_master,
        )
        exit_code = os.waitstatus_to_exitcode(status)
    else:
        import subprocess
        import sys

        bash_cmd = ["bash", "-c", command_line]
        if os.name == "nt" and not shutil.which("bash") and shutil.which("wsl"):
            bash_cmd = ["wsl", "--exec", "bash", "-c", command_line]

        proc = subprocess.Popen(
            bash_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        while True:
            chunk = proc.stdout.read(1024)
            if not chunk:
                break
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            room = max(0, output_limit - len(captured))
            if room:
                captured.extend(chunk[:room])
            if len(chunk) > room:
                truncated[0] = True
        proc.wait()
        exit_code = proc.returncode

    vm.push({
        "exit_code": exit_code,
        "output": captured.decode("utf-8", errors="replace"),
        "truncated": truncated[0],
    })
    end-code
    // ( command-line -- result-dict ) Execute a command script in Bash.
last :: safe=False

: bash "" word (bash) ;
    // ( <command> -- result-dict ) Run remaining TIB text in Bash.
last :: safe=False

code (sudo)
    import os
    import shutil

    command_line = vm.pop()
    if not isinstance(command_line, str):
        vm.push({
            "exit_code": None,
            "output": "",
            "truncated": False,
            "error": "(sudo) expects a command line string.",
        })
        return

    if not command_line.strip():
        vm.push({
            "exit_code": 2,
            "output": "",
            "truncated": False,
            "error": "empty command line",
        })
        return

    print("[sudo] Enter your password in this terminal if prompted.", flush=True)

    output_limit = 65536
    captured = bytearray()
    truncated = [False]

    try:
        import pty
        has_pty = True
    except ImportError:
        has_pty = False

    if has_pty:
        def read_master(fd):
            try:
                chunk = os.read(fd, 1024)
            except OSError:
                return b""

            room = max(0, output_limit - len(captured))
            if room:
                captured.extend(chunk[:room])
            if len(chunk) > room:
                truncated[0] = True

            return chunk

        status = pty.spawn(
            ["sudo", "--", "bash", "-c", command_line],
            master_read=read_master,
        )
        exit_code = os.waitstatus_to_exitcode(status)
    else:
        import subprocess
        import sys

        sudo_cmd = ["sudo", "bash", "-c", command_line]
        if os.name == "nt" and shutil.which("wsl"):
            sudo_cmd = ["wsl", "--exec", "sudo", "bash", "-c", command_line]

        proc = subprocess.Popen(
            sudo_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        while True:
            chunk = proc.stdout.read(1024)
            if not chunk:
                break
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
            room = max(0, output_limit - len(captured))
            if room:
                captured.extend(chunk[:room])
            if len(chunk) > room:
                truncated[0] = True
        proc.wait()
        exit_code = proc.returncode

    vm.push({
        "exit_code": exit_code,
        "output": captured.decode("utf-8", errors="replace"),
        "truncated": truncated[0],
    })
    end-code
    // ( command-line -- result-dict ) Execute a command script with sudo in Bash.
last :: safe=False

: sudo "" word (sudo) ;
    // ( <command> -- result-dict ) Run remaining TIB text with sudo.
last :: safe=False


\ --- 9. Windows Dialogs ---

code Windows-Message-Box
    import subprocess
    import json
    import shutil
    import os

    buttons = vm.pop()
    title = vm.pop()
    msg = vm.pop()
    if not all(isinstance(x, str) for x in (msg, title, buttons)):
        raise TypeError("Windows-Message-Box expects message, title, and buttons strings")
    allowed = {"OK", "OKCancel", "YesNo", "YesNoCancel", "RetryCancel", "AbortRetryIgnore"}
    if buttons not in allowed:
        raise ValueError(f"buttons must be one of: {', '.join(sorted(allowed))}")

    ps = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$f = New-Object System.Windows.Forms.Form -Property @{ TopMost = $true }; "
        f"$r = [System.Windows.Forms.MessageBox]::Show($f, {json.dumps(msg, ensure_ascii=False)}, "
        f"{json.dumps(title, ensure_ascii=False)}, "
        f"[System.Windows.Forms.MessageBoxButtons]::{buttons}, "
        "[System.Windows.Forms.MessageBoxIcon]::Question); "
        "$f.Dispose(); "
        "[Console]::Out.Write($r.ToString())"
    )
    ps_path = (
        shutil.which("pwsh.exe")
        or shutil.which("pwsh")
        or shutil.which("powershell.exe")
        or shutil.which("powershell")
    )
    if not ps_path:
        raise RuntimeError("PowerShell was not found")
    kwargs = {"capture_output": True, "text": True, "encoding": "utf-8", "errors": "replace"}
    if os.name == "nt":
        kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    r = subprocess.run([ps_path, "-NoProfile", "-NonInteractive", "-Command", ps], **kwargs)
    vm.push({"exit_code": r.returncode, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()})
    end-code
    // ( message-string title-string buttons-string -- result-dict ) Display a top-most Windows dialog with a selectable button set; stdout is the clicked button name.
    /// Buttons string options: "OK", "OKCancel", "YesNo", "YesNoCancel", "RetryCancel", "AbortRetryIgnore" (case-sensitive).
    /// Example: s" Continue?" s" Confirm" s" YesNo" Windows-Message-Box .  ( result dict; stdout is "Yes" or "No" )
last :: safe=False


\ --- 10. External Notifications (LINE) ---

code line-notify
    import os
    import json
    import urllib.request
    import urllib.error

    msg = vm.pop()
    if not isinstance(msg, str):
        raise TypeError("line-notify expects a message string on TOS")

    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
    user_id = os.environ.get("LINE_USER_ID", "").strip()
    endpoint = os.environ.get("LINE_API_ENDPOINT", "").strip() or "https://api.line.me/v2/bot/message/push"
    disabled = os.environ.get("LINE_NOTIFY_DISABLED", "").strip() == "1"

    if not token or not user_id:
        try:
            import ai
            ai.load_dotenv()
            token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip()
            user_id = os.environ.get("LINE_USER_ID", "").strip()
        except Exception:
            pass

    if not token or not user_id:
        vm.push({
            "status_code": None,
            "error": "LINE_CHANNEL_ACCESS_TOKEN and LINE_USER_ID must be set in environment or .env.",
            "response": None,
        })
        return

    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": msg}],
    }
    payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    if disabled:
        vm.push({
            "status_code": 200,
            "disabled": True,
            "payload": payload,
            "error": None,
            "response": "LINE_NOTIFY_DISABLED=1: message prepared but not sent.",
        })
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    req = urllib.request.Request(endpoint, data=payload_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            body_text = resp.read().decode("utf-8", errors="replace")
            try:
                resp_data = json.loads(body_text) if body_text.strip() else {}
            except Exception:
                resp_data = body_text
            vm.push({"status_code": status, "error": None, "response": resp_data})
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(err_body)
        except Exception:
            err_json = err_body
        vm.push({"status_code": e.code, "error": f"HTTPError {e.code}: {e.reason}", "response": err_json})
    except Exception as e:
        vm.push({"status_code": None, "error": f"{type(e).__name__}: {e}", "response": None})
    end-code
    // ( message-string -- result-dict ) Push a text message to user's LINE account via LINE Messaging API.
    /// Reads LINE_CHANNEL_ACCESS_TOKEN and LINE_USER_ID from environment (.env).
    /// If LINE_NOTIFY_DISABLED=1, prepares payload without sending (status_code=200, disabled=True).
    /// Example: s" Build completed successfully!" line-notify .
last :: safe=False
