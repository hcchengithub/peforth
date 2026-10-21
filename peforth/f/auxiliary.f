\ Auxiliary words are optional conveniences outside the core Forth dictionary.

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
// Like for ... next, a zero count still enters the body once.

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

code lcd-backlight
    import json
    level = vm.pop()
    if isinstance(level, bool) or not isinstance(level, (int, float)) or int(level) != level:
        raise ValueError("lcd-backlight expects an integer brightness from 0 to 100.")
    level = int(level)
    if not 0 <= level <= 100:
        raise ValueError("lcd-backlight brightness must be from 0 to 100.")
    script = (
        "$method = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods; "
        f"$result = Invoke-CimMethod -InputObject $method -MethodName WmiSetBrightness -Arguments @{{Timeout=1; Brightness={level}}}; "
        "$current = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness | Select-Object -ExpandProperty CurrentBrightness; "
        "[pscustomobject]@{CurrentBrightness=$current} | ConvertTo-Json -Compress"
    )
    vm.push(script)
    yield from vm.call(vm.tick("run_pwsh"))
    result = vm.pop()
    if not isinstance(result, dict) or result.get("exit_code") != 0:
        detail = result.get("stderr", repr(result)) if isinstance(result, dict) else repr(result)
        raise RuntimeError("lcd-backlight failed: " + detail)
    try:
        confirmed = json.loads(result.get("stdout", "").strip()).get("CurrentBrightness")
    except Exception as exc:
        raise RuntimeError("Could not verify lcd-backlight result: " + str(exc))
    if confirmed != level:
        raise RuntimeError(f"Requested {level}%, but Windows reports {confirmed}%.")
    print(f"LCD backlight set to {confirmed}%.")
end-code
// ( n -- ) Set the laptop LCD backlight to an integer percentage from 0 to 100.
/// Uses Windows WMI and verifies the reported brightness; reports an error if the setting fails.
