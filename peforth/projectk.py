"""Project K — a small, extensible Forth kernel in Python.

    from peforth.projectk import VM
    vm = VM(host={"answer": 42})
    vm.dictate('''code answer
        vm.push(answer)
    end-code
    answer''')
    assert vm.pop() == 42

Only code/end-code are installed initially. Python bodies receive `vm` and
the supplied host bindings. end-code terminates a body (inline or multiline).
Words are case-sensitive. Compositions capture definitions, so redefining a
name affects new lookups but not previously compiled compositions.

dictate()/execute() return a Task: inspect its status and resume() after a
pause. tick() finds a Word by name; last() returns the most recently defined Word.
Generator words can `yield vm.pause()` and `yield from vm.evaluate(text)`
or `yield from vm.call(word)` to preserve their own continuation too.
Ordinary Python calls to dictate() start separate tasks sharing this VM's data.
Tasks are cooperative, in-memory continuations; a VM is not thread-safe.

Run this file to see a system grow from its two initial words. Python code
bodies run with normal host privileges. No third-party dependencies.
"""

from dataclasses import dataclass, field
from inspect import isgenerator
import io
import re
import tokenize
from typing import NamedTuple


class ForthError(Exception):
    """An input, definition, or execution failure."""


class _Abort(Exception):
    pass


_PAUSE = object()
_MISSING = object()


@dataclass
class Input:
    """One mutable TIB string and the offset of its next unread character."""

    tib: str = ""
    itib: int = 0

    def __init__(self, tib=None, itib=0, text=None):
        if text is not None and tib is None:
            tib = text
        if tib is None:
            tib = ""
        if not isinstance(tib, str):
            raise ForthError("TIB must be a string")
        self.tib = tib
        self.itib = itib

    @property
    def remaining(self) -> str:
        return self.tib[self.itib:]

    def append(self, text: str) -> None:
        """Append source text at the TIB tail without moving the input cursor."""
        if not isinstance(text, str):
            raise ForthError("Appended TIB text must be a string")
        self.tib += text

    def consume(self, count: int) -> str:
        """Advance over and return count characters from the current TIB offset."""
        if not isinstance(count, int) or count < 0:
            raise ForthError("Input character count must be a nonnegative integer")
        part = self.tib[self.itib:self.itib + count]
        self.itib += len(part)
        return part

    def read(self, until=None):
        remaining = self.remaining
        if until is None:
            match = re.search(r"\S+", remaining)
            if match is None:
                self.itib = len(self.tib)
                return None
            self.itib += match.end()
            return match.group()
        if isinstance(until, str):
            if not until:
                raise ForthError("An input boundary cannot be empty")
            start = remaining.find(until)
            if start < 0:
                raise ForthError(f"Expected input boundary {until!r}")
            end = start + len(until)
        else:
            match = until.search(remaining)
            start, end = match.span() if match else (-1, -1)
            if start == end and start >= 0:
                raise ForthError("An input boundary must consume text")
            if start < 0:
                raise ForthError(f"Expected input boundary {until!r}")
        value = remaining[:start]
        self.itib += end
        return value

    def rest(self):
        remaining = self.remaining
        self.itib = len(self.tib)
        return remaining


@dataclass
class _Word:
    name: str
    action: object
    immediate: bool = False
    source: str = ""
    help: str = ""
    comment: str = ""
    type: str = ""
    _value: object = None
    body: list = None
    properties: dict = field(default_factory=dict, repr=False)

    @property
    def value(self):
        if hasattr(self.action, "value"):
            return self.action.value
        if self.body is not None and len(self.body) > 0:
            return self.body[0]
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        if hasattr(self.action, "value"):
            self.action.value = val
        if self.body is not None and len(self.body) > 0:
            self.body[0] = val

    def to_dict(self, collapse=False):
        word_type = self.type
        if not word_type:
            if isinstance(self.action, tuple):
                word_type = "colon"
            elif self.source:
                word_type = "code"
            else:
                word_type = "host"
        return {
            "name": self.name,
            "type": word_type,
            "immediate": self.immediate,
            "action": self.action,
            "body": self.body,
            "help": "..." if (collapse and self.help) else self.help,
            "comment": "..." if (collapse and self.comment) else self.comment,
            "source": "..." if (collapse and self.source) else self.source,
        }

    def format_dict(self, collapse=True):
        d = self.to_dict(collapse=collapse)
        lines = ["{"]
        for k, v in d.items():
            if k == "action" and isinstance(v, tuple):
                items = [f"<_Word {item.name}>" if isinstance(item, _Word) else repr(item) for item in v]
                val_repr = f"({', '.join(items)})" if len(items) != 1 else f"({items[0]},)"
            else:
                val_repr = repr(v)
            lines.append(f"    {k!r}: {val_repr},")
        if lines[-1].endswith(","):
            lines[-1] = lines[-1][:-1]
        lines.append("}")
        return "\n".join(lines)


