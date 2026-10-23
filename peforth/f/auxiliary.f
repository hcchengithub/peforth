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

