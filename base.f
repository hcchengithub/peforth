\ base.f - peforth v2.1.0 standard vocabulary
\ Inherited from peforth 2.0.0, aligned with Project K v2.1.0 kernel and task security model.

\ =====================================================================
\ 1. Stack Manipulation
\ =====================================================================

code pick
    n = vm.pop()
    if not isinstance(n, int) or isinstance(n, bool) or n < 0 or n >= len(vm.dstack):
        raise KernelError("pick index out of range")
    vm.push(vm.dstack[-n-1])
    end-code
    // ( ... xj ... j -- ... xj ... xj ) Copy the j-th item to top.
    last :: safe=True

code roll
    n = vm.pop()
    if not isinstance(n, int) or isinstance(n, bool) or n < 0 or n >= len(vm.dstack):
        raise KernelError("roll index out of range")
    vm.push(vm.dstack.pop(-n-1))
    end-code
    // ( ... xj ... j -- ... xj ) Move the j-th item to TOS.
    last :: safe=True

code dup
    if not vm.dstack:
        raise KernelError("stack underflow")
    vm.push(vm.dstack[-1])
    end-code
    // ( x -- x x ) Duplicate the top item on the data stack.
    last :: safe=True

code drop
    if not vm.dstack:
        raise KernelError("stack underflow")
    vm.pop()
    end-code
    // ( x -- ) Discard top item.
    last :: safe=True

code dropall
    vm.dstack.clear()
    end-code
    // ( ... -- ) Clear the entire data stack.
    last :: safe=True

code swap
    if len(vm.dstack) < 2:
        raise KernelError("swap needs two stack items")
    b, a = vm.pop(), vm.pop()
    vm.push(b, a)
    end-code
    // ( x1 x2 -- x2 x1 ) Exchange top two stack items.
    last :: safe=True

code over
    if len(vm.dstack) < 2:
        raise KernelError("over needs two stack items")
    vm.push(vm.dstack[-2])
    end-code
    // ( x1 x2 -- x1 x2 x1 ) Copy second item to top.
    last :: safe=True

code rot
    if len(vm.dstack) < 3:
        raise KernelError("rot needs three stack items")
    c, b, a = vm.pop(), vm.pop(), vm.pop()
    vm.push(b, c, a)
    end-code
    // ( x1 x2 x3 -- x2 x3 x1 ) Rotate top three items.
    last :: safe=True

: -rot
    rot rot ;
    // ( x1 x2 x3 -- x3 x1 x2 ) Rotate top three items in reverse.
    last :: safe=True

: nip
    swap drop ;
    // ( x1 x2 -- x2 ) Drop the second item.
    last :: safe=True

: 2dup
    over over ;
    // ( x1 x2 -- x1 x2 x1 x2 ) Duplicate top two items.
    last :: safe=True

: 2drop
    drop drop ;
    // ( x1 x2 -- ) Drop top two items.
    last :: safe=True

code depth
    vm.push(len(vm.dstack))
    end-code
    // ( -- n ) Return number of items on data stack.
    last :: safe=True

code slice
    n = vm.pop()
    if not isinstance(n, int) or isinstance(n, bool):
        raise KernelError("slice expects an integer")
    start = max(0, len(vm.dstack) + n) if n < 0 else 0
    end = len(vm.dstack) if n < 0 else min(n, len(vm.dstack))
    result = vm.dstack[start:end]
    del vm.dstack[start:end]
    vm.push(result)
    end-code
    // ( ... cells -n -- ... [cells] ) Move the last -n cells into a list.
    last :: safe=True

\ =====================================================================
\ 2. Return Stack and Temporary Stack (Task Private)
\ =====================================================================

code >r
    vm.rstack.append(vm.pop())
    end-code
    // ( x -- ) ( R: -- x ) Move item to return stack.
    last :: safe=True

code r>
    if not vm.rstack:
        raise KernelError("rstack underflow")
    vm.push(vm.rstack.pop())
    end-code
    // ( -- x ) ( R: x -- ) Move item from return stack.
    last :: safe=True

code r@
    if not vm.rstack:
        raise KernelError("rstack underflow")
    vm.push(vm.rstack[-1])
    end-code
    // ( -- x ) ( R: x -- x ) Copy top of return stack.
    last :: safe=True

code rdrop
    if not vm.rstack:
        raise KernelError("rstack underflow")
    vm.rstack.pop()
    end-code
    // ( -- ) ( R: x -- ) Drop top of return stack.
    last :: safe=True

