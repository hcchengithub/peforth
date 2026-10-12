code immediate
    word = vm.last()
    if word is None:
        raise ForthError("immediate needs a previous definition")
    word.immediate = True
end-code

code //
    s = vm.input.read(until=chr(10)) if chr(10) in vm.input.remaining else vm.input.rest()
    word = vm.last()
    if word is not None:
        word.help = s.strip()
end-code
immediate

code ///
    s = vm.input.read(until=chr(10)) if chr(10) in vm.input.remaining else vm.input.rest()
    word = vm.last()
    if word is not None:
        line = s.strip() + chr(10)
        word.comment = (getattr(word, "comment", "") or "") + line
end-code
immediate

code (last)
    name = vm.input.read()
    if name is not None:
        vm._last = vm.words.get(name)
end-code
// ( <name> -- ) Set vm.last() to the specified word name.
/// Allow retroactively setting // help and /// comments for earlier words.

(last) code
// ( <name> -- ) Begin a Python host code definition.
/// Read the next token as the word name.
/// Read Python body text until the matching end-code keyword.
/// Compile the Python code into a host operation: def operation(vm).

(last) end-code
// ( -- ) Terminate a Python host code definition.
/// Delimiter that ends a host code block and installs it into the dictionary.

(last) \
// ( <line> -- ) Skip line comment to newline.
/// Immediate word that ignores all characters up to the next newline.

