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
    py> [[1319,160],[1175,160],[740,320],[831,320]] (play-notes)
    ;
    // ( -- ) Play the first Nokia Tune phrase (4 notes) asynchronously.
    last :: safe=True

: nokia2 ( -- )
    py> [[988,160],[880,160],[554,320],[659,320],[880,640]] (play-notes)
    ;
    // ( -- ) Play the final Nokia Tune phrase (5 notes, long finish) asynchronously.
    last :: safe=True
