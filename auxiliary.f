\ auxiliary.f - Auxiliary words and system utilities for peforth
\ peforth 2.1.0

\ --- 1. Terminal Utilities ---

code cls
    print("\x1b[2J\x1b[H", end="", flush=True)
    end-code
    // ( -- ) Clear visible terminal screen and move cursor to top-left.
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

