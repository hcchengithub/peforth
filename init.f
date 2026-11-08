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

\ init.f - Minimal bootstrap vocabulary for peforth
\ peforth 2.1.0

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
    if isinstance(target, dict):
        target[key] = val
    else:
        try:
            setattr(target, key, val)
        except Exception:
            pass
        if hasattr(target, "properties") and isinstance(target.properties, dict):
            target.properties[key] = val
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

\ --- 3. Constants & Input Helper Needed by ai.f ---

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

code rest
    vm.push(vm.input.rest().strip())
    end-code
    // ( -- text ) Consume and return remainder of current input buffer.
    /// Return trimmed text remaining in the active TIB.
    last :: safe=True

\ --- 4. Task Control & Lifecycle ---

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

\ --- 5. File Loading ---

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

\ --- 6. Tick Word ---

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

\ --- 7. Help Word ---

code help
    line = vm.input.read(until="\n") if "\n" in vm.input.remaining else vm.input.rest()
    pattern = line.strip()

    if not pattern:
        print("""=== Welcome to peforth ===
peforth is an AI-first Forth environment hosted by Python.

1. Basic Usage:
   - Forth mode (prompt '>'):
     Enter Forth expressions and stack words directly.
     Examples:
       10 20 + .              ( Calculate and print: 30 )
       words                  ( List available Forth words )
       see <word>             ( Decompile and view source of a word )

   - Chat mode (prompt 'chat>'):
     Switch to conversational AI mode by typing 'chat'.
     Chat directly with peforth. Type '/forth' to return to Forth mode.

   - Ask AI anytime:
     From Forth mode, use 'ai: <question>' or 'AI: <question>' (with chime).
     Examples:
       ai: How do I define a new word with a loop?
       ai: What does the word 'over' do?

2. Python Interoperability:
   - Execute inline Python code inside Forth with <py> ... </py>:
       <py> import math; vm.push(math.sqrt(144)) </py> . cr

3. Help & Exploration:
   - help             Display this user guide.
   - help *           List help and comments for all words in the dictionary.
   - help <pattern>   Look up documentation for specific word(s) (e.g. 'help dup').
   - words <pattern>  Filter dictionary words by name.

💡 Have a question? Just ask peforth!
   peforth has full access to its own source code, live dictionary, and system
   architecture. It can explain any word, diagnose code, or guide your workflow.
   Try: ai: <your question>""")
    else:
        if pattern == "*":
            matched_words = list(vm.words.values())
        else:
            target = pattern.casefold()
            exact = [w for name, w in vm.words.items() if name.casefold() == target]
            if exact:
                matched_words = exact
            else:
                patterns = [p.casefold() for p in pattern.split() if p.strip()]
                matched_words = [
                    w for name, w in vm.words.items()
                    if all(
                        p in name.casefold()
                        or p in (getattr(w, "help", "") or "").casefold()
                        or p in (getattr(w, "comment", "") or "").casefold()
                        for p in patterns
                    )
                ]

        if not matched_words:
            print(f"No word matching {pattern!r}.")
        else:
            entries = []
            for word in matched_words:
                w_help = getattr(word, "help", "")
                header = f"{word.name} {w_help}" if w_help else word.name
                comment = getattr(word, "comment", "") or ""
                if comment:
                    indented = "\n".join("    " + c_line for c_line in comment.splitlines())
                    entries.append(header + "\n" + indented)
                else:
                    entries.append(header)
            if entries:
                print("\n\n".join(entries))
    end-code immediate
    // ( [<pattern>] -- ) Display tutorial guide, all words ('*'), or matching word help.
    /// With no arguments, displays a comprehensive introduction to peforth.
    /// 'help *' lists help and comments for all words in the dictionary.
    /// 'help <pattern>' searches word names, help, and comments.
    last :: safe=True

\ --- 8. Load Master peforth ---

    include peforth.f
