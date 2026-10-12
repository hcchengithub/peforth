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