code >t
    vm.tstack.append(vm.pop())
    end-code
    // ( x -- ) ( T: -- x ) Push onto temporary stack.
    last :: safe=True

code t@
    if not vm.tstack:
        raise KernelError("tstack underflow")
    vm.push(vm.tstack[-1])
    end-code
    // ( -- x ) ( T: x -- x ) Copy top of temporary stack.
    last :: safe=True

code t>
    if not vm.tstack:
        raise KernelError("tstack underflow")
    vm.push(vm.tstack.pop())
    end-code
    // ( -- x ) ( T: x -- ) Pop from temporary stack.
    last :: safe=True

\ =====================================================================
\ 3. Arithmetic and Logic
\ =====================================================================

code +
    b, a = vm.pop(), vm.pop()
    vm.push(a + b)
    end-code
    // ( n1 n2 -- n3 ) Add.
    last :: safe=True

code -
    b, a = vm.pop(), vm.pop()
    vm.push(a - b)
    end-code
    // ( n1 n2 -- n3 ) Subtract.
    last :: safe=True

code *
    b, a = vm.pop(), vm.pop()
    vm.push(a * b)
    end-code
    // ( n1 n2 -- n3 ) Multiply.
    last :: safe=True

code /
    b, a = vm.pop(), vm.pop()
    vm.push(a / b)
    end-code
    // ( n1 n2 -- n3 ) Divide.
    last :: safe=True

code mod
    b, a = vm.pop(), vm.pop()
    vm.push(a % b)
    end-code
    // ( n1 n2 -- rem ) Remainder.
    last :: safe=True

code 1+
    vm.push(vm.pop() + 1)
    end-code
    // ( n -- n+1 ) Increment by 1.
    last :: safe=True

code 1-
    vm.push(vm.pop() - 1)
    end-code
    // ( n -- n-1 ) Decrement by 1.
    last :: safe=True

code 2+
    vm.push(vm.pop() + 2)
    end-code
    // ( n -- n+2 ) Increment by 2.
    last :: safe=True

code 2-
    vm.push(vm.pop() - 2)
    end-code
    // ( n -- n-2 ) Decrement by 2.
    last :: safe=True

code abs
    vm.push(abs(vm.pop()))
    end-code
    // ( n -- |n| ) Absolute value.
    last :: safe=True

code negate
    vm.push(-vm.pop())
    end-code
    // ( n -- -n ) Negate.
    last :: safe=True

code max
    b, a = vm.pop(), vm.pop()
    vm.push(max(a, b))
    end-code
    // ( a b -- max ) Keep the larger value.
    last :: safe=True

code min
    b, a = vm.pop(), vm.pop()
    vm.push(min(a, b))
    end-code
    // ( a b -- min ) Keep the smaller value.
    last :: safe=True

code =
    b, a = vm.pop(), vm.pop()
    vm.push(a == b)
    end-code
    // ( x1 x2 -- flag ) Test equality.
    last :: safe=True

code <>
    b, a = vm.pop(), vm.pop()
    vm.push(a != b)
    end-code
    // ( x1 x2 -- flag ) Test inequality.
    last :: safe=True

code !=
    b, a = vm.pop(), vm.pop()
    vm.push(a != b)
    end-code
    // ( x1 x2 -- flag ) Test inequality.
    last :: safe=True

code ==
    b, a = vm.pop(), vm.pop()
    vm.push(bool(a) == bool(b))
    end-code
    // ( a b -- flag ) Compare truth values.
    last :: safe=True

code <
    b, a = vm.pop(), vm.pop()
    vm.push(a < b)
    end-code
    // ( n1 n2 -- flag ) Test less than.
    last :: safe=True

code >
    b, a = vm.pop(), vm.pop()
    vm.push(a > b)
    end-code
    // ( n1 n2 -- flag ) Test greater than.
    last :: safe=True

code <=
    b, a = vm.pop(), vm.pop()
    vm.push(a <= b)
    end-code
    // ( n1 n2 -- flag ) Test less than or equal.
    last :: safe=True

code >=
    b, a = vm.pop(), vm.pop()
    vm.push(a >= b)
    end-code
    // ( n1 n2 -- flag ) Test greater than or equal.
    last :: safe=True

code 0=
    vm.push(vm.pop() == 0)
    end-code
    // ( x -- flag ) Test zero.
    last :: safe=True

code 0<
    vm.push(vm.pop() < 0)
    end-code
    // ( n -- flag ) Test negative.
    last :: safe=True

