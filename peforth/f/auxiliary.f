\ Additional auxiliary words ported from peforth v1.33.
code dir
    obj=vm.pop()
    vm.push([name for name in dir(obj) if not name.startswith("_") and not name.endswith("_")])
    end-code // ( object -- names ) List public member names.
    /// Filters names beginning or ending with an underscore.
code _dir_
    vm.push(dir(vm.pop()))
    end-code // ( object -- names ) Return Python's complete dir() result.
    /// Includes private and special names.
code dict>keys
    vm.push(list(vm.pop().keys()))
    end-code // ( dict -- keys ) Return dictionary keys as a list.
    /// The result is a list, not a dict_keys view.
code keys
    obj=vm.pop()
    if isinstance(obj,dict): vm.push(list(obj.keys()))
    else: vm.push([name for name in dir(obj) if not name.startswith("_") and not name.endswith("_")])
    end-code // ( object -- keys ) Return dict keys or public members as a list.
    /// Both input cases return a list.
code <text>
    import re
    chunks=[]
    depth=1
    boundary=re.compile(r"</text>|<text>")
    while depth:
        remaining=vm.input.remaining
        match=boundary.search(remaining)
        if match is None: raise RuntimeError("Unclosed <text>")
        chunk=vm.input.read(until=boundary)
        tag=remaining[len(chunk):match.end()]
        chunks.append(chunk)
        if tag=="<text>":
            depth+=1
            chunks.append(tag)
        else:
            depth-=1
            if depth: chunks.append(tag)
    text="".join(chunks)
    if text.startswith(" "): text=text[1:]
    if vm.compiling: vm.literal(text)
    else: vm.push(text)
    end-code immediate // ( <text> -- string ) Read a possibly nested text block.
    /// Inner <text> tags are retained.
code </text>
    end-code immediate // ( -- ) Closing delimiter consumed by <text>.
code <comment>
    import re
    depth=1
    boundary=re.compile(r"<comment>|</comment>")
    while depth:
        remaining=vm.input.remaining
        match=boundary.search(remaining)
        if match is None: raise RuntimeError("Unclosed <comment>")
        vm.input.read(until=boundary)
        tag=remaining[match.start():match.end()]
        if tag=="<comment>": depth+=1
        else: depth-=1
    end-code immediate
code </comment>
    end-code immediate // ( -- ) Closing delimiter consumed by <comment>.
code -->
    value=vm.pop()
    source=vm.input.tib
    line_start=source.rfind("\n",0,vm.input.itib)+1
    command=source[line_start:vm.input.itib].strip()
    print(f"{command} {value} ({type(value)})")
    end-code// ( result -- ) Print command line, and result.
    /// Includes the Python type.
code ==>
    value=vm.pop()
    source=vm.input.tib
    line_start=source.rfind("\n",0,vm.input.itib)+1
    command=source[line_start:vm.input.itib].strip()
    print(f"\n{command} {value} ({type(value)})")
    end-code // ( result -- ) Print a blank line, command line, and result.
    /// Includes the Python type.
code (space)
    vm.push(" ")
    end-code // ( -- string ) Push one space.
code (')
    name=vm.pop()
    word=vm.tick(name) if isinstance(name,str) else None
    if word is None: raise RuntimeError(f"Unknown word: {name}")
    vm.push(word)
    end-code // ( name -- word ) Look up the word named by the string on TOS.
    /// Unlike tick, it takes the name from the stack.

\ Auxiliary words are optional conveniences outside the core Forth dictionary.

code sleep
    import time

    milliseconds = vm.pop()
    if isinstance(milliseconds, bool) or not isinstance(milliseconds, int):
        raise TypeError('sleep expects an integer number of milliseconds')
    if milliseconds < 0:
        raise ValueError('sleep milliseconds must be non-negative')
    time.sleep(milliseconds / 1000)
    end-code
    // ( milliseconds -- ) Suspend the current Forth task for the given number of milliseconds.
    /// Blocks this VM's current Forth task until the delay expires; the VM cannot interpret other input while sleeping.
    /// milliseconds must be a non-negative integer; zero returns immediately.

code cls
    print("\x1b[2J\x1b[H", end="", flush=True)
    end-code
    // ( -- ) Clear the visible terminal screen and move the cursor to the top-left.
    /// Output ANSI escape sequences; requires an ANSI-compatible terminal.

code stringify
    import ast
    import json

    value = vm.pop()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
                pass

    try:
        result = json.dumps(value, indent=2, ensure_ascii=False, default=repr)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"stringify cannot encode this value as JSON: {exc}") from exc
    vm.push(result)
    end-code
    // ( object -- pretty-string ) Convert a Python value to indented JSON text.
    /// String input is parsed as JSON or a Python literal when possible; other text is quoted as JSON.
    /// Unsupported nested values are represented with repr.

