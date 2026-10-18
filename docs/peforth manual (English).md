# peforth v2 — Forth Kernel Technical Manual and Architectural Philosophy

> English edition · Based on the Traditional Chinese [peforth manual（漂亮字）](peforth%20manual.md), revision dated 2026-10-08.
>
> Runtime: Python 3.10+ on Linux, WSL, and Windows. Principal sources: `peforth/projectk.py`, `peforth/repl.py`, and `peforth/f/base.f`.

This is an **architecture and design manual**, not an exhaustive Forth word reference. The dictionary provides per-word help and comments. For installation, virtual environments, the `f` command, and current compatibility limitations, start with the repository [README](../README.md). For the optional AI assistant, also see [AI support](ai.md).

**Use AI as a reading companion.** We have made every effort to explain the design and technical details clearly, but some passages may still leave questions unanswered. If anything is unclear, consider using an AI sidebar in your browser (for example, Gemini in Chrome) to ask questions about the page you are reading, request additional examples, or explore the code and concepts in greater depth. AI explanations can be mistaken, so verify important technical details against the source code and actual behavior.

## Preface — Minimalism, Revisited

Forth's enduring appeal lies in its small stack machine, postfix notation, open compiler, and the ability to extend the language from within itself. Re-creating a vintage flat-memory computer inside a modern operating system, however, can isolate Forth from the very facilities that make contemporary software useful.

**peforth (Python Edition)** takes another path: retain Forth's programmable language machinery while letting Python supply objects, libraries, I/O, and system integration. Rather than making Python look like Forth or turning Forth into a conventional Python wrapper, the two languages cooperate. Forth orchestrates; Python provides rich capabilities.

Project K is the intentionally small shared kernel at the heart of peforth v2. The remainder of the language is built as layers of Forth vocabulary and host integration.

---

## 1. Design Philosophy and Architecture

### 1.1 From isolated memory to a symbiotic microkernel

Traditional Forth implementations often assume a linear address space and cells that hold numbers or addresses. This is elegant on a bare-metal target, but less attractive when working with Python dictionaries, arrays, generators, class instances, and scientific libraries.

In peforth, the data stack holds **Python object references**. A Forth word can consume an integer, string, list, or application object without pretending it is a byte-addressed cell. The kernel provides execution and extension mechanisms; the host provides the wider ecosystem.

This design deliberately trades strict traditional memory-model compatibility for expressive host interoperability. peforth v2 is **not** a drop-in replacement for peforth v1 or a claim of full ANS Forth compatibility.

### 1.2 The three stacks

- **Data stack** (`vm.stack`): a Python list of operands and object references, shared by executions within one VM.
- **Return stack** (`Task.rstack`): private to each Task; holds return-stack values and loop-related state. `vm.rstack` routes operations to the currently active Task.
- **T-stack** (`Task.tstack`): private to each Task; used for auxiliary task-local values, including input-related offsets.

Typical notation places the top of the stack at the **right**:

```forth
( a b -- c )             \ data stack
( x -- ) ( R: -- x )     \ move to return stack
( x -- ) ( T: -- x )     \ move to T-stack
```

A data-stack underflow raises `ForthError`, rather than reading arbitrary memory. The Forth words `>r`, `r>`, `r@`, and `rdrop` manipulate the return stack; `>t`, `t@`, and `t>` operate on the T-stack.

### 1.3 Interpreter and compiler

The outer interpreter reads tokens from the current input stream. When a token names a dictionary word, it is executed in interpretation mode or compiled in compilation mode, unless marked `immediate`. A token not found in the dictionary is interpreted as a numeric literal or rejected.

In compilation mode, normal words become operations in the new definition; numeric literals become literal operations. Immediate words execute **while compiling**, which makes Forth's control structures and language extensions possible.

```forth
: square dup * ;
5 square . cr
```

The colon word starts a definition; the semicolon finishes it. The important distinction is not an elaborate syntax tree but the ability to manipulate compilation using words defined in the language itself.

### 1.4 Source boundaries

| File | Responsibility |
| --- | --- |
| `peforth/projectk.py` | Input parser, Word objects, VM, Task, continuation, host-code words |
| `peforth/f/base.f` | Base dictionary, control structures, defining words, Python bridge |
| `peforth/f/auxiliary.f` | Nonessential utility vocabulary |
| `peforth/f/ai.f` | Forth-facing AI commands |
| `peforth/ai_bridge.py`, `peforth/ai_tools.py` | AI sessions, transport, host tools |
| `peforth/repl.py` | Runtime assembly, resources, interactive terminal |

The bare Project K kernel intentionally does **not** preload the complete peforth vocabulary.

---

## 2. Input Streams, Lexing, and Delimiters

### 2.1 Terminal input as a persistent stream