code not
    vm.push(not vm.pop())
    end-code
    // ( x -- flag ) Logical NOT.
    last :: safe=True

code and
    b, a = vm.pop(), vm.pop()
    vm.push(bool(a and b))
    end-code
    // ( x1 x2 -- flag ) Logical AND.
    last :: safe=True

code or
    b, a = vm.pop(), vm.pop()
    vm.push(bool(a or b))
    end-code
    // ( x1 x2 -- flag ) Logical OR.
    last :: safe=True

code AND
    b, a = vm.pop(), vm.pop()
    vm.push(a & b)
    end-code
    // ( n1 n2 -- n3 ) Bitwise AND.
    last :: safe=True

code OR
    b, a = vm.pop(), vm.pop()
    vm.push(a | b)
    end-code
    // ( n1 n2 -- n3 ) Bitwise OR.
    last :: safe=True

code NOT
    vm.push(~vm.pop())
    end-code
    // ( n -- ~n ) Bitwise NOT.
    last :: safe=True

code XOR
    b, a = vm.pop(), vm.pop()
    vm.push(a ^ b)
    end-code
    // ( n1 n2 -- n3 ) Bitwise XOR.
    last :: safe=True

code <<
    b, a = vm.pop(), vm.pop()
    vm.push(a << b)
    end-code
    // ( value n -- value<<n ) Shift left n bits.
    last :: safe=True

code >>
    b, a = vm.pop(), vm.pop()
    vm.push(a >> b)
    end-code
    // ( value n -- value>>n ) Shift right n bits.
    last :: safe=True

code within
    high, low, val = vm.pop(), vm.pop(), vm.pop()
    vm.push(low <= val < high)
    end-code
    // ( x low high -- flag ) Test if low <= x < high.
    last :: safe=True

\ =====================================================================
\ 4. Literals, Constants, and Python Types
\ =====================================================================

code BL
    vm.push(" ")
    end-code
    // ( -- " " ) Push a space string.
    last :: safe=True

code CR
    vm.push("\n")
    end-code
    // ( -- "\n" ) Push a newline string.
    last :: safe=True

code none
    vm.push(None)
    end-code
    // ( -- None ) Push Python None.
    last :: safe=True

code ""
    vm.push("")
    end-code
    // ( -- "" ) Push an empty string.
    last :: safe=True

code inf
    vm.push(float("inf"))
    end-code
    // ( -- inf ) Push infinity.
    last :: safe=True

code -inf
    vm.push(float("-inf"))
    end-code
    // ( -- -inf ) Push negative infinity.
    last :: safe=True

code nan
    vm.push(float("nan"))
    end-code
    // ( -- nan ) Push NaN.
    last :: safe=True

code int
    vm.push(int(vm.pop()))
    end-code
    // ( x -- int ) Convert to integer.
    last :: safe=True

code float
    vm.push(float(vm.pop()))
    end-code
    // ( x -- float ) Convert to float.
    last :: safe=True

code bool
    vm.push(bool(vm.pop()))
    end-code
    // ( x -- bool ) Convert to boolean.
    last :: safe=True

code str
    vm.push(str(vm.pop()))
    end-code
    // ( x -- str ) Convert to string.
    last :: safe=True

code list
    vm.push(list(vm.pop()))
    end-code
    // ( x -- list ) Convert to list.
    last :: safe=True

code dict
    vm.push(dict(vm.pop()))
    end-code
    // ( x -- dict ) Convert to dictionary.
    last :: safe=True

code set
    vm.push(set(vm.pop()))
    end-code
    // ( x -- set ) Convert to set.
    last :: safe=True

code tuple
    vm.push(tuple(vm.pop()))
    end-code
    // ( x -- tuple ) Convert to tuple.
    last :: safe=True

code type
    vm.push(type(vm.pop()))
    end-code
    // ( x -- type ) Return Python type.
    last :: safe=True

code {}
    vm.push({})
    end-code
    // ( -- dict ) Push an empty dictionary.
    last :: safe=True

code []
    vm.push([])
    end-code
    // ( -- list ) Push an empty list.
    last :: safe=True

code count
    if not vm.dstack:
        raise KernelError("count needs a stack item")
    vm.push(len(vm.dstack[-1]))
    end-code
    // ( x -- x n ) Leave x and push its length.
    last :: safe=True