\ ---- Task T-stack based interpretation-time flow control ------------------

code (itib@)
    vm.push(vm.input.itib)
    end-code

code (itib!)
    offset = vm.pop()
    if not isinstance(offset, int) or isinstance(offset, bool) or not 0 <= offset <= len(vm.input.tib):
        raise ForthError("Invalid TIB input offset")
    vm.input.itib = offset
    end-code

code (interpret-only)
    if vm.compiling:
        raise ForthError("This flow-control word can only be used while interpreting")
    end-code

code (skip-conditional)
    stop_at_else = bool(vm.pop())
    vm.tstack.append(1)
    try:
        while True:
            token = vm.input.read()
            if token is None:
                end = "[else] or [then]" if stop_at_else else "[then]"
                raise ForthError(f"Unmatched conditional; expected {end}")
            quoted = vm.tick(token)
            if quoted is not None and getattr(quoted, "type", "") == "string-quote":
                vm.input.read(until=quoted.value)
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

code [if]
    if not vm.pop():
        vm.push(True)
        yield from vm.call(vm.tick("(skip-conditional)"))
    end-code immediate
    // ( flag -- ) Interpret the true arm; skip to the matching [else] or [then] when false.
    // Nested [if] groups are tracked on this Task's T-stack.

code [else]
    vm.push(False)
    yield from vm.call(vm.tick("(skip-conditional)"))
    end-code immediate
    // ( -- ) Skip the false arm of the matching [if] group.

: [then] ; immediate
    // ( -- ) End a bracketed conditional group.

: [begin] (interpret-only) (itib@) >t ; immediate
    // ( -- ) Save this input position as the start of an interpretation-time loop.

: [again] (interpret-only) t@ (itib!) ; immediate
    // ( -- ) Repeat the current [begin] loop unconditionally.

: [until]
    (interpret-only)
    if t> drop else t@ (itib!) then
    ; immediate
    // ( flag -- ) Repeat the current [begin] loop while flag is false.

: [for] (interpret-only) (itib@) >t >t ; immediate
    // ( count -- ) Start an interpretation-time counted loop; [next] checks after each pass.
    /// Like for ... next, a zero count still enters the body once.

: [next]
    (interpret-only)
    t> 1- dup >t 0 >
    if
        t> t> dup (itib!) >t >t
    else
        t> t> drop drop
    then
    ; immediate
    // ( -- ) Decrement the current [for] count; rewind to its body or discard its state.

code run-monitor
    import os
    import subprocess
    import sys
    from pathlib import Path

    venv = Path(sys.prefix)
    monitor = venv.parent / "tools" / "peforth_logging_monitor.py"
    if not monitor.is_file():
        raise RuntimeError(f"Monitor script not found: {monitor}")

    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv)
    env["PATH"] = str(venv / "bin") + os.pathsep + env.get("PATH", "")

    subprocess.run([sys.executable, str(monitor)], env=env, check=False)
    end-code
    // ( -- ) Run the peforth diagnostic logging monitor in the foreground.
    /// Uses the current Python VENV and configured SQLite diagnostics database.
    /// Press Ctrl-C to stop the monitor and return to Forth.

: system_info
    py> system_info
    ;
    // ( -- info ) Return the startup System Info prepared by the Python runtime.

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