The kernel's `Input` object stores a text buffer (`tib`) and a character offset (`itib`). Reading a token advances the offset, while preserving the underlying buffer. The relevant operations include:

| Operation | Meaning |
| --- | --- |
| `append(text)` | Extend the current buffer without resetting its offset |
| `consume(count)` | Consume a specified number of characters |
| `read()` | Read the next token |
| `read(until=delimiter)` | Read through a delimiter |
| `rest()` | Return the unconsumed suffix and advance to the end |

An active paused Task can receive more input through `task.append_input(text)` and then continue with `task.resume()`. A completed Task cannot be revived by appending text.

Comments and documentation words are immediate: `\` skips the rest of a line, `( ... )` consumes a delimited comment, and `//` and `///` attach documentation to the most recently defined word.

### 2.2 Correctly delimiting embedded Python

A naïve search for `end-code` can mistake a marker **inside a Python string or comment** for the end of a host definition:

```forth
code example
    message = "the words end-code are only text"
    # end-code here is also only a comment
    vm.push(message)
end-code
```

Project K uses Python's `tokenize.generate_tokens` in its terminator finder. Python's lexer distinguishes strings and comments from actual tokens, allowing the kernel to recognize a real `end-code` marker instead of splitting at a misleading occurrence.

This is a general architectural lesson: **let the host language parse its own syntax** rather than constructing a second, fragile parser.

### 2.3 Extensible string delimiters

The base vocabulary provides string forms such as `s"`, `s'`, `s|`, and other delimiter variants. Choosing a suitable delimiter can reduce escaping when working with quotes, regular expressions, JSON, or snippets of another language.

These forms are not merely parser special cases. Forth's defining-word facilities can construct families of words with their own parsing behavior. Inspect the current `base.f` and a word's `see` output for exact delimiter semantics.

---

## 3. Memory, Streams, and the PAD Concept

### 3.1 Python objects instead of simulated flat RAM

The VM's data stack carries native Python values. Memory-like Forth abstractions can therefore be implemented using Python collections and references, without imposing a universal 64-KB address space.

The traditional words `here`, `,`, `@`, and `!` should be understood in the context of the v2 vocabulary and its compilation/data abstractions, **not** assumed to expose raw host pointers. Inspect their definitions when porting code that depends on byte-level memory layout.

### 3.2 Compile-time addresses and patching

Branch targets can be represented as positions in a definition's operation sequence. A control word records a position, compiles a placeholder, and later patches the destination when the corresponding closing word is encountered.

This gives `if ... else ... then` and loop words their familiar structure without requiring a native machine-code compiler.

### 3.3 Input buffers and task-local scratch state

The terminal input buffer is a stream with a cursor, not a global mutable string shared indiscriminately by every task. Input contexts are associated with active execution, and the T-stack is Task-private. This distinction matters when a word pauses halfway through parsing: its continuation must resume with the correct input and scratch state.

---

## 4. Control Structures

### 4.1 Forth control words are compiler extensions

`if`, `else`, `then`, `begin`, `again`, `until`, and `while ... repeat` express structured flow while preserving Forth's extensible compiler. The words participate in compilation by emitting or patching branch operations.

```forth
: absolute dup 0 < if negate then ;
: countdown begin dup . 1 - dup 0 = until drop ;
```

These examples illustrate the intended postfix style; verify individual vocabulary words with `words` and `see` in the running version.

### 4.2 Forward branches

An `if` does not initially know where its false branch will land. It records a forward reference. `else` optionally introduces another forward branch, and `then` resolves the outstanding destination. The same mechanism generalizes to custom structured words.

### 4.3 Indefinite loops

`begin ... again` describes an unconditional backward branch. `begin ... until` tests a flag, and `begin ... while ... repeat` separates the test from the loop body. These are ordinary compiler-level constructions, not Python loops secretly substituted for Forth syntax.

### 4.4 Counted loops and `aft`

The `for ... next` family uses task-private return-stack state for its loop counter. The `aft` form supports a first-iteration-versus-subsequent-iterations arrangement, a compact idiom inherited from classic eForth-style control flow.

A paused Task retains its return stack. Another Task can run without stealing the suspended loop counter.

---

## 5. Dictionary, Compiler, and Defining Words

### 5.1 Word objects and introspection

Each dictionary entry is a `_Word` object, with a name, executable action, an immediate flag, and descriptive metadata such as source, help, comment, type, value, and body.

The VM exposes useful Python-side operations:

```python
word = vm.tick("square")   # Lookup; None if missing
latest = vm.last()         # Most recently defined word
```

`vm.define(...)` installs a word; `vm.begin(name)`, `vm.comma(operation)`, `vm.literal(value)`, and `vm.finish()` implement the compilation lifecycle.

### 5.2 Colon definitions