code trim
    val = vm.pop()
    if not isinstance(val, str):
        raise KernelError("trim expects a string")
    vm.push(val.strip())
    end-code
    // ( string -- string' ) Strip leading and trailing whitespace.
    last :: safe=True

\ =====================================================================
\ 5. Strings and Display
\ =====================================================================

code .
    print(vm.pop(), end="", flush=True)
    end-code
    // ( x -- ) Output top stack value without trailing newline.
    last :: safe=True

code .s
    print(vm.dstack)
    end-code immediate
    // ( -- ) Display data stack non-destructively.
    last :: safe=True

code cr
    print()
    end-code
    // ( -- ) Print a newline.
    last :: safe=True

code space
    print(" ", end="", flush=True)
    end-code
    // ( -- ) Print a single space.
    last :: safe=True

code words
    line = vm.input.read(until="\n") if "\n" in vm.input.remaining else vm.input.rest()
    patterns = [p.lower() for p in line.strip().split() if p.strip()]
    if not patterns:
        matched = list(vm.words.keys())
    else:
        matched = [name for name in vm.words.keys() if all(p in name.lower() for p in patterns)]
    if matched:
        print(" ".join(matched))
    end-code immediate
    // ( [<patterns>] -- ) List words in dictionary filtered by pattern(s).
    /// If no patterns given, list all word names.
    /// If patterns given, list names containing all patterns (case-insensitive AND).
    last :: safe=True

code see
    name = vm.input.read()
    if not name:
        raise KernelError("see expects a word name")
    word = vm.tick(name)
    if word is None:
        raise KernelError(f"Unknown word: {name}")

    has_doc = bool(getattr(word, "help", "") or getattr(word, "comment", ""))
    if has_doc:
        help_text = word.help.strip() if getattr(word, "help", "") else ""
        if help_text:
            print(f"{word.name} {help_text}")
        else:
            print(word.name)
        if getattr(word, "comment", ""):
            for line in word.comment.splitlines():
                print(f"    {line}")
        print()

    print(word)

    if getattr(word, "category", "") == "colon" or isinstance(getattr(word, "action", None), tuple):
        parts = []
        for item in word.action:
            if hasattr(item, "name") and item.name:
                parts.append("does>" if item.name == "(does>)" else str(item.name))
            elif hasattr(item, "source") and item.source:
                parts.append(str(item.source))
            elif hasattr(item, "value"):
                if hasattr(item.value, "name"):
                    parts.append(f"['] {item.value.name}")
                elif isinstance(item.value, str):
                    parts.append(f's" {item.value}"')
                else:
                    parts.append(repr(item.value))
            elif isinstance(item, int):
                parts.append(str(item))
            elif callable(item):
                src = getattr(item, "name", None) or getattr(item, "source", None)
                if not src:
                    import inspect
                    try:
                        src = inspect.getsource(item).strip()
                    except Exception:
                        src = getattr(item, "__name__", repr(item))
                parts.append(str(src))
            else:
                parts.append(repr(item))
        imm = " immediate" if word.immediate else ""
        print(f": {word.name} {' '.join(parts)} ;{imm}")
    elif getattr(word, "category", "") == "constant" or (hasattr(word, "body") and word.category == "constant"):
        val = word.body[0] if hasattr(word, "body") and word.body else getattr(word, "value", None)
        print(f"{val!r} constant {word.name}")
    elif getattr(word, "category", "") == "variable" or (hasattr(word, "body") and word.category == "variable"):
        print(f"variable {word.name} (body: {word.body!r})")
    elif getattr(word, "category", "") == "created" or (hasattr(word, "body") and word.body is not None):
        print(f"created {word.name} (body: {word.body!r})")
    elif getattr(word, "source", ""):
        lines = [f"code {word.name}"]
        lines.append(word.source.rstrip())
        lines.append("end-code" + (" immediate" if word.immediate else ""))
        print("\n".join(lines))
    else:
        imm = " (immediate)" if word.immediate else ""
        print(f"Host word {word.name}: {word.action!r}{imm}")
    end-code immediate
    // ( <name> -- ) Display a word's definition and source.
    last :: safe=True

code s"
    text = vm.input.read(until='"')
    if text.startswith(' '):
        text = text[1:]
    if vm.compiling:
        vm.literal(text)
    else:
        vm.push(text)
    end-code immediate
    // ( <string"> -- text ) Parse string up to closing quote.
    last :: safe=True