: nokia2 ( -- )
    s" $child = '$notes = @(@(988,160),@(880,160),@(554,320),@(659,320),@(880,640)); foreach ($n in $notes) { [Console]::Beep($n[0], $n[1]); Start-Sleep -Milliseconds 25 }'; $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($child)); $pwsh = (Get-Command pwsh -ErrorAction Stop).Source; Start-Process -FilePath $pwsh -WindowStyle Hidden -ArgumentList @('-NoLogo','-NoProfile','-NonInteractive','-WindowStyle','Hidden','-EncodedCommand',$encoded) | Out-Null" run_pwsh drop
    ;
    // ( -- ) Start the final Nokia Tune section asynchronously.
    /// Plays the last five notes, including the long final note. Uses the same background PowerShell playback path as nokia.

: nokia ( -- )
    s" $child = '$notes = @(@(1319,160),@(1175,160),@(740,320),@(831,320),@(1109,160),@(988,160),@(587,320),@(659,320)); foreach ($n in $notes) { [Console]::Beep($n[0], $n[1]); Start-Sleep -Milliseconds 25 }'; $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($child)); $pwsh = (Get-Command pwsh -ErrorAction Stop).Source; Start-Process -FilePath $pwsh -WindowStyle Hidden -ArgumentList @('-NoLogo','-NoProfile','-NonInteractive','-WindowStyle','Hidden','-EncodedCommand',$encoded) | Out-Null" run_pwsh drop
    ;
    // ( -- ) Start the first two Nokia Tune sections asynchronously.
    /// Launches a hidden PowerShell child process and returns without waiting for playback.
    /// Plays the first eight notes with 25 ms gaps, using PowerShell Console.Beep.

code (sudo)
    import os
    import pty

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

    print(
        "[sudo] Enter your password in this terminal if prompted.",
        flush=True,
    )

    output_limit = 65536
    captured = bytearray()
    truncated = [False]

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

    vm.push({
        "exit_code": os.waitstatus_to_exitcode(status),
        "output": captured.decode("utf-8", errors="replace"),
        "truncated": truncated[0],
    })
    end-code
    // ( command-line -- result-dict ) Run a command script as root in an interactive PTY.
    /// The complete string is passed to sudo -- bash -c; every line runs as root.
    /// PTY output is shown live and returned as combined output, capped at 65536 bytes.
    /// Returns a dictionary with exit_code, output, and truncated; an error key appears for invalid input.
    /// Blocks until the command exits. sudo normally disables echo while reading the password.
    /// Before invoking this word for a user, tell them the password prompt may appear in this terminal.

: sudo "" word (sudo) ;
    // ( -- result-dict ) Run the remaining TIB text as a root command script.
    /// Consumes all remaining TIB text, including newlines, and passes it to (sudo).
    /// Submit multiline commands as one TIB input; separately submitted lines are not collected together.
    /// Put sudo last in the Forth submission: all following text becomes the root shell script.
    /// The result dictionary is left on the data stack; use stringify . in the next input to display it.

code (bash)
    import os
    import pty

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

    vm.push({
        "exit_code": os.waitstatus_to_exitcode(status),
        "output": captured.decode("utf-8", errors="replace"),
        "truncated": truncated[0],
    })
    end-code
    // ( command-line -- result-dict ) Execute a command script in interactive Bash on a PTY.
    /// Bash inherits the current working directory and environment, and reads interactive startup configuration.
    /// PTY output is shown live and returned as combined output, capped at 65536 bytes.
    /// Returns a dictionary with exit_code, output, and truncated.
    /// Blocks until the command exits; terminal input and control keys are forwarded to Bash.

: bash "" word (bash) ;
    // ( -- result-dict ) Run the remaining TIB text in interactive Bash.
    /// Consumes all remaining TIB text, including newlines, and passes it to (bash).
    /// Submit multiline commands as one TIB input; separately submitted lines are not collected together.
    /// The command runs with the current user's privileges, not sudo.
    /// The result dictionary is left on the data stack; use stringify . in the next input to display it.
