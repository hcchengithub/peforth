code immediate
    vm.latest.immediate = True
    end-code immediate

code \
    curr = vm.input.remaining
    pos = curr.find("\n")
    if pos < 0:
        vm.input.consume(len(curr))
    else:
        vm.input.consume(pos + 1)
    end-code immediate

\ base.f - Core Foundation Vocabulary for Project K
\ Project K 2.1.0

\ --- 1. Early Documentation and Property Words ---

code (
    vm.input.read(until=")")
    end-code immediate

code //
    s = vm.input.read(until="\n") if "\n" in vm.input.remaining else vm.input.rest()
    if vm.latest is not None:
        vm.latest.help = s.strip()
    end-code immediate

code ///
    s = vm.input.read(until="\n") if "\n" in vm.input.remaining else vm.input.rest()
    if vm.latest is not None:
        vm.latest.comment = (getattr(vm.latest, "comment", "") or "") + s.strip() + "\n"
    end-code immediate

code (last)
    name = vm.input.read()
    if name is not None:
        vm.latest = vm.words.get(name)
    end-code

code last
    vm.push(vm.latest)
    end-code

code ::
    token = vm.input.read()
    if "=" not in token:
        raise KernelError(f"Expected key=value, got {token}")
    key, val_str = token.split("=", 1)
    target = vm.pop()
    if val_str.lower() == "true":
        val = True
    elif val_str.lower() == "false":
        val = False
    else:
        try:
            val = int(val_str)
        except ValueError:
            try:
                val = float(val_str)
            except ValueError:
                val = val_str
    if hasattr(target, "properties") and isinstance(target.properties, dict):
        target.properties[key] = val
    elif isinstance(target, dict):
        target[key] = val
    else:
        setattr(target, key, val)
    end-code

\ Retroactively document and configure early words

(last) code
    // ( <name> -- ) Begin a Python host code definition.
    /// Read word name and Python body up to matching end-code keyword.

(last) end-code
    // ( -- ) Terminate a Python host code definition.
    /// Delimiter ending a host code block and compiling it into dictionary.

(last) immediate
    // ( -- ) Mark the latest definition as immediate.
    /// Toggle word.immediate to True so it executes during compilation.

(last) \
    // ( <comment> -- ) Skip line comment to newline.
    /// Ignore all characters up to the next newline.
    last :: safe=True

(last) (
    // ( <comment> ) Skip parenthetical comment.
    /// Ignore all characters up to matching right parenthesis.
    last :: safe=True

(last) //
    // ( <text> -- ) Set one-line help string for the latest word.
    /// Read remainder of the line and assign to word.help.
    last :: safe=True

(last) ///
    // ( <text> -- ) Append detailed comment line for the latest word.
    /// Read remainder of the line and append to word.comment.
    last :: safe=True

(last) (last)
    // ( <name> -- ) Select a word as latest definition.
    /// Set vm.latest to the named word so help or comments can be attached.

(last) last
    // ( -- word ) Push the latest defined word onto the data stack.
    /// Provide reference to the word just defined so properties can be configured.
    last :: safe=True

(last) ::
    // ( word <key=value> -- ) Set property on the target word.
    /// Parse key=value and store in word.properties.
    last :: safe=True

\ --- 2. Colon Definition Words ---

code :
    vm.begin(vm.input.read())
    end-code
    // ( <name> -- ) Begin a colon definition.
    /// Read next token as word name and start compiling a new colon definition.

code ;
    vm.finish()
    end-code immediate
    // ( -- ) Terminate a colon definition.
    /// Finish compiling current colon definition and publish it to dictionary.

\ --- 3. Stack Manipulation ---

code pick
    vm.push(vm.peek(vm.pop()))
    end-code
    // ( ... n -- ... x ) Copy the nth stack item to top.
    /// 0 pick is dup, 1 pick is over. n is 0-indexed from top of stack.
    last :: safe=True

code roll
    vm.push(vm.pop(vm.pop()))
    end-code
    // ( ... n -- ... x ) Move the nth stack item to top.
    /// Remove nth item from depth and push to top. 1 roll is swap, 2 roll is rot.
    last :: safe=True

: dup
    0 pick
    ;
    // ( x -- x x ) Duplicate the top stack item.
    /// Push a copy of the top data stack value.
    last :: safe=True

: over
    1 pick
    ;
    // ( x1 x2 -- x1 x2 x1 ) Copy the second stack item to top.
    /// Push a copy of the item beneath the top of stack.
    last :: safe=True

: swap
    1 roll
    ;
    // ( x1 x2 -- x2 x1 ) Exchange the top two stack items.
    /// Swap the top two elements on the data stack.
    last :: safe=True

: rot
    2 roll
    ;
    // ( x1 x2 x3 -- x2 x3 x1 ) Rotate top three stack items.
    /// Move the third stack item to the top.
    last :: safe=True

code drop
    vm.pop()
    end-code
    // ( x -- ) Discard top stack item.
    /// Remove and discard the top element of the data stack.
    last :: safe=True

code dropall
    vm.dstack.clear()
    end-code
    // ( ... -- ) Clear the entire data stack.
    /// Remove all elements from the data stack leaving it empty.
    last :: safe=True

code depth
    vm.push(len(vm.dstack))
    end-code
    // ( -- n ) Return number of items on the data stack.
    /// Push current data stack depth.
    last :: safe=True

\ --- 4. Arithmetic and Logic ---

code +
    right, left = vm.pop(), vm.pop()
    vm.push(left + right)
    end-code
    // ( n1 n2 -- n3 ) Add n1 and n2.
    /// Pop two numbers and push their sum.
    last :: safe=True

code -
    right, left = vm.pop(), vm.pop()
    vm.push(left - right)
    end-code
    // ( n1 n2 -- n3 ) Subtract n2 from n1.
    /// Pop two numbers and push left minus right.
    last :: safe=True

code *
    right, left = vm.pop(), vm.pop()
    vm.push(left * right)
    end-code
    // ( n1 n2 -- n3 ) Multiply n1 and n2.
    /// Pop two numbers and push their product.
    last :: safe=True

code /
    right, left = vm.pop(), vm.pop()
    vm.push(left / right)
    end-code
    // ( n1 n2 -- n3 ) Divide n1 by n2.
    /// Pop two numbers and push left divided by right.
    last :: safe=True

code mod
    right, left = vm.pop(), vm.pop()
    vm.push(left % right)
    end-code
    // ( n1 n2 -- rem ) Remainder of n1 divided by n2.
    /// Pop two numbers and push left modulo right.
    last :: safe=True

code =
    right, left = vm.pop(), vm.pop()
    vm.push(left == right)
    end-code
    // ( x1 x2 -- flag ) Test for equality.
    /// Return True if top two items are equal, otherwise False.
    last :: safe=True

code <
    right, left = vm.pop(), vm.pop()
    vm.push(left < right)
    end-code
    // ( n1 n2 -- flag ) Test if n1 is less than n2.
    /// Return True if left is strictly less than right.
    last :: safe=True

code >
    right, left = vm.pop(), vm.pop()
    vm.push(left > right)
    end-code
    // ( n1 n2 -- flag ) Test if n1 is greater than n2.
    /// Return True if left is strictly greater than right.
    last :: safe=True

code 0=
    vm.push(vm.pop() == 0)
    end-code
    // ( x -- flag ) Test if top of stack is zero.
    /// Return True if x equals 0.
    last :: safe=True

code 0<
    vm.push(vm.pop() < 0)
    end-code
    // ( n -- flag ) Test if top of stack is negative.
    /// Return True if n is less than 0.
    last :: safe=True

code 1+
    vm.push(vm.pop() + 1)
    end-code
    // ( n -- n+1 ) Increment top of stack by 1.
    /// Add 1 to top stack value.
    last :: safe=True

code 1-
    vm.push(vm.pop() - 1)
    end-code
    // ( n -- n-1 ) Decrement top of stack by 1.
    /// Subtract 1 from top stack value.
    last :: safe=True

code not
    vm.push(not vm.pop())
    end-code
    // ( x -- flag ) Logical NOT.
    /// Invert boolean truth value of top stack item.
    last :: safe=True

code and
    right, left = vm.pop(), vm.pop()
    vm.push(bool(left and right))
    end-code
    // ( x1 x2 -- flag ) Logical AND.
    /// Return True if both items are truthy.
    last :: safe=True

code or
    right, left = vm.pop(), vm.pop()
    vm.push(bool(left or right))
    end-code
    // ( x1 x2 -- flag ) Logical OR.
    /// Return True if either item is truthy.
    last :: safe=True

\ --- 5. Constants & Literals ---

code true
    vm.push(True)
    end-code
    // ( -- True ) Push boolean True.
    /// Constant for boolean True.
    last :: safe=True

code false
    vm.push(False)
    end-code
    // ( -- False ) Push boolean False.
    /// Constant for boolean False.
    last :: safe=True

\ --- 6. Strings and Display ---

code .
    print(vm.pop(), end="", flush=True)
    end-code
    // ( x -- ) Output top stack value without trailing newline.
    /// Print top item to stdout and flush buffer.
    last :: safe=True

code .s
    print(vm.dstack)
    end-code immediate
    // ( -- ) Display data stack non-destructively.
    /// Print the data stack list representation.
    last :: safe=True

code cr
    print()
    end-code
    // ( -- ) Print a newline.
    /// Output a newline to stdout.
    last :: safe=True

code space
    print(" ", end="", flush=True)
    end-code
    // ( -- ) Print a single space.
    /// Output one space character to stdout.
    last :: safe=True

code words
    print(" ".join(vm.words))
    end-code immediate
    // ( -- ) List all words in the dictionary.
    /// Print all word names separated by spaces.
    last :: safe=True

code see
    name = vm.input.read()
    word = vm.tick(name)
    if word is None:
        raise KernelError(f"Unknown word: {name}")
    print(word)
    print(word.source or word.action)
    end-code immediate
    // ( <name> -- ) Display a word's definition and source.
    /// Print word metadata, source code, or colon action tuple.
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
    /// Push text string or compile literal into colon definition.
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
    /// Print text directly or compile code to print it.
    last :: safe=True

\ --- 7. Input Helper ---

code rest
    vm.push(vm.input.rest().strip())
    end-code
    // ( -- text ) Consume and return remainder of current input buffer.
    /// Return trimmed text remaining in the active TIB.
    last :: safe=True

\ --- 8. Task Control & Lifecycle ---

code pause
    yield vm.pause()
    end-code
    // ( -- ) Cooperatively suspend the current task.
    /// Yield pause signal returning control to host.

code resume
    tasks = vm.host.setdefault('paused_tasks', [])
    if not tasks:
        raise KernelError('No paused task')
    task = tasks.pop()
    try:
        task.resume()
    finally:
        if task.status == 'paused':
            tasks.append(task)
        else:
            if task is vm.host.get('pending_ai_task'):
                vm.host['pending_ai_task'] = None
            trusted = vm.host.get('trusted_ai_tasks')
            if trusted and task in trusted:
                trusted.remove(task)
    end-code immediate
    // ( -- ) Resume the most recently paused task.
    /// Pop last paused task and resume its continuation.

code abort
    vm.abort()
    end-code
    // ( -- ) Abort active task.
    /// Discard unfinished colon definition and abort task.

code (bye)
    vm.host['exit_requested'] = True
    end-code
    // ( -- ) Set host exit requested flag.
    /// Request host REPL loop to exit.

: bye
    (bye) abort
    ; immediate
    // ( -- ) Exit Forth REPL back to Python host.
    /// Signal exit and abort current task.

\ --- 9. File Loading ---

code include
    filename = vm.input.read()
    import os
    if not os.path.isabs(filename):
        here = vm.host.get("__file__dir__", ".")
        candidate = os.path.join(here, filename)
        if os.path.exists(candidate):
            filename = candidate
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    yield from vm.evaluate(content)
    end-code
    // ( <filename> -- ) Load and evaluate a Forth file.
    /// Read file content and evaluate it in current task.

\ --- 10. Tick Word ---

code '
    name = vm.input.read()
    word = vm.tick(name)
    if word is None:
        raise KernelError(f"Unknown word: {name}")
    if vm.compiling:
        vm.literal(word)
    else:
        vm.push(word)
    end-code immediate
    // ( <name> -- word ) Look up word and push its reference.
    /// Push word object onto stack or compile as literal.
    last :: safe=True

\ --- 11. Help Word ---

code help
    tokens = vm.input.rest().strip().split()
    if tokens:
        name = tokens[0]
        word = vm.tick(name)
        if word is None:
            print(f"Unknown word: {name}")
            return
        header = f"{word.name} {word.help}" if getattr(word, "help", "") else word.name
        print(header)
        comment = getattr(word, "comment", "") or ""
        for line in comment.splitlines():
            print(f"    {line}")
    else:
        for word in vm.words.values():
            header = f"{word.name} {word.help}" if getattr(word, "help", "") else word.name
            print(header)
            comment = getattr(word, "comment", "") or ""
            for line in comment.splitlines():
                print(f"    {line}")
    end-code immediate
    // ( [<name>] -- ) Print help and comments for a word or all words.
    /// Consume remainder of TIB and display help for the first token, or all words if omitted.
    last :: safe=True

\ --- 12. Load Extensions ---

    include peforth.f