code ."
    text = vm.input.read(until='"')
    if text.startswith(' '):
        text = text[1:]
    if vm.compiling:
        vm.literal(text)
        vm.comma('.')
    else:
        print(text, end="", flush=True)
    end-code immediate
    // ( <string"> -- ) Print string up to closing quote.
    last :: safe=True

code char
    tok = vm.input.read()
    if tok is None:
        raise KernelError("char expects a token")
    if vm.compiling:
        vm.literal(tok)
    else:
        vm.push(tok)
    end-code immediate
    // ( <token> -- string ) Read next token as string and push/compile it.
    last :: safe=True

code word
    delim = vm.pop()
    if not delim:
        val = vm.input.rest()
    elif delim == " " or delim == "\\s":
        val = vm.input.read()
    elif delim == chr(10) or delim == "\\n":
        val = vm.input.read(until=chr(10)) if chr(10) in vm.input.remaining else vm.input.rest()
    else:
        val = vm.input.read(until=delim)
    vm.push(val if val is not None else "")
    end-code
    // ( delim -- text ) Read text from input buffer up to delimiter.
    last :: safe=True

code tib.append
    txt = vm.pop()
    if not isinstance(txt, str):
        raise KernelError("tib.append expects string")
    vm.input.append(txt)
    end-code
    // ( text -- ) Append text to current input buffer.

\ =====================================================================
\ 6. Control Flow Engine and Structures
\ =====================================================================

code branch
    vm.frame.ip = vm.frame.colon_code[vm.frame.ip]
    end-code
    // ( -- ) Unconditional branch at runtime.
    last :: safe=True

code 0branch
    if not vm.pop():
        vm.frame.ip = vm.frame.colon_code[vm.frame.ip]
    else:
        vm.frame.ip += 1
    end-code
    // ( flag -- ) Conditional branch if flag is false at runtime.
    last :: safe=True

code doNext
    r = vm.rstack
    if not r:
        raise KernelError("rstack underflow in doNext")
    count = r[-1] - 1
    if count >= 0:
        r[-1] = count
        vm.frame.ip = vm.frame.colon_code[vm.frame.ip]
    else:
        r.pop()
        vm.frame.ip += 1
    end-code
    // ( -- ) Runtime loop counter step for 'next'.
    last :: safe=True

code here
    if not vm.compiling:
        raise KernelError("here only valid during compilation")
    vm.push(len(vm._builder.colon_code))
    end-code
    // ( -- addr ) Return the current compilation address in the definition body.
    last :: safe=True

code ,
    val = vm.pop()
    if vm.compiling:
        vm._builder.colon_code.append(val)
    else:
        target = vm.latest
        if target is None or not hasattr(target, "body") or target.body is None:
            raise KernelError("No created word body being populated")
        target.body.append(val)
    end-code
    // ( x -- ) Compile an operation into definition, or append to created word body.
    last :: safe=True

code !
    addr = vm.pop()
    val = vm.pop()
    if isinstance(addr, list):
        if not addr:
            addr.append(val)
        else:
            addr[0] = val
    elif isinstance(addr, int):
        if vm.compiling:
            vm._builder.colon_code[addr] = val
        else:
            raise KernelError("Integer address only valid during compilation")
    else:
        raise KernelError("! expects list or integer compilation address")
    end-code
    // ( val addr -- ) Store value into memory cell or compilation address.
    last :: safe=True

code @
    addr = vm.pop()
    if isinstance(addr, list):
        if not addr:
            raise KernelError("Fetch from empty body")
        vm.push(addr[0])
    elif isinstance(addr, int):
        if vm.compiling:
            vm.push(vm._builder.colon_code[addr])
        else:
            raise KernelError("Integer address only valid during compilation")
    else:
        raise KernelError("@ expects list or integer compilation address")
    end-code
    // ( addr -- val ) Fetch value from memory cell or compilation address.
    last :: safe=True