A colon definition composes existing operations. The compiler keeps an in-progress definition until it is finished, then publishes it in the dictionary. A failed or aborted definition is discarded instead of being left half-installed.

```forth
: fourth-power dup * dup * ;
3 fourth-power . cr
```

### 5.3 Defining words as factories

Words such as `constant`, `variable`, `create`, and `does>` illustrate a powerful Forth pattern: a word can create **new words** with data and runtime behavior. A defining word is effectively a small factory for domain-specific vocabulary.

`does>` is particularly important because it separates the construction of a new word from what that word does when later executed. This is metaprogramming expressed in Forth rather than an external code-generation framework.

### 5.4 Word type and factory identity

A word's `type` metadata can describe how it was produced. Combined with its action, body, and source, this enables more informative introspection than a dictionary containing only names and opaque function pointers.

---

## 6. Python Interoperability

### 6.1 One process, two complementary languages

peforth runs Forth and Python in the same host process. Python objects can travel on the data stack, and host functions can operate directly on them. No separate foreign-function runtime is necessary.

**Security consequence:** embedded Python runs with the permissions of the local process. Never treat untrusted Forth or Python snippets as sandboxed.

### 6.2 Defining a host-backed word

```forth
code double
    vm.push(vm.pop() * 2)
end-code

21 double . cr
```

The kernel builds a Python callable for the word, passing the active `vm`. Within the body, `vm.pop()`, `vm.push()`, `vm.peek()`, and other VM operations are available.

The base vocabulary also offers inline Python forms such as `<py> ... </py>` and `<py> ... </pyV>`, plus shorter forms. These belong to the peforth layer, not the bare Project K kernel; consult `base.f` for exact stack effects and scope.

### 6.3 Python modules and existing libraries

The main architectural advantage is reuse. Computationally heavy routines, system APIs, or a library such as an FFT implementation can remain in Python while Forth supplies the high-level orchestration. A `code ... end-code` word may import a module and expose a concise Forth interface.

```forth
code magnitude
    import math
    vm.push(math.fabs(vm.pop()))
end-code
-3 magnitude . cr
```

Host integration also includes `::` and `:>` forms for Python object access or invocation. Their difference is whether the operation returns a value to the Forth stack. Verify the exact syntax in the current base vocabulary before embedding these forms in scripts.

---

## 7. Tasks, Pause, and Continuations

### 7.1 Why another concurrency model?

Many asynchronous designs ask the programmer to coordinate callbacks, timeouts, cancellation tokens, locks, and the ownership of intermediate state. These mechanisms can be necessary in some systems, but they need not be hardwired into the **core execution model** of a small language.

peforth separates **mechanism** from **policy**. The mechanism is a resumable computation. Scheduling, external events, deadlines, and user interaction can remain outside the kernel.

### 7.2 `pause` is deliberately minimal

The kernel's `vm.pause()` produces a pause signal. A Python generator-based word can yield that signal:

```forth
code wait-here
    yield vm.pause()
end-code

: two-stages 1 . wait-here 2 . ;
```

When execution reaches `wait-here`, the Task pauses; after `resume()`, it continues after the yield. This preserves the computation's position instead of restarting the word.

The bare VM supports this mechanism directly. The complete peforth REPL adds its own policy for dealing with interactive tasks and user input.

### 7.3 A Task is one execution and its continuation

On the Python side:

```python
from peforth.projectk import VM

vm = VM()
# Bare VM starts with only the minimal kernel words.
task = vm.dictate("code wait\n    yield vm.pause()\nend-code\nwait")
print(task.status)   # paused
task.resume()
print(task.status)   # done
```

`dictate(text)` starts an execution and returns its Task after its first run. `execute(operation)` similarly starts an execution of a word or operation. A Task holds the suspended generator, its input contexts, and its private stacks.

The statuses are `ready`, `running`, `paused`, `done`, `aborted`, and `failed`. A failed Task records an error and propagates the failure to its host caller.

### 7.4 Shared and private resources

| Resource | Scope |
| --- | --- |
| Data stack (`vm.stack`) | Shared inside a VM |
| Dictionary (`vm.words`) | Shared inside a VM |
| Host environment (`vm.host`) | Shared inside a VM |
| Return stack (`Task.rstack`) | Task-private |
| T-stack (`Task.tstack`) | Task-private |
| Active input contexts | Task-local execution context |
| Continuation and status | Task-private |

The design is **cooperative**, not automatically parallel or thread-safe. Tasks yield explicitly, so normal execution between yields is not preempted by this VM scheduler. Host-side threads or shared mutable Python objects still require appropriate synchronization if used concurrently.

### 7.5 Why the return stack must be private

Imagine Task A entering a counted loop and pausing. Task B then enters another loop. If both use one global return stack, Task B can overwrite the state Task A expects upon resumption.