@dataclass(frozen=True)
class _Value:
    value: object


class _Definition(NamedTuple):
    owner: object
    word: _Word
    body: list
    previous_last: object


class Task:
    """One execution and its continuation. Failure is raised to the host.

    status is ready/running/paused/done/aborted/failed. Work already performed
    is retained; cancellation does not undo data or completed definitions.
    """

    def __init__(self, vm, steps):
        self.vm, self._steps = vm, steps
        self.inputs = []
        self.rstack = []
        self.tstack = []
        self.status, self.error = "ready", None

    def append_input(self, text):
        """Append source text to this task's active TIB."""
        if self.status in {"done", "aborted", "failed"}:
            raise ForthError(f"Cannot append input to a {self.status} task")
        if not self.inputs:
            raise ForthError("Task has no active input")
        self.inputs[-1].append(text)
        return self

    def resume(self):
        if self.status not in ("ready", "paused"):
            raise ForthError(f"Cannot resume a {self.status} task")
        self.status = "running"
        self.vm._active.append(self)
        try:
            signal = next(self._steps)
            if signal is not _PAUSE:
                raise ForthError("A word may only yield vm.pause()")
            self.status = "paused"
        except StopIteration:
            self.status = "done"
        except _Abort:
            self.status = "aborted"
            self.vm._discard_definition()
        except BaseException as error:
            self.status, self.error = "failed", error
            self.vm._discard_definition()
            self._steps.close()
            raise
        finally:
            self.vm._active.pop()
        return self

    def cancel(self):
        if self.status == "running":
            raise ForthError("Use vm.abort() inside a running task")
        if self.status in ("ready", "paused"):
            # Closing a suspended generator unwinds its input contexts.
            self.vm._active.append(self)
            try:
                self._steps.close()
                self.vm._discard_definition(owner=self)
                self.status = "aborted"
            finally:
                self.vm._active.pop()


class _Frame:
    def __init__(self, action, word=None):
        self.action = action
        self.word = word
        self.ip = 0


class _RStackProxy:
    """Proxy routing return stack operations to the active Task."""

    def __init__(self, vm):
        self._vm = vm

    @property
    def _current(self):
        return self._vm.rstack

    def append(self, item):
        self._current.append(item)

    def pop(self, *args):
        try:
            return self._current.pop(*args)
        except IndexError:
            raise ForthError("Return stack underflow") from None

    def __getitem__(self, idx):
        try:
            return self._current[idx]
        except IndexError:
            raise ForthError("Return stack underflow") from None

    def __setitem__(self, idx, val):
        try:
            self._current[idx] = val
        except IndexError:
            raise ForthError("Return stack underflow") from None

    def __len__(self):
        return len(self._current)

    def __bool__(self):
        return bool(self._current)

    def __repr__(self):
        try:
            return repr(self._current)
        except ForthError:
            return "[]"

    def clear(self):
        self._current.clear()