code [']
    tok = vm.input.read()
    if tok is None:
        raise KernelError("['] expects a word name")
    word = vm.tick(tok)
    if word is None:
        raise KernelError(f"['] unknown word: {tok}")
    vm.literal(word)
    end-code immediate
    // ( <name> -- ) Compile word reference as literal.
    last :: safe=True

code [compile]
    tok = vm.input.read()
    if tok is None:
        raise KernelError("[compile] expects a word name")
    word = vm.tick(tok)
    if word is None:
        raise KernelError(f"[compile] unknown word: {tok}")
    vm.comma(word)
    end-code immediate
    // ( <name> -- ) Compile an immediate word into current definition.
    last :: safe=True

: begin     here ; immediate
    // ( -- addr ) Mark the start of an indefinite loop.
    /// Push current compilation address (here) as backward branch destination.
    last :: safe=True

: until     ['] 0branch , , ; immediate
    // ( addr -- ) Conditional loop termination: repeat if flag is false.
    /// Compile 0branch back to addr. Exit loop when flag is true.
    last :: safe=True

: again     ['] branch , , ; immediate
    // ( addr -- ) Unconditional loop repeat: loop forever.
    /// Compile branch back to addr.
    last :: safe=True

: if        ['] 0branch , here 0 , ; immediate
    // ( flag -- ) Conditional forward branch: execute following code if flag is true.
    /// Compile 0branch and reserve a forward patch address on the compilation stack.
    last :: safe=True

: ahead     ['] branch , here 0 , ; immediate
    // ( -- addr ) Unconditional forward branch.
    /// Compile branch and reserve a forward patch address on the compilation stack.
    last :: safe=True

: then      here swap ! ; immediate
    // ( addr -- ) Resolve a forward branch target for if/else/ahead.
    /// Patch target cell at addr to point to current compilation address (here).
    last :: safe=True

: else      [compile] ahead swap [compile] then ; immediate
    // ( addr1 -- addr2 ) Alternate branch clause for if ... else ... then.
    /// Compile ahead branch past false block and resolve preceding if branch.
    last :: safe=True

: ?dup      dup if dup then ;
    // ( x -- x x | x ) Duplicate TOS if it is logically true.
    /// Tests TOS using Python truthiness. If true, leaves two copies of x; if false, leaves x.
    last :: safe=True

: while     [compile] if swap ; immediate
    // ( addr1 -- addr2 addr1 ) Test loop condition in begin ... while ... repeat.
    /// Compile if check; if false, exit past repeat.
    last :: safe=True

: repeat    [compile] again [compile] then ; immediate
    // ( addr2 addr1 -- ) End a begin ... while ... repeat loop.
    /// Compile again back to addr1 and resolve the forward branch from while at addr2.
    last :: safe=True

: aft       drop [compile] ahead [compile] begin swap ; immediate
    // ( addr1 -- addr2 addr1 ) Jump past code on the first loop iteration.
    /// Used in for ... aft ... then ... next loops to skip first iteration logic.
    last :: safe=True

: for       ['] >r , here ; immediate
    // ( count -- ) ( R: -- count ) Begin a for ... next counted loop.
    /// Compile >r to put count on rstack and leave loop start address (here) on stack.
    last :: safe=True

: next      ['] doNext , , ; immediate
    // ( addr -- ) End a for ... next counted loop.
    /// Compile doNext and target address back to the beginning of the for loop.
    last :: safe=True

\ =====================================================================
\ 7. Defining Words: create, does>, constant, variable, value, to
\ =====================================================================

code create
    name = vm.input.read()
    if not name:
        raise KernelError("create expects a name")
    body = []
    def default_action(v, b=body):
        v.push(b)
    word = vm.define(name, default_action, category="created")
    word.body = body
    end-code
    // ( <name> -- ) Create a new word with an initialized data body.
    last :: safe=True

code (does>)
    child = vm.latest
    if child is None or not hasattr(child, "body"):
        raise KernelError("does> needs a created word")
    frame = vm.frame
    if frame is None or not isinstance(frame.colon_code, tuple):
        raise KernelError("does> runtime called outside colon definition")
    steps = frame.colon_code[frame.ip:]
    defining_word = getattr(frame, "word", None)
    if defining_word:
        child.category = defining_word.name
    def child_action(v, w=child, s=steps):
        v.push(w.body)
        yield from v.call(s)
    child.action = child_action
    frame.ip = len(frame.colon_code)
    end-code
    // ( -- ) Runtime helper for does>.

code does>
    vm.comma(vm.words["(does>)"])
    end-code immediate
    // ( -- ) Define runtime behavior for words built by the current defining word.
    last :: safe=True

: constant ( val <name> -- )
    create , does> @ ;
    // ( val <name> -- ) Define a named constant with value val.
    /// Defined via create ... does>. Executing the constant pushes val.
    last :: safe=True

: variable ( <name> -- )
    create 0 , does> ;
    // ( <name> -- ) Define a named variable initialized to 0.
    /// Executing pushes variable's body list. Use @ to fetch and ! to store.
    last :: safe=True

: value ( val <name> -- )
    create , does> @ ;
    // ( val <name> -- ) Define a named reassignable value initialized to val.
    /// Defined via create ... does>. Executing pushes current value. Update via 'to'.
    last :: safe=True

code to
    tok = vm.input.read()
    if tok is None:
        raise KernelError("to expects a value word name")
    word = vm.tick(tok)
    if word is None or not hasattr(word, "body") or not word.body:
        raise KernelError(f"to expects a value word, got {tok}")
    val = vm.pop()
    word.body[0] = val
    end-code
    // ( val <name> -- ) Set value of a word created by value.
    last :: safe=True

\ =====================================================================
\ 8. Compilation Control and Meta-Programming
\ =====================================================================

code [
    vm.host.setdefault('_base2_brackets', []).append(vm._builder)
    vm._builder = None
    end-code immediate
    // ( -- ) Enter interpretation state while compiling.
    last :: safe=True

code ]
    brackets = vm.host.get('_base2_brackets')
    if not brackets:
        raise KernelError("] without matching [")
    vm._builder = brackets.pop()
    end-code immediate
    // ( -- ) Resume compilation after [.
    last :: safe=True

code compiling
    vm.push(vm.compiling)
    end-code
    // ( -- flag ) Report whether compilation is active.
    last :: safe=True

code literal
    val = vm.pop()
    if vm.compiling:
        vm.literal(val)
    elif vm.host.get("_base2_brackets"):
        builder = vm._builder
        vm._builder = vm.host["_base2_brackets"][-1]
        try:
            vm.literal(val)
        finally:
            vm._builder = builder
    else:
        raise KernelError("literal requires an active definition")
    end-code immediate
    // ( x -- ) Compile literal into active definition.
    last :: safe=True

code compile
    tok = vm.input.read()
    if tok is None:
        raise KernelError("compile expects a word name")
    word = vm.tick(tok)
    if word is None:
        raise KernelError(f"compile: unknown word {tok}")
    vm.comma(word)
    end-code immediate
    // ( <name> -- ) Compile the named word into current definition.
    last :: safe=True

code compile-only
    if vm.latest is not None:
        vm.latest.compileonly = True
    end-code
    // ( -- ) Mark latest word as compile-only.
    last :: safe=True

code interpret-only
    if vm.latest is not None:
        vm.latest.interpretonly = True
    end-code
    // ( -- ) Mark latest word as interpret-only.
    last :: safe=True

code nop
    pass
    end-code
    // ( -- ) No operation.
    last :: safe=True

code alias
    target_name = vm.input.read()
    new_name = vm.input.read()
    if not target_name or not new_name:
        raise KernelError("alias expects <target> <new_name>")
    word = vm.tick(target_name)
    if word is None:
        raise KernelError(f"alias: unknown word {target_name}")
    vm.define(new_name, word.action, immediate=word.immediate, category="alias",
              source=word.source, help=word.help, comment=word.comment, properties=word.properties)
    end-code
    // ( <target> <new_name> -- ) Create alias for an existing word.
    last :: safe=True

code perform
    target = vm.pop()
    yield from vm.call(target)
    end-code
    // ( word|callable -- ) Execute word or callable.

: execute perform ;
    // ( word|callable -- ) Execute word or callable.

code stop
    vm.abort()
    end-code
    // ( -- ) Abort the current Forth task.

code ?stop
    if vm.pop():
        vm.abort()
    end-code
    // ( flag -- ) Abort current task when flag is true.

code forget
    name = vm.input.read()
    if name is None:
        raise KernelError("forget expects a name")
    if name not in vm.words:
        raise KernelError(f"forget: unknown word {name}")
    del vm.words[name]
    end-code immediate
    // ( <name> -- ) Remove word from dictionary.

\ =====================================================================
\ 9. Case Structure
\ =====================================================================

: case // ( -- 0 ) Begin a case ... of ... endof ... endcase structure.
    0 ; immediate
    last :: safe=True

: of // ( -- ) Compare selector with case value.
    ['] over , ['] = , [compile] if ['] drop , ; immediate
    last :: safe=True

: endof // ( -- ) Finish a case branch.
    [compile] else ; immediate
    last :: safe=True

: endcase // ( -- ) Resolve case branches and drop selector.
    ['] drop ,
    begin
        ?dup
    while
        [compile] then
    repeat ; immediate
    last :: safe=True

\ =====================================================================
\ 10. Python Interoperability
\ =====================================================================

code <py>
    import re
    curr = vm.input.remaining
    match = re.search(r"</py>|</pyV>", curr)
    if not match:
        raise KernelError("Expected </py> or </pyV>")
    code_str = curr[:match.start()]
    vm.input.consume(match.start())
    vm.push(code_str)
    end-code immediate
    // ( <python> -- string ) Read Python code until </py> or </pyV>.

code </py>
    source = vm.pop()
    import textwrap
    source = textwrap.dedent(source)
    if vm.compiling:
        def op(v):
            exec(source, {"vm": v, **v.host})
        op.source = source
        op.name = f"py: {source.strip()}"
        vm.comma(op)
    else:
        exec(source, {"vm": vm, **vm.host})
    end-code immediate
    // ( string -- ) Execute Python code block without pushing a result.

code </pyV>
    source = vm.pop().strip()
    wrapped = f"vm.push({source})"
    if vm.compiling:
        def op(v):
            exec(wrapped, {"vm": v, **v.host})
        op.source = source
        op.name = f"py> {source}"
        vm.comma(op)
    else:
        exec(wrapped, {"vm": vm, **vm.host})
    end-code immediate
    // ( string -- result ) Evaluate Python expression and push result onto stack.

: py:  BL word [compile] </py>  ; immediate
    // ( <python_token> -- ) Execute next single-token Python code without return value.
    /// Read one whitespace-free word of Python code and execute it in host environment.

: py>  BL word [compile] </pyV> ; immediate
    // ( <python_expr> -- result ) Evaluate next single-token Python expression.
    /// Read one whitespace-free word of Python expression, evaluate it, and push result onto stack.

: py:: CR word [compile] </py>  ; immediate
    // ( <python_line> -- ) Execute Python code up to newline without return value.
    /// Read remainder of line as Python code (spaces allowed) and execute in host environment.

: py>> CR word [compile] </pyV> ; immediate
    // ( <python_expr> -- result ) Evaluate Python expression up to newline.
    /// Read remainder of line as Python expression (spaces allowed) and push result onto stack.

code (::)
    stmt = vm.pop().strip()
    if not stmt:
        raise KernelError("Expected member or expression after ::")

    def _parse_val(raw):
        s = raw.strip()
        low = s.lower()
        if low == "true":
            return True
        if low == "false":
            return False
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s

    if vm.compiling:
        def op(v, s=stmt):
            target = v.pop()
            if "=" in s and not s.startswith("(") and not s.startswith("[") and hasattr(target, "properties"):
                key, val_str = s.split("=", 1)
                key = key.strip()
                val = _parse_val(val_str)
                target.properties[key] = val
                try:
                    setattr(target, key, val)
                except Exception:
                    pass
            else:
                code_str = f"obj{s}" if s.startswith("[") or s.startswith("(") else f"obj.{s}"
                exec(code_str, {"vm": v, "obj": target, **v.host})
        op.source = stmt
        op.name = f":: {stmt}"
        vm.comma(op)
    else:
        target = vm.pop()
        if "=" in stmt and not stmt.startswith("(") and not stmt.startswith("[") and hasattr(target, "properties"):
            key, val_str = stmt.split("=", 1)
            key = key.strip()
            val = _parse_val(val_str)
            target.properties[key] = val
            try:
                setattr(target, key, val)
            except Exception:
                pass
        else:
            code_str = f"obj{stmt}" if stmt.startswith("[") or stmt.startswith("(") else f"obj.{stmt}"
            exec(code_str, {"vm": vm, "obj": target, **vm.host})
    end-code
    // ( str -- ) Access member or call method on TOS without pushing result.

: :: BL word (::) ; immediate
    // ( <member> -- ) Invoke member or statement on TOS without return value.

code (:>)
    stmt = vm.pop().strip()
    if not stmt:
        raise KernelError("Expected member or expression after :>")
    if stmt.startswith("[") or stmt.startswith("("):
        code_str = f"vm.push(vm.pop(){stmt})"
    else:
        code_str = f"vm.push(vm.pop().{stmt})"
    if vm.compiling:
        def op(v):
            exec(code_str, {"vm": v, **v.host})
        op.source = stmt
        op.name = f":> {stmt}"
        vm.comma(op)
    else:
        exec(code_str, {"vm": vm, **vm.host})
    end-code
    // ( str -- result ) Access member or call method on TOS and push result.

: :> BL word (:>) ; immediate
    // ( <member> -- result ) Access member on TOS and push result onto data stack.
    /// Read next token as attribute or method call, evaluate on TOS, and push the result.
