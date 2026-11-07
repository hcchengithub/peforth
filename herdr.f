\ herdr.f - Herdr multi-pane integration vocabulary
\ peforth 2.1.0

\ --- 1. Pane Context & Identification ---

code herdr-current-pane
    import json
    import os
    import shutil
    import subprocess

    if os.environ.get("HERDR_ENV") != "1":
        raise KernelError("Not running inside Herdr (HERDR_ENV != 1)")
    inherited = os.environ.get("HERDR_PANE_ID")
    if inherited:
        vm.push(inherited)
    else:
        herdr = shutil.which("herdr") or shutil.which("herdr.exe")
        if not herdr:
            raise KernelError("Could not find the Herdr CLI on PATH")
        completed = subprocess.run([herdr, "pane", "current", "--current"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if completed.returncode != 0:
            raise KernelError(f"Herdr error: {completed.stderr.strip() or completed.stdout.strip()}")
        data = json.loads(completed.stdout)
        vm.push(data["result"]["pane"]["pane_id"])
    end-code
    // ( -- pane-id ) Resolve and verify this process's live Herdr pane context.
    last :: safe=True

code herdr-set-pane-id
    import json
    import os
    import shutil
    import subprocess

    mode = vm.pop()
    if mode not in ("show", "clear"):
        raise KernelError("herdr-set-pane-id expects 'show' or 'clear'")
    if os.environ.get("HERDR_ENV") != "1":
        raise KernelError("Not running inside Herdr (HERDR_ENV != 1)")
    herdr = shutil.which("herdr") or shutil.which("herdr.exe")
    if not herdr:
        raise KernelError("Could not find the Herdr CLI on PATH")

    def herdr_json(arguments):
        completed = subprocess.run(
            [herdr, *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if completed.returncode != 0:
            raise KernelError(completed.stderr.strip() or completed.stdout.strip() or f"Herdr exited with status {completed.returncode}")
        try:
            return json.loads(completed.stdout)
        except Exception as exc:
            raise KernelError(f"Herdr returned invalid JSON: {completed.stdout!r}") from exc

    current = herdr_json(["pane", "current", "--current"])
    workspace_id = current["result"]["pane"]["workspace_id"]
    pane_rows = herdr_json(["pane", "list", "--workspace", workspace_id])["result"]["panes"]
    pane_ids = [row["pane_id"] for row in pane_rows]
    if not pane_ids:
        raise KernelError(f"No panes found in workspace {workspace_id}")
    for pane_id in pane_ids:
        if mode == "show":
            herdr_json(["pane", "rename", pane_id, pane_id])
        else:
            herdr_json(["pane", "rename", pane_id, "--clear"])
    vm.push({"action": mode, "workspace_id": workspace_id, "pane_ids": pane_ids})
    end-code
    // ( mode -- result ) Set or clear pane names in current Herdr workspace.
    last :: safe=True

: herdr-show-pane-id ( -- )
    s" show" herdr-set-pane-id stringify . cr
    ;
    // ( -- ) Set each pane name in current Herdr workspace to its pane ID.
    last :: safe=True

: herdr-clear-pane-id ( -- )
    s" clear" herdr-set-pane-id stringify . cr
    ;
    // ( -- ) Clear custom names from all panes in current Herdr workspace.
    last :: safe=True

\ --- 2. Read-Only Screen Inspection ---

code herdr-screen-read
    import json
    import os
    import shutil
    import subprocess

    line_count = 80
    if vm.dstack and isinstance(vm.dstack[-1], int) and not isinstance(vm.dstack[-1], bool):
        line_count = vm.pop()
    pane_id = str(vm.pop())

    herdr = shutil.which("herdr") or shutil.which("herdr.exe")
    if not herdr:
        raise KernelError("Could not find the Herdr CLI on PATH")

    completed = subprocess.run(
        [herdr, "pane", "read", pane_id, "--source", "visible", "--lines", str(line_count)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    if completed.returncode != 0:
        raise KernelError(f"Herdr error: {completed.stderr.strip() or completed.stdout.strip()}")
    vm.push(completed.stdout)
    end-code
    // ( pane-id [line-count] -- snapshot ) Read visible text; line-count defaults to 80.
    last :: safe=True

code herdr-screen-tail
    import json
    import os
    import shutil
    import subprocess

    line_count = 80
    if vm.dstack and isinstance(vm.dstack[-1], int) and not isinstance(vm.dstack[-1], bool):
        line_count = vm.pop()
    pane_id = str(vm.pop())

    herdr = shutil.which("herdr") or shutil.which("herdr.exe")
    if not herdr:
        raise KernelError("Could not find the Herdr CLI on PATH")

    completed = subprocess.run(
        [herdr, "pane", "read", pane_id, "--source", "recent-unwrapped", "--lines", str(line_count)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    if completed.returncode != 0:
        raise KernelError(f"Herdr error: {completed.stderr.strip() or completed.stdout.strip()}")
    vm.push(completed.stdout)
    end-code
    // ( pane-id [line-count] -- snapshot ) Read recent unwrapped output; line-count defaults to 80.
    last :: safe=True

\ --- 3. Mutating Screen Operations (Unsafe: triggers security approval under untrusted AI task) ---

code herdr-screen-send-text
    import json
    import os
    import shutil
    import subprocess

    text = str(vm.pop())
    pane_id = str(vm.pop())

    herdr = shutil.which("herdr") or shutil.which("herdr.exe")
    if not herdr:
        raise KernelError("Could not find the Herdr CLI on PATH")

    completed = subprocess.run(
        [herdr, "pane", "send-text", pane_id, text],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    if completed.returncode != 0:
        raise KernelError(f"Herdr error: {completed.stderr.strip() or completed.stdout.strip()}")
    vm.push({"pane_id": pane_id, "operation": "send_text", "text": text, "success": True})
    end-code
    // ( pane-id text -- result ) Send text to the selected pane.
    last :: safe=False

code herdr-screen-send-keys
    import json
    import os
    import shutil
    import subprocess

    raw_keys = vm.pop()
    if isinstance(raw_keys, str):
        keys = [raw_keys]
    elif isinstance(raw_keys, list):
        keys = [str(k) for k in raw_keys]
    else:
        raise KernelError("herdr-screen-send-keys expects key string or list of key strings")
    pane_id = str(vm.pop())

    herdr = shutil.which("herdr") or shutil.which("herdr.exe")
    if not herdr:
        raise KernelError("Could not find the Herdr CLI on PATH")

    completed = subprocess.run(
        [herdr, "pane", "send-keys", pane_id, *keys],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    if completed.returncode != 0:
        raise KernelError(f"Herdr error: {completed.stderr.strip() or completed.stdout.strip()}")
    vm.push({"pane_id": pane_id, "operation": "send_keys", "keys": keys, "success": True})
    end-code
    // ( pane-id keys -- result ) Send key names to the selected pane.
    last :: safe=False

code herdr-screen-run
    import json
    import os
    import shutil
    import subprocess

    command = str(vm.pop())
    pane_id = str(vm.pop())

    herdr = shutil.which("herdr") or shutil.which("herdr.exe")
    if not herdr:
        raise KernelError("Could not find the Herdr CLI on PATH")

    completed = subprocess.run(
        [herdr, "pane", "run", pane_id, command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    if completed.returncode != 0:
        raise KernelError(f"Herdr error: {completed.stderr.strip() or completed.stdout.strip()}")
    vm.push({"pane_id": pane_id, "operation": "run", "command": command, "success": True})
    end-code
    // ( pane-id command -- result ) Run a command in the selected pane.
    last :: safe=False