Task-private return stacks remove that particular interference. `vm.rstack` provides a convenient active-Task proxy while keeping the underlying storage separate.

### 7.6 REPL input versus a Task's input

Typing a new line in the REPL is not the same operation as appending text to a paused Task's existing input stream. The distinction is intentional: a host or scheduler must decide **which continuation** should receive incoming text.

For an active paused Task, `task.append_input(text)` extends its input and `task.resume()` continues it. A completed or aborted Task cannot be resumed or given new input.

### 7.7 Two useful mental models

**The unaware guard (polling):** A scheduler repeatedly checks whether a Task can continue. This works, but the guard may waste effort and needs a policy for deciding when to check again.

**The restaurant buzzer (event-driven continuation):** A Task pauses and keeps its place. An external event — user input, a response, or a completed operation — signals that it is time to resume. The Task itself need not know how the event was detected.

Neither model is mandated by `pause`. That freedom is the point: the kernel preserves a continuation; the surrounding application chooses how and when to resume it.

### 7.8 Cancellation and failure are not rollback

`task.cancel()` can abort a ready or paused Task. It does not undo completed stack changes, side effects, I/O, or previously committed definitions. Calling `vm.abort()` inside an active Task is a different path to aborting execution.

A Task that has finished cannot be resumed. This simple lifecycle prevents accidental resurrection of a completed computation.

---

## 8. Introspection, Debugging, and Tooling

### 8.1 Stack inspection

The interactive environment provides familiar Forth stack operations and display words. On the Python side, `vm.stack`, `vm.peek()`, and `vm.pop()` make the live stack observable. Stack-effect comments remain an essential discipline because Python object references are dynamically typed.

### 8.2 Dictionary discovery and self-documentation

Use `words` to discover vocabulary and `see` to inspect a definition. Documentation attached through `//` and `///` is stored with the word, allowing source-level descriptions to travel with executable vocabulary.

### 8.3 Three-stage `see`

The v2 `see` design combines:

1. **Documentation:** help and explanatory comments.
2. **Metadata:** the Word object's properties and identity.
3. **Implementation:** source or reconstructed composition appropriate to the word's type and action.

This matters for AI-assisted development as much as for human debugging. A tool can inspect a word before proposing a change, rather than guessing how the word behaves from its name.

### 8.4 Debugging strategy

Inspect the stack, the current dictionary entry, its metadata, and the relevant source file. For suspended execution, inspect the Task status and the active input/continuation context. The legacy v1 debugger is not part of the supported v2 interface; avoid relying on obsolete v1 APIs.

---

## 9. Engineering, Deployment, and Verification

### 9.1 Layered architecture

Keep the kernel small and generic. Implement reusable language constructs in `base.f`; nonessential conveniences in `auxiliary.f`; REPL policy in `repl.py`; and AI behavior in the optional AI layer. This separation makes it possible to embed the bare kernel without taking on an interactive terminal or a network dependency.

### 9.2 Cross-platform development

Use Python 3.10 or newer. The repository README documents separate editable installations for Windows and Linux/WSL. A WSL checkout is best kept in the Linux filesystem, and each platform should use its own virtual environment.

Avoid assuming that shell paths, executable locations, or newline conventions are identical across platforms.

### 9.3 Tests

From an editable checkout, run the project's unit tests with the virtual environment's Python:

```bash
.venv/bin/python -m unittest discover -s tests
```

On Windows, substitute `.venv\Scripts\python.exe`. Tests and source code are the final authority for precise behavior when documentation and implementation diverge.

### 9.4 Optional AI assistance

The `f` REPL can integrate an AI assistant, but ordinary Forth operation does not require an API key. AI may help explain vocabulary, design new words, and propose code. Execution of proposed Forth actions is permissioned and occurs in the **live local VM** when approved.

This matches the practical peforth v2 workflow:

> **You describe what you want. AI writes the Forth. Powered by Python and Project K.**

The human still controls whether proposed actions should run, especially when they can access local files or host APIs. See [AI support](ai.md) for configuration, sessions, and approval behavior.

---

## Conclusion — A Small Kernel, an Open World

peforth v2 is an experiment in preserving Forth's deepest ideas without preserving every constraint of its historical hardware. Python provides objects and libraries; Forth provides a malleable vocabulary and compiler; Project K supplies the small execution engine and resumable Tasks.

The result is not merely a Forth interpreter implemented in Python. It is a programmable bridge between a minimal stack language, a modern host runtime, and — optionally — an AI collaborator.

### Further reading

- [Repository README: installation and quick start](../README.md)
- [Traditional Chinese manual（漂亮字）](peforth%20manual.md)
- [AI assistant guide](ai.md)
- [Project K source](../peforth/projectk.py)
- [Base Forth vocabulary](../peforth/f/base.f)
- [Tests](../tests/)