class VM:
    """Persistent working data and definitions, independent of other VMs."""

    def __init__(self, host=None):
        self.stack = []
        self.words = {}
        self.host = dict(host or {})
        self.host.setdefault("rstack", _RStackProxy(self))
        self._active = []
        self._definition = None
        self._last = None
        self._frames = []
        self.define("code", lambda vm: vm._code())
        self.define("end-code", lambda vm: vm._unexpected_end())

    @property
    def frame(self):
        return self._frames[-1] if self._frames else None

    @property
    def input(self):
        if not self._active or not self._active[-1].inputs:
            raise ForthError("No active input")
        return self._active[-1].inputs[-1]

    @property
    def rstack(self):
        if not self._active:
            raise ForthError("No active task")
        return self._active[-1].rstack

    @property
    def tstack(self):
        if not self._active:
            raise ForthError("No active task")
        return self._active[-1].tstack

    @property
    def compiling(self):
        return self._definition is not None

    def push(self, *values):
        self.stack.extend(values)
        return self

    def pop(self, depth=0):
        if not self.stack:
            raise ForthError("Data stack is empty")
        if depth is None or depth == 0:
            return self.stack.pop()
        if not isinstance(depth, int) or depth < 0 or depth >= len(self.stack):
            raise ForthError("Invalid data stack depth")
        return self.stack.pop(-1 - depth)

    def peek(self, depth=0):
        if not isinstance(depth, int) or depth < 0 or depth >= len(self.stack):
            raise ForthError("Invalid data stack depth")
        return self.stack[-1-depth]

    def define(self, name, action, *, immediate=False, source="", help="", comment="", type="", value=None, body=None):
        if not isinstance(name, str) or not name or any(c.isspace() for c in name):
            raise ForthError("A word needs a nonempty name without whitespace")
        if not callable(action) and not isinstance(action, tuple):
            raise ForthError("A definition needs a host function or composition")
        word = _Word(name, action, immediate, source, help, comment, type, value, body)
        self.words.pop(name, None)
        self.words[name] = word
        self._last = word
        return word

    def tick(self, name):
        """Find a Word by name, or return None when it is absent."""
        return self.words.get(name)

    def last(self):
        """Return the most recently defined Word, or None if none exists."""
        return self._last

    def _require_word(self, name):
        word = self.tick(name)
        if word is None:
            raise ForthError(f"Unknown word: {name}")
        return word

    def begin(self, name):
        if self.compiling:
            raise ForthError("A definition is already being built")
        if not name or any(c.isspace() for c in name):
            raise ForthError("Expected a definition name")
        owner = self._active[-1] if self._active else None
        word = _Word(name, None)
        previous_last = self._last
        self._last = word
        body = []
        self._definition = _Definition(owner, word, body, previous_last)

    def comma(self, operation):
        if not self.compiling:
            raise ForthError("No definition is being built")
        if isinstance(operation, str):
            operation = self._require_word(operation)
        if not isinstance(operation, (_Word, _Value, int)) and not callable(operation):
            raise ForthError("Expected an operation; use literal() for data")
        self._definition.body.append(operation)

    def literal(self, value):
        self.comma(_Value(value))

    def finish(self):
        if not self.compiling:
            raise ForthError("No definition is being built")
        word, body = self._definition.word, self._definition.body
        word.action = tuple(body)
        self.words.pop(word.name, None)
        self.words[word.name] = word
        self._last = word
        self._definition = None
        return word

    def _discard_definition(self, owner=_MISSING):
        if self.compiling and (owner is _MISSING or self._definition.owner is owner):
            self._last = self._definition.previous_last
            self._definition = None

    @staticmethod
    def pause():
        return _PAUSE

    @staticmethod
    def abort():
        raise _Abort()

    def dictate(self, text):
        return Task(self, self.evaluate(text)).resume()

    def execute(self, operation):
        return Task(self, self.call(operation)).resume()

    def call(self, operation):
        """Generator interface for calls that may yield back to the host."""
        if isinstance(operation, int):
            return
        if isinstance(operation, str):
            operation = self._require_word(operation)
        if isinstance(operation, _Value):
            self.push(operation.value)
            return
        action = operation.action if isinstance(operation, _Word) else operation
        if isinstance(action, tuple):
            frame = _Frame(action, word=operation if isinstance(operation, _Word) else None)
            self._frames.append(frame)
            try:
                while frame.ip < len(frame.action):
                    step = frame.action[frame.ip]
                    frame.ip += 1
                    yield from self.call(step)
            finally:
                self._frames.pop()
        elif callable(action):
            try:
                result = action(self)
                if isgenerator(result):
                    yield from result
                elif result is _PAUSE:
                    yield _PAUSE
            except (ForthError, _Abort):
                raise
            except Exception as error:
                name = operation.name if isinstance(operation, _Word) else repr(action)
                raise ForthError(f"{name}: {error}") from error
        else:
            raise ForthError(f"Cannot execute {operation!r}")

    def evaluate(self, text):
        """Interpret a source inside the current task, preserving its context."""
        source = Input(text)
        task = self._active[-1]
        task.inputs.append(source)
        try:
            while (item := source.read()) is not None:
                word = self.words.get(item)
                if word is not None:
                    if self.compiling and not word.immediate:
                        self.comma(word)
                    else:
                        yield from self.call(word)
                else:
                    value = self._number(item)
                    if self.compiling:
                        self.literal(value)
                    else:
                        self.push(value)
        finally:
            task.inputs.pop()

    @staticmethod
    def _number(text):
        # Parse integers first: large integers must never pass through float.
        try:
            return int(text, 10)
        except ValueError:
            try:
                return int(text, 0)
            except ValueError:
                try:
                    return float(text)
                except ValueError:
                    raise ForthError(f"Unknown input: {text}") from None

    def _code(self):
        if self.compiling:
            raise ForthError("Host definitions cannot nest inside a composition")
        name = self.input.read()
        if name is None:
            raise ForthError("Expected a name after code")
        body = self._read_code()
        source = "def operation(vm):\n" + self._function_body(body)
        environment = dict(self.host)
        try:
            exec(compile(source, f"<Project K: {name}>", "exec"), environment)
        except Exception as error:
            raise ForthError(f"Cannot define {name}: {error}") from error
        self.define(name, environment["operation"], source=body)

    @staticmethod
    def _find_code_terminator(text):
        lines = text.splitlines(keepends=True)
        offsets, offset = [], 0
        for line in lines:
            offsets.append(offset)
            offset += len(line)
        try:
            tokens = []
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                tokens.append(token)
                if len(tokens) > 3:
                    tokens.pop(0)
                if len(tokens) == 3:
                    t1, t2, t3 = tokens
                    if (t1.type == tokenize.NAME and t1.string == "end"
                            and t2.type == tokenize.OP and t2.string == "-"
                            and t3.type == tokenize.NAME and t3.string == "code"
                            and t1.end == t2.start and t2.end == t3.start):
                        start_pos = offsets[t1.start[0] - 1] + t1.start[1]
                        end_pos = offsets[t3.end[0] - 1] + t3.end[1]
                        if start_pos > 0 and (text[start_pos - 1].isalnum() or text[start_pos - 1] in ("_", "-")):
                            continue
                        if end_pos < len(text) and (text[end_pos].isalnum() or text[end_pos] in ("_", "-")):
                            continue
                        return start_pos, end_pos
        except (tokenize.TokenError, IndentationError):
            pass
        return None, None

    @staticmethod
    def _function_body(body):
        # Change structural indentation without modifying multiline strings.
        lines = body.splitlines(keepends=True)
        protected = set()
        for token in tokenize.generate_tokens(io.StringIO(body).readline):
            if token.type == tokenize.STRING:
                protected.update(range(token.start[0] + 1, token.end[0] + 1))
        structural = [line for row, line in enumerate(lines, 1)
                      if row not in protected and line.strip()]
        if not structural:
            return "    pass\n"
        width = min(len(line) - len(line.lstrip(" \t")) for line in structural)
        res = "".join(line if row in protected or not line.strip()
                       else "    " + line[width:]
                       for row, line in enumerate(lines, 1))
        if not res.endswith("\n"):
            res += "\n"
        return res

    def _read_code(self):
        # Let Python's lexer distinguish a terminator from text in a string.
        source = self.input
        remaining = source.remaining
        start_pos, end_pos = self._find_code_terminator(remaining)
        if start_pos is not None:
            body = remaining[:start_pos]
            source.consume(end_pos)
            return body
        try:
            for _ in tokenize.generate_tokens(io.StringIO(remaining).readline):
                pass
        except (tokenize.TokenError, IndentationError) as error:
            raise ForthError(f"Cannot read host definition: {error}") from error
        raise ForthError("Expected end-code")

    @staticmethod
    def _unexpected_end():
        raise ForthError("end-code has no matching code definition")


