code herdr-set-pane-id
	import json
	import os
	import shutil
	import subprocess

	mode = vm.pop()
	if mode not in ("show", "clear"):
		raise ValueError("herdr-set-pane-id expects 'show' or 'clear'")
	if os.environ.get("HERDR_ENV") != "1":
		raise RuntimeError("Not running inside Herdr")
	herdr = shutil.which("herdr") or shutil.which("herdr.exe")
	if not herdr:
		raise RuntimeError("Could not find the Herdr CLI on PATH")

	def herdr_json(arguments):
		completed = subprocess.run(
			[herdr, *arguments],
			capture_output=True,
			text=True,
			encoding="utf-8",
			errors="replace",
			timeout=30,
		)
		if completed.returncode:
			raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or
							   f"Herdr exited with status {completed.returncode}")
		try:
			return json.loads(completed.stdout)
		except json.JSONDecodeError as exc:
			raise RuntimeError(f"Herdr returned invalid JSON: {completed.stdout!r}") from exc

	current = herdr_json(["pane", "current", "--current"])
	workspace_id = current["result"]["pane"]["workspace_id"]
	pane_rows = herdr_json(["pane", "list", "--workspace", workspace_id])["result"]["panes"]
	pane_ids = [row["pane_id"] for row in pane_rows]
	if not pane_ids:
		raise RuntimeError(f"No panes found in workspace {workspace_id}")
	for pane_id in pane_ids:
		if mode == "show":
			herdr_json(["pane", "rename", pane_id, pane_id])
		else:
			herdr_json(["pane", "rename", pane_id, "--clear"])
	vm.push({"action": mode, "workspace_id": workspace_id, "pane_ids": pane_ids})
	end-code
	// ( mode -- result ) Set or clear pane names in the current Herdr workspace.
	/// Use mode 'show' to name each pane after its ID; use 'clear' to remove custom names.
	/// Requires a Herdr-managed pane. Returns action, workspace_id, and pane_ids.

: herdr-show-pane-id s" show" herdr-set-pane-id stringify . ; 
	// ( -- ) Set each pane name in the current Herdr workspace to its pane ID.
	/// Looks up the current workspace and pane list on every call.
	/// Requires HERDR_ENV=1 and the Herdr CLI on PATH. Prints a JSON summary.

: herdr-clear-pane-id s" clear" herdr-set-pane-id stringify . ; 
	// ( -- ) Clear custom names from all panes in the current Herdr workspace.
	/// Looks up the current workspace and pane list on every call; does not close or move panes.
	/// Requires HERDR_ENV=1 and the Herdr CLI on PATH. Prints a JSON summary.

code herdr-current-pane
	from peforth import ai_tools

	vm.push(ai_tools._herdr_current_pane())
	end-code
	// ( -- pane-id ) Resolve and verify this process's live Herdr pane context.

code herdr-screen-read
	from peforth import ai_tools

	line_count = 80
	if vm.stack and type(vm.stack[-1]) is int:
		line_count = vm.pop()
	pane_id = vm.pop()
	vm.push(ai_tools._herdr_screen_read(pane_id, "visible", line_count))
	end-code
	// ( pane-id [line-count] -- snapshot ) Read visible text; line-count defaults to 80.

code herdr-screen-tail
	from peforth import ai_tools

	line_count = 80
	if vm.stack and type(vm.stack[-1]) is int:
		line_count = vm.pop()
	pane_id = vm.pop()
	vm.push(ai_tools._herdr_screen_read(pane_id, "recent-unwrapped", line_count))
	end-code
	// ( pane-id [line-count] -- snapshot ) Read recent unwrapped output; line-count defaults to 80.

code herdr-screen-send-text
	from peforth import ai_tools

	text = vm.pop()
	pane_id = vm.pop()
	result = yield from ai_tools._herdr_forth_operation(vm, "send_text", pane_id, text)
	vm.push(result)
	end-code
	// ( pane-id text -- result ) Send text to the selected pane through the shared ai-approve flow.

code herdr-screen-send-keys
	from peforth import ai_tools

	keys = vm.pop()
	pane_id = vm.pop()
	result = yield from ai_tools._herdr_forth_operation(vm, "send_keys", pane_id, keys)
	vm.push(result)
	end-code
	// ( pane-id keys -- result ) Send key names. Example: char w2:p4 char ctrl+a -1 slice herdr-screen-send-keys.
	/// Key names are passed through to Herdr CLI; syntax is version-specific, with no fixed peforth key list.
	/// Examples: printable characters, backspace, enter, tab, esc/escape, arrows, f12; modifiers ctrl/shift/alt/cmd/super can combine (ctrl+shift+alt+left).
	/// Named punctuation includes minus, comma, ampersand, plus, and backtick. On the tested Herdr build, backspace works; home/end/delete did not.
	/// These examples are not exhaustive; check herdr pane send-keys --help and do not assume undocumented names.
	/// For two keys: char w2:p4 char ctrl+a char enter -2 slice herdr-screen-send-keys.

code herdr-screen-run
	from peforth import ai_tools

	command = vm.pop()
	pane_id = vm.pop()
	result = yield from ai_tools._herdr_forth_operation(vm, "run", pane_id, command)
	vm.push(result)
	end-code
	// ( pane-id command -- result ) Run a command in the selected pane through the shared ai-approve flow.