(last) (
// ( <comment> ) Skip parenthetical comment.
/// Immediate word that ignores all characters up to the matching right parenthesis.

(last) immediate
// ( -- ) Mark the most recently defined word as immediate.
/// Set word.immediate = True so the word executes during compilation rather than compiling.

(last) //
// ( <line> -- ) Set one-line help description for the last defined word.
/// Read the remainder of the line up to newline.
/// Assign the stripped string to vm.last().help.

(last) ///
// ( <line> -- ) Append detailed comment line to the last defined word.
/// Read the remainder of the line up to newline.
/// Append the line to vm.last().comment.
/// Multiple consecutive /// commands accumulate lines into multi-line comments.

code dup
    vm.push(vm.peek())
end-code
// ( x -- x x ) Duplicate the top item on the data stack.
/// Push a duplicate of TOS (top-of-stack) onto the data stack.

code drop
    vm.pop()
end-code
// ( x -- ) Discard the top item from the data stack.
/// Pop and discard the top value from the data stack.

code dropall
    vm.stack.clear()
end-code
// ( ... -- ) Clear all items from the data stack.
/// Remove all elements, leaving the data stack completely empty.

code swap
    b, a = vm.pop(), vm.pop()
    vm.push(b)
    vm.push(a)
end-code
// ( x1 x2 -- x2 x1 ) Exchange the top two items on the data stack.
/// Swap the positions of the top two stack values.

code over
    vm.push(vm.peek(1))
end-code
// ( x1 x2 -- x1 x2 x1 ) Copy the second item to the top of the data stack.
/// Peek the item below TOS (depth 1) and push a copy onto the stack.

code rot
    c, b, a = vm.pop(), vm.pop(), vm.pop()
    vm.push(b)
    vm.push(c)
    vm.push(a)
end-code
// ( x1 x2 x3 -- x2 x3 x1 ) Rotate the third item to the top of the stack.
/// Move the third stack item to the top, shifting the other two items down.

code depth
    vm.push(len(vm.stack))
end-code
// ( -- n ) Push the current depth of the data stack.
/// Return the total number of items currently on the data stack.

code >r
    rstack.append(vm.pop())
end-code
// ( x -- ) ( R: -- x ) Move the top item from data stack to return stack.
/// Pop TOS and push it onto the return stack (rstack).

code r>
    vm.push(rstack.pop())
end-code
// ( -- x ) ( R: x -- ) Move the top item from return stack to data stack.
/// Pop the top item from rstack and push it onto the data stack.

code r@
    vm.push(rstack[-1])
end-code
// ( -- x ) ( R: x -- x ) Copy the top item from return stack to data stack.
/// Peek the top value of rstack without popping it.

code rdrop
    rstack.pop()
end-code
// ( -- ) ( R: x -- ) Discard the top item from the return stack.
/// Pop and discard the top value from rstack.

code >t
    vm.tstack.append(vm.pop())
end-code
// ( x -- ) ( T: -- x ) Move the top data-stack item to this Task's T-stack.
/// Each REPL input runs in its own Task, so T-stack contents do not carry over to the next input.

code t@
    if not vm.tstack:
        raise ForthError("T-stack underflow")
    vm.push(vm.tstack[-1])
end-code
// ( -- x ) ( T: x -- x ) Copy the top item from this Task's T-stack.
/// Each REPL input runs in its own Task, so T-stack contents do not carry over to the next input.

code t>
    if not vm.tstack:
        raise ForthError("T-stack underflow")
    vm.push(vm.tstack.pop())
end-code
// ( -- x ) ( T: x -- ) Move the top item from this Task's T-stack to data stack.
/// Each REPL input runs in its own Task, so T-stack contents do not carry over to the next input.

code *
    b, a = vm.pop(), vm.pop()
    vm.push(a * b)
end-code
// ( n1 n2 -- n3 ) Multiply n1 by n2.
/// Pop two numbers from the data stack and push their product.

code +
    b, a = vm.pop(), vm.pop()
    vm.push(a + b)
end-code
// ( n1 n2 -- n3 ) Add n1 and n2.
/// Pop two numbers from the data stack and push their sum.

code -
    b, a = vm.pop(), vm.pop()
    vm.push(a - b)
end-code
// ( n1 n2 -- n3 ) Subtract n2 from n1.
/// Pop two numbers from the data stack and push the difference (n1 - n2).

code /
    b, a = vm.pop(), vm.pop()
    vm.push(a / b if isinstance(a, float) or isinstance(b, float) else a // b)
end-code
// ( n1 n2 -- n3 ) Divide n1 by n2.
/// Perform floating-point division if either operand is float;
/// otherwise perform integer floor division.

code =
    b, a = vm.pop(), vm.pop()
    vm.push(a == b)
end-code
// ( x1 x2 -- flag ) Check if x1 equals x2.
/// Pop two items and push True if they are equal, False otherwise.

code <>
    b, a = vm.pop(), vm.pop()
    vm.push(a != b)
end-code
// ( x1 x2 -- flag ) Check if x1 is not equal to x2.
/// Pop two items and push True if they are not equal, False otherwise.

code <
    b, a = vm.pop(), vm.pop()
    vm.push(a < b)
end-code
// ( n1 n2 -- flag ) Check if n1 is strictly less than n2.
/// Pop two numbers and push True if n1 < n2, False otherwise.

code >
    b, a = vm.pop(), vm.pop()
    vm.push(a > b)
end-code
// ( n1 n2 -- flag ) Check if n1 is strictly greater than n2.
/// Pop two numbers and push True if n1 > n2, False otherwise.

code <=
    b, a = vm.pop(), vm.pop()
    vm.push(a <= b)
end-code
// ( n1 n2 -- flag ) Check if n1 is less than or equal to n2.
/// Pop two numbers and push True if n1 <= n2, False otherwise.

code >=
    b, a = vm.pop(), vm.pop()
    vm.push(a >= b)
end-code
// ( n1 n2 -- flag ) Check if n1 is greater than or equal to n2.
/// Pop two numbers and push True if n1 >= n2, False otherwise.

code 1+
    vm.push(vm.pop() + 1)
end-code
// ( n -- n+1 ) Increment the top of the stack by 1.
/// Add 1 to the top stack value.

code 1-
    vm.push(vm.pop() - 1)
end-code
// ( n -- n-1 ) Decrement the top of the stack by 1.
/// Subtract 1 from the top stack value.

code nip
    b, a = vm.pop(), vm.pop()
    vm.push(b)
end-code
// ( x1 x2 -- x2 ) Drop the item just below the top of the stack.
/// Equivalent to swap drop. Discard the second item on the stack.

code 0=
    vm.push(not vm.pop())
end-code
// ( x -- flag ) Check if x is zero or false.
/// Return True if TOS is falsy (0, False, None, etc.), False otherwise.

code not
    vm.push(not vm.pop())
end-code
// ( x -- flag ) Logical NOT of the top stack item.
/// Return boolean negation of the top stack value.

code .
    print(vm.pop(), end="", flush=True)
end-code
// ( x -- ) Pop and print the top of the stack without trailing newline.
/// Print TOS to stdout with flush=True and without automatic spacing.

code .s
    print(vm.stack)
end-code
// ( -- ) Print the contents of the data stack.
/// Display the current data stack list representation to stdout.

code cr
    print()
end-code
// ( -- ) Output a newline.
/// Print a carriage return / newline to stdout.

code space
    print(" ", end="", flush=True)
end-code
// ( -- ) Output a single space character.
/// Print a space ' ' to stdout without newline.
code :
    vm.begin(vm.input.read())
end-code
// ( <name> -- ) Begin a colon definition.
/// Read the next token as the name of the new word.
/// Switch the system into compilation mode (vm.compiling = True).

code ;
    vm.finish()
end-code
immediate
// ( -- ) End a colon definition.
/// Finish building the colon definition and return to interpretation mode.
/// Install the completed word into the dictionary.

code ,
    val = vm.pop()
    if vm.compiling:
        vm.comma(val)
    else:
        target = vm.last()
        if target is None or getattr(target, "type", "") != "created" or getattr(target, "body", None) is None:
            raise ForthError("No definition is being built")
        target.body.append(val)
end-code
// ( x -- ) Compile an operation into definition, or append to created word body.
/// In compilation mode, append to current definition. In interpret mode, append to last().body.

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
            vm._definition.body[addr] = val
        else:
            raise ForthError("Integer address only valid during compilation")
    else:
        raise ForthError(f"Cannot store to {type(addr)}")
end-code
// ( val addr -- ) Store val at addr (body list or compilation cell).
/// If addr is list, store into addr[0]. If addr is int, patch definition cell.

code @
    addr = vm.pop()
    if isinstance(addr, list):
        if not addr:
            raise ForthError("Fetch from empty body")
        vm.push(addr[0])
    elif isinstance(addr, int):
        if vm.compiling:
            vm.push(vm._definition.body[addr])
        else:
            raise ForthError("Integer address only valid during compilation")
    else:
        raise ForthError(f"Cannot fetch from {type(addr)}")
end-code
// ( addr -- val ) Fetch value stored at addr (body list or compilation cell).
/// If addr is list, push addr[0]. If addr is int, push definition cell.

code create
    name = vm.input.read()
    if not name:
        raise ForthError("create expects a name")
    body = []
    def default_action(v, b=body):
        v.push(b)
    word = vm.define(name, default_action, type="created", body=body)
end-code
// ( <name> -- ) Create a new word with an initialized data body.
/// Default execution pushes the word's body list onto stack.

code (does>)
    child = vm.last()
    if child is None or not hasattr(child, "body"):
        raise ForthError("does> needs a created word")
    frame = vm.frame
    if frame is None or not isinstance(frame.action, tuple):
        raise ForthError("does> runtime called outside colon definition")
    steps = frame.action[frame.ip:]
    defining_word = getattr(frame, "word", None)
    if defining_word:
        child.type = defining_word.name
    def child_action(v, w=child, s=steps):
        v.push(w.body)
        yield from v.call(s)
    child.action = child_action
    frame.ip = len(frame.action)
end-code
// ( -- ) Runtime step of does>.
/// Rebinds the last created word's action to execute the following steps, and exits.

code does>
    vm.comma(vm.words["(does>)"])
end-code
immediate
// ( -- ) Define runtime behavior for words built by the current defining word.
/// In compilation mode, compiles (does>). At runtime, attaches the following code block to the child word.

code char
    tok = vm.input.read()
    if tok is None:
        raise ForthError("char expects a token")
    if vm.compiling:
        vm.literal(tok)
    else:
        vm.push(tok)
end-code
immediate
// ( <token> -- string ) Read next token as string and push/compile it.
/// Enhanced char that reads any whitespace-delimited token without truncating to 1 character.

: constant ( val <name> -- )
    create ,
does> ( -- val )
    @ ;
// ( val <name> -- ) Define a named constant with value val.
/// Defined via create ... does>. Executing the constant pushes val.

: variable ( <name> -- )
    create 0 , ;
// ( <name> -- ) Define a named variable initialized to 0.
/// Executing pushes variable's body list. Use @ to fetch and ! to store.

: value ( val <name> -- )
    create ,
does> ( -- val )
    @ ;
// ( val <name> -- ) Define a named reassignable value initialized to val.
/// Defined via create ... does>. Executing pushes current value. Update via 'to'.

code to
    name = vm.input.read()
    if name is None:
        raise ForthError("Expected a name after to")
    word = vm.tick(name)
    if word is None:
        raise ForthError(f"Unknown word: {name}")
    if getattr(word, "type", "") == "value":
        if vm.compiling:
            def op(v, target=word):
                target.value = v.pop()
            op.name = f"to {word.name}"
            vm.comma(op)
        else:
            word.value = vm.pop()
    else:
        raise ForthError(f"{name} is not a value")
end-code
immediate
// ( val <name> -- ) Assign val to the specified value word.
/// If interpreting, update value immediately. If compiling, compile runtime assignment.

code branch
    vm.frame.ip = vm.frame.action[vm.frame.ip]
end-code
// ( -- ) Unconditional branch at runtime.
/// Advance the instruction pointer (ip) to the target address stored in the next cell.

code 0branch
    if not vm.pop():
        vm.frame.ip = vm.frame.action[vm.frame.ip]
    else:
        vm.frame.ip += 1
end-code
// ( flag -- ) Conditional branch if flag is false at runtime.
/// Pop flag; if false, jump to the target address stored in the next cell;
/// otherwise, advance ip past the target cell.

code doNext
    count = rstack.pop() - 1
    if count > 0:
        rstack.append(count)
        vm.frame.ip = vm.frame.action[vm.frame.ip]
    else:
        vm.frame.ip += 1
end-code
// ( -- ) ( R: count -- count-1 ) Counted loop runtime step.
/// Decrement rstack counter by 1. If counter > 0, jump to loop start;
/// otherwise pop counter and exit the loop.

code here
    vm.push(len(vm._definition.body))
end-code
// ( -- addr ) Return the current compilation address in the definition body.
/// Push the current length of the definition array being compiled.

code (s)
    delim = vm.pop()
    raw = vm.input.read(until=delim)
    val = raw[1:] if raw.startswith(" ") else raw
    if vm.compiling:
        vm.literal(val)
    else:
        vm.push(val)
end-code
// ( delim -- string ) Internal engine for parsing string delimited by delim.
/// Read input stream until delimiter, handle leading space, and emit literal or push.

: string-quote ( delim <name> -- )
    create , immediate
does> ( -- string )
    @ (s) ;
// ( delim <name> -- ) Define an immediate string quote word for delim.
/// Defined via create ... does>. When executed, parses input until delim.

char " string-quote s"
// ( <string>" -- string ) Parse string delimited by double quote ".
/// Part of the s["'`|^/] string family. Delimiter is '"'.
/// Friends: s" s' s` s| s^ s/
/// Use alternative delimiters to avoid escaping internal quotes.

char ' string-quote s'
// ( <string>' -- string ) Parse string delimited by single quote '.
/// Part of the s["'`|^/] string family. Delimiter is "'".
/// Friends: s" s' s` s| s^ s/
/// Use alternative delimiters to avoid escaping internal quotes.

char ` string-quote s`
// ( <string>` -- string ) Parse string delimited by backtick `.
/// Part of the s["'`|^/] string family. Delimiter is '`'.
/// Friends: s" s' s` s| s^ s/
/// Use alternative delimiters to avoid escaping internal quotes.

char | string-quote s|
// ( <string>| -- string ) Parse string delimited by pipe |.
/// Part of the s["'`|^/] string family. Delimiter is '|'.
/// Friends: s" s' s` s| s^ s/
/// Use alternative delimiters to avoid escaping internal quotes.

char ^ string-quote s^
// ( <string>^ -- string ) Parse string delimited by caret ^.
/// Part of the s["'`|^/] string family. Delimiter is '^'.
/// Friends: s" s' s` s| s^ s/
/// Use alternative delimiters to avoid escaping internal quotes.

char / string-quote s/
// ( <string>/ -- string ) Parse string delimited by slash /.
/// Part of the s["'`|^/] string family. Delimiter is '/'.
/// Friends: s" s' s` s| s^ s/
/// Use alternative delimiters to avoid escaping internal quotes.

code BL
    vm.push(" ")
end-code
// ( -- char ) Push a blank space character ' '.
/// Constant providing the space string ' '.

code int
    vm.push(int(vm.pop()))
end-code
// ( value -- integer ) Convert a value to a Python integer.
/// Uses Python's built-in int() conversion.

code float
    vm.push(float(vm.pop()))
end-code
// ( value -- float ) Convert a value to a Python floating-point number.
/// Uses Python's built-in float() conversion.

code true
    vm.push(True)
end-code
// ( -- flag ) Push Python's True value.

code false
    vm.push(False)
end-code
// ( -- flag ) Push Python's False value.

code none
    vm.push(None)
end-code
// ( -- None ) Push Python's None value.

code ""
    vm.push("")
end-code
// ( -- string ) Push an empty string.

code inf
    vm.push(float("inf"))
end-code
// ( -- number ) Push positive floating-point infinity.

code -inf
    vm.push(float("-inf"))
end-code
// ( -- number ) Push negative floating-point infinity.

code nan
    vm.push(float("nan"))
end-code
// ( -- number ) Push a floating-point NaN value.

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
// ( delim -- string ) Read input text until the specified delimiter.
/// If delim is falsy (None, empty string, False, or 0), consume all remaining TIB.
/// If delim is space, read the next whitespace-delimited word.
/// If delim is newline, read until the end of the line.
/// Otherwise read until the delimiter.

code tib.append
    vm.input.append(" " + vm.pop())
end-code
// ( string -- ) Append source text at the TIB tail with a separating space.

code '
    name = vm.input.read()
    if name is None:
        raise ForthError("Expected a name after '")
    word = vm.tick(name)
    if word is None:
        raise ForthError(f"Unknown word: {name}")
    if vm.compiling:
        vm.literal(word)
    else:
        vm.push(word)
end-code
immediate
// ( <name> -- word ) Find word by name.
/// Read the next token and look up the word in the dictionary.
/// If compiling, compile the word as a literal; if interpreting, push it.

code [']
    name = vm.input.read()
    if name is None:
        raise ForthError("Expected a name after [']")
    word = vm.tick(name)
    if word is None:
        raise ForthError(f"Unknown word: {name}")
    if vm.compiling:
        vm.literal(word)
    else:
        vm.push(word)
end-code
immediate
// ( <name> -- word ) Compile the next word as a literal in a colon definition.
/// Immediate word that looks up the following word and compiles it into the definition.

code [compile]
    name = vm.input.read()
    if name is None:
        raise ForthError("Expected a word name after [compile]")
    word = vm.tick(name)
    if word is None:
        raise ForthError(f"Unknown word: {name}")
    vm.comma(word)
end-code
immediate
// ( <name> -- ) Compile the next immediate word into the definition.
/// Force compiling an immediate word as a normal operation instead of executing it.

code alias
    target = vm.pop()
    if not hasattr(target, "action") or not isinstance(getattr(target, "name", None), str):
        raise ForthError("alias expects a word on the stack.")
    alias_name = vm.input.read()
    if alias_name is None:
        raise ForthError("Expected a name after alias.")
    vm.define(alias_name, (target,), immediate=target.immediate,
              source=f": {alias_name} {target.name} ;",
              help=target.help, comment=target.comment, type="alias")
end-code
immediate
// ( word <alias-name> -- ) Define an alias for an existing word.
/// Usage: ' true alias True. The alias executes the original word.

' true alias True
' false alias False
' none alias None
' inf alias infinity
' -inf alias -infinity

: begin     here ; immediate
// ( -- addr ) Mark the start of an indefinite loop.
/// Push the current compilation address (here) as the backward branch destination.

: until     ['] 0branch , , ; immediate
// ( addr -- ) Conditional loop termination: repeat if flag is false.
/// Compile 0branch back to addr. Exit loop when flag is true.

: again     ['] branch , , ; immediate
// ( addr -- ) Unconditional loop repeat: loop forever.
/// Compile branch back to addr.

: if        ['] 0branch , here 0 , ; immediate
// ( flag -- ) Conditional forward branch: execute following code if flag is true.
/// Compile 0branch and reserve a forward patch address on the compilation stack.

: ahead     ['] branch , here 0 , ; immediate
// ( -- addr ) Unconditional forward branch.
/// Compile branch and reserve a forward patch address on the compilation stack.

: then      here swap ! ; immediate
// ( addr -- ) Resolve a forward branch target for if/else/ahead.
/// Patch the target cell at addr to point to the current compilation address (here).

: else      [compile] ahead swap [compile] then ; immediate
// ( addr1 -- addr2 ) Alternate branch clause for if ... else ... then.
/// Compile an ahead branch past the false block and resolve the preceding if branch.

: ?dup      dup if dup then ;
// ( x -- x x | x ) Duplicate TOS if it is logically true.
/// Tests TOS using Python truthiness. If true, leaves two copies of x;
/// if false, leaves x unchanged.

: while     [compile] if swap ; immediate
// ( addr1 -- addr2 addr1 ) Test loop condition in begin ... while ... repeat.
/// Compile if check; if false, exit past repeat.

: repeat    [compile] again [compile] then ; immediate
// ( addr2 addr1 -- ) End a begin ... while ... repeat loop.
/// Compile again back to addr1 and resolve the forward branch from while at addr2.

: aft       drop [compile] ahead [compile] begin swap ; immediate
// ( addr1 -- addr2 addr1 ) Jump past code on the first loop iteration.
/// Used in for ... aft ... then ... next loops to skip first iteration logic.

: for       ['] >r , here ; immediate
// ( count -- ) ( R: -- count ) Begin a for ... next counted loop.
/// Compile >r to put count on rstack and leave loop start address (here) on stack.

: next      ['] doNext , , ; immediate
// ( addr -- ) End a for ... next counted loop.
/// Compile doNext and target address back to the beginning of the for loop.

code last
    vm.push(vm.last())
end-code
// ( -- word ) Push the most recently defined word object onto the stack.
/// Return vm.last().

code perform
    word = vm.pop()
    yield from vm.call(word)
end-code
// ( word -- ... ) Execute a word object from the data stack.
/// Dispatch the word through the current VM task so stack effects and pauses are preserved.

: execute perform ;
// ( word -- ... ) Execute the word object on the data stack.
/// Commonly used as `last execute` to run the most recently defined word.

code <py>
    import re
    curr = vm.input.remaining
    match = re.search(r"</py>|</pyV>", curr)
    if not match:
        raise ForthError("Expected </py> or </pyV>")
    code_str = curr[:match.start()]
    vm.input.consume(match.start())
    vm.push(code_str)
end-code
immediate
// ( <python> -- string ) Read Python code until </py> or </pyV>.
/// Collect the multi-line Python source block from input and push it onto the stack.

code </py>
    source = vm.pop()
    import textwrap
    source = textwrap.dedent(source)
    if vm.compiling:
        def op(v):
            exec(source, v.host)
        vm.comma(op)
    else:
        exec(source, vm.host)
end-code
immediate
// ( string -- ) Execute Python code block without pushing a result.
/// Execute dedented Python code inside the host environment.
/// In compilation mode, compile as a runtime host execution step.

code </pyV>
    source = vm.pop().strip()
    wrapped = f"push({source})"
    if vm.compiling:
        def op(v):
            exec(wrapped, v.host)
        vm.comma(op)
    else:
        exec(wrapped, vm.host)
end-code
immediate
// ( string -- ) Execute Python expression and push its result onto the data stack.
/// Wrap the Python expression with push(...) and execute in host environment.
/// In compilation mode, compile as a runtime push step.

code CR
    vm.push(chr(10))
end-code
// ( -- char ) Push a newline character (chr(10)).
/// Provide newline string for string/word delimiters.

: py:  BL word [compile] </py>  ; immediate
// ( <python_token> -- ) Execute next single-token Python code without return value.
/// Read one word of Python code and execute it in host environment.

: py>  BL word [compile] </pyV> ; immediate
// ( <python_expr> -- result ) Evaluate next single-token Python expression.
/// Read one word of Python code, evaluate it, and push the result onto data stack.

: py:: CR word [compile] </py>  ; immediate
// ( <python_line> -- ) Execute Python code up to newline without return value.
/// Read remainder of line as Python code and execute in host environment.

: py>> CR word [compile] </pyV> ; immediate
// ( <python_expr> -- result ) Evaluate Python expression up to newline.
/// Read remainder of line as Python expression and push result onto data stack.

code (::)
    stmt = vm.pop().strip()
    if not stmt:
        raise ForthError("Expected member or expression after ::")
    if stmt.startswith("[") or stmt.startswith("("):
        code_str = f"pop(){stmt}"
    else:
        code_str = f"pop().{stmt}"
    if vm.compiling:
        def op(v):
            exec(code_str, v.host)
        vm.comma(op)
    else:
        exec(code_str, vm.host)
end-code
// ( str -- ) Runtime helper for member call or execution on TOS.
/// Execute pop().str or pop()str in host environment.

code (:>)
    stmt = vm.pop().strip()
    if not stmt:
        raise ForthError("Expected member or expression after :>")
    if stmt.startswith("[") or stmt.startswith("("):
        code_str = f"push(pop(){stmt})"
    else:
        code_str = f"push(pop().{stmt})"
    if vm.compiling:
        def op(v):
            exec(code_str, v.host)
        vm.comma(op)
    else:
        exec(code_str, vm.host)
end-code
// ( str -- result ) Runtime helper for member access on TOS with result.
/// Execute push(pop().str) or push(pop()str) in host environment.
: :: BL word (::) ; immediate
// ( <member> -- ) Execute member expression on TOS without return value.
/// Read the next token as attribute/method name and invoke it on the top stack object.

: :> BL word (:>) ; immediate
// ( <member> -- result ) Access member on TOS and push result onto data stack.
/// Read next token as attribute/method name, evaluate on TOS, and push the result.

code see
    name = vm.input.read()
    if not name:
        raise ForthError("Expected a name after see")
    word = vm.tick(name)
    if word is None:
        raise ForthError(f"Unknown word: {name}")

    # Stage 1: Documentation (if help or comment exists)
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

    # Stage 2: Word Object Metadata
    if hasattr(word, "format_dict"):
        print(word.format_dict(collapse=True))
    else:
        imm = " (immediate)" if word.immediate else ""
        print(f"Host word {word.name}: {word.action!r}{imm}")
    print()

    # Stage 3: Definition / Source Code
    if getattr(word, "type", "") == "value":
        print(f"{word.value!r} value {word.name}")
    elif getattr(word, "type", "") == "constant" or isinstance(word.action, Constant):
        print(f"{word.value!r} constant {word.name}")
    elif getattr(word, "type", "") == "variable":
        print(f"variable {word.name}")
    elif getattr(word, "type", "") == "string-quote":
        print(f"char {word.body[0]!r} string-quote {word.name}")
    elif getattr(word, "type", "") == "created" or (hasattr(word, "body") and word.body is not None):
        print(f"created {word.name} (body: {word.body!r})")
    elif isinstance(word.action, tuple):
        parts = []
        for item in word.action:
            if hasattr(item, "name"):
                parts.append("does>" if item.name == "(does>)" else item.name)
            elif hasattr(item, "value"):
                if hasattr(item.value, "name"):
                    parts.append(f"['] {item.value.name}")
                else:
                    parts.append(repr(item.value))
            elif isinstance(item, int):
                parts.append(str(item))
            else:
                parts.append(repr(item))
        imm = " immediate" if word.immediate else ""
        print(f": {word.name} {' '.join(parts)} ;{imm}")
    elif getattr(word, "source", ""):
        lines = [f"code {word.name}", word.source, "end-code"]
        if word.immediate:
            lines.append("immediate")
        print("\n".join(lines))
    else:
        imm = " (immediate)" if word.immediate else ""
        print(f"Host word {word.name}: {word.action!r}{imm}")
end-code
// ( <name> -- ) Decompile and display the documentation, object metadata, and definition of word.
/// Print the documentation header, word object metadata dictionary, and definition source.

code pause
    yield vm.pause()
end-code
// ( -- ) Yield execution back to the host task scheduler.
/// Pause the current Forth task continuation, returning control to host Python.

code *debug*
    breakpoint()
end-code
// ( -- ) Enter Python interactive breakpoint debugger.
/// Call Python's built-in breakpoint() to inspect VM state.

code words
    line = vm.input.read(until=chr(10)) if chr(10) in vm.input.remaining else vm.input.rest()
    patterns = [p.lower() for p in line.strip().split() if p.strip()]
    if not patterns:
        matched = list(vm.words.keys())
    else:
        matched = [name for name in vm.words.keys() if all(p in name.lower() for p in patterns)]
    if matched:
        print(" ".join(matched))
end-code
// ( <patterns> -- ) List words in dictionary filtered by pattern(s).
/// If no patterns given, list all word names.
/// If patterns given, list names containing all patterns (case-insensitive AND).

code help
    line = vm.input.read(until=chr(10)) if chr(10) in vm.input.remaining else vm.input.rest()
    patterns = [p.lower() for p in line.strip().split() if p.strip()]
    matched_words = []
    for name, word in vm.words.items():
        if patterns:
            w_h = getattr(word, "help", "") or ""
            w_c = getattr(word, "comment", "") or ""
            text = (name + " " + w_h + " " + w_c).lower()
            if not all(p in text for p in patterns):
                continue
        matched_words.append(word)
    if patterns:
        def sort_key(w):
            n = w.name.lower()
            if any(n == p for p in patterns):
                return (0, n)
            if any(n.startswith(p) for p in patterns):
                return (1, n)
            if any(p in n for p in patterns):
                return (2, n)
            return (3, n)
        matched_words.sort(key=sort_key)
    entries = []
    nl = chr(10)
    for word in matched_words:
        w_help = getattr(word, "help", "")
        header = f"{word.name} {w_help}" if w_help else word.name
        comment = getattr(word, "comment", "")
        if comment:
            indented = nl.join("    " + c_line for c_line in comment.splitlines())
            entries.append(header + nl + indented)
        else:
            entries.append(header)
    if entries:
        print((nl + nl).join(entries))
end-code
// ( <patterns> -- ) Display help and comments for words.
/// If no patterns given, display help and comments for all words.
/// If patterns given, display words whose name, help, or comments match all patterns (case-insensitive AND).

code bye
    raise SystemExit(0)
end-code
// ( -- ) Exit the Forth process.
/// Terminate execution immediately via SystemExit(0).