# An example extension layer: none of these words are hardwired into VM.
DEMO = '''
code dup
    vm.push(vm.peek())
end-code
code *
    b, a = vm.pop(), vm.pop()
    vm.push(a * b)
end-code
code .
    print(vm.pop(), end="", flush=True)
end-code
code :
    vm.begin(vm.input.read())
end-code
code immediate
    word = vm.last()
    if word is None:
        raise ForthError("immediate needs a previous definition")
    word.immediate = True
end-code
code ;
    vm.finish()
end-code
immediate
code constant
    name = vm.input.read()
    if name is None:
        raise ForthError("constant expects a name")
    val = vm.pop()
    vm.define(name, lambda v, x=val: v.push(x), type="constant", value=val)
end-code
code s"
    raw = vm.input.read(until='"')
    value = raw[1:] if raw.startswith(" ") else raw
    if vm.compiling:
        vm.literal(value)
    else:
        vm.push(value)
end-code
immediate
code pause
    yield vm.pause()
end-code
: square dup * ;
: greeting s" Hello from Project K!" . ;
: interrupted 3 square . pause 4 square . ;
10 constant ten
greeting ten 2 * . 12 square . interrupted
'''


if __name__ == "__main__":
    machine = VM(host={"ForthError": ForthError})
    print("Initial words:", ", ".join(machine.words))
    work = machine.dictate(DEMO)
    print("Task:", work.status, "— returning control to the host")
    work.resume()
    print("Task:", work.status)
