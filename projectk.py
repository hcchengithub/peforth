"""Project K, implemented from its conceptual specification.

Only code/end-code belong to a new VM.
Host bodies use Python and receive `vm` plus copied host bindings.
Numbers use Python's int(text, 10), int(text, 0), then float(text): arbitrary
precision integers, 0x/0o/0b prefixes, and platform binary floating point.
Tasks are cooperative and not thread-safe. Frames are task-private, but the
data stack, vocabulary and single unfinished definition remain shared.
"""

from dataclasses import dataclass, field
import inspect
import io
import re
import tokenize


class KernelError(Exception):
    pass


class _Abort(BaseException):
    pass


_PAUSE = object()
_ALL = object()


class Input:
    def __init__(self, tib="", itib=0):
        if not isinstance(tib, str):
            raise KernelError("TIB must be text")
        self.tib = tib
        self.itib = itib

    @property
    def itib(self):
        return self._itib

    @itib.setter
    def itib(self, value):
        if type(value) is not int or not 0 <= value <= len(self.tib):
            raise KernelError("itib is outside TIB")
        self._itib = value

    @property
    def remaining(self):
        return self.tib[self.itib:]

    def append(self, text):
        if not isinstance(text, str):
            raise KernelError("Appended input must be text")
        self.tib += text

    def consume(self, count):
        if type(count) is not int or count < 0:
            raise KernelError("Character count must be a nonnegative integer")
        result = self.remaining[:count]
        self.itib += len(result)
        return result

    def rest(self):
        return self.consume(len(self.remaining))

    def read(self, until=None):
        text = self.remaining
        if until is None:
            match = re.search(r"\S+", text)
            if match is None:
                self.itib = len(self.tib)
                return None
            self.itib += match.end()
            return match.group()
        if isinstance(until, str):
            if not until:
                raise KernelError("Boundary cannot be empty")
            start = text.find(until)
            if start < 0:
                raise KernelError(f"Missing boundary: {until!r}")
            end = start + len(until)
        else:
            match = until.search(text)
            if match is None:
                raise KernelError(f"Missing boundary: {until!r}")
            start, end = match.span()
            if start == end:
                raise KernelError("Boundary must consume characters")
        result = text[:start]
        self.itib += end
        return result


@dataclass(eq=False)
class Word:
    name: str
    action: object = None
    immediate: bool = False
    category: str = "host"
    source: str = ""
    help: str = ""
    comment: str = ""
    properties: dict = field(default_factory=dict)

    def __repr__(self):
        return f"<Word {self.name!r} ({self.category})>"


@dataclass(frozen=True)
class Literal:
    value: object


@dataclass
class Frame:
    word: object
    colon_code: tuple
    ip: int = 0


@dataclass
class _Builder:
    word: Word
    owner: object
    previous: object
    colon_code: list = field(default_factory=list)


class Task:
    def __init__(self, vm, continuation):
        self.vm = vm
        self.continuation = continuation
        self.inputs = []
        self.frames = []
        self.rstack = []
        self.tstack = []
        self.status = "ready"
        self.error = None

    def append_input(self, text):
        if self.status in ("done", "aborted", "failed") or not self.inputs:
            raise KernelError("Task has no live input to append to")
        self.inputs[-1].append(text)
        return self

    def resume(self):
        if self.status not in ("ready", "paused"):
            raise KernelError(f"Cannot resume a {self.status} task")
        self.status = "running"
        self.vm._active.append(self)
        try:
            try:
                signal = next(self.continuation)
                if signal is not _PAUSE:
                    raise KernelError("Only the pause signal may be yielded")
                self.status = "paused"
            except StopIteration:
                self.status = "done"
            except _Abort:
                self.status = "aborted"
                self.vm._discard()
            except BaseException as error:
                self.status = "failed"
                self.error = error
                self.vm._discard()
                raise
            finally:
                if self.status in ("done", "aborted", "failed"):
                    self.continuation.close()
        finally:
            self.vm._active.pop()
        return self

    def cancel(self):
        if self.status == "running":
            raise KernelError("A running task must abort from inside execution")
        if self.status in ("ready", "paused"):
            self.vm._active.append(self)
            try:
                self.status = "aborted"
                try:
                    self.continuation.close()
                finally:
                    self.vm._discard(self)
            finally:
                self.vm._active.pop()
        return self


class VM:
    def __init__(self, host=None):
        self.dstack = []
        self.words = {}
        self.host = dict(host or {})
        self._active = []
        self._builder = None
        self.latest = None
        self.define("code", lambda m: m._host_definition())
        self.define("end-code", lambda m: m._unmatched_end())

    @property
    def task(self):
        if not self._active:
            raise KernelError("No active task")
        return self._active[-1]

    @property
    def input(self):
        if not self.task.inputs:
            raise KernelError("No active input")
        return self.task.inputs[-1]

    @property
    def rstack(self):
        return self.task.rstack

    @property
    def tstack(self):
        return self.task.tstack

    @property
    def frame(self):
        return self.task.frames[-1] if self.task.frames else None

    @property
    def compiling(self):
        return self._builder is not None

    def push(self, *values):
        self.dstack.extend(values)
        return self

    def _depth(self, depth):
        if type(depth) is not int or not 0 <= depth < len(self.dstack):
            raise KernelError("Invalid data stack depth (or empty stack)")
        return -1 - depth

    def peek(self, depth=0):
        return self.dstack[self._depth(depth)]

    def pop(self, depth=0):
        return self.dstack.pop(self._depth(depth))

    @staticmethod
    def _name(name):
        if not isinstance(name, str) or not name or any(c.isspace() for c in name):
            raise KernelError("A name must be nonempty and contain no whitespace")

    def tick(self, name):
        return self.words.get(name)

    def _resolve(self, operation):
        if isinstance(operation, str):
            word = self.tick(operation)
            if word is None:
                raise KernelError(f"Unknown word: {operation}")
            return word
        return operation

    def _publish(self, word):
        self.words.pop(word.name, None)
        self.words[word.name] = word
        self.latest = word
        return word

    def define(self, name, action, *, immediate=False, category="host",
               source="", help="", comment="", properties=None):
        self._name(name)
        if not callable(action) and not isinstance(action, tuple):
            raise KernelError("Behavior must be a callable or colon body tuple")
        return self._publish(Word(name, action, immediate, category, source,
                                  help, comment, dict(properties or {})))

    def begin(self, name):
        if self.compiling:
            raise KernelError("A colon definition is already being built")
        self._name(name)
        word = Word(name, category="colon")
        owner = self._active[-1] if self._active else None
        self._builder = _Builder(word, owner, self.latest)
        self.latest = word
        return word

    def comma(self, operation):
        if not self.compiling:
            raise KernelError("No unfinished colon definition")
        operation = self._resolve(operation)
        if not isinstance(operation, (Word, Literal)) and not callable(operation):
            raise KernelError("Compile an operation; use literal() for data")
        self._builder.colon_code.append(operation)

    def literal(self, value):
        self.comma(Literal(value))

    def finish(self):
        if not self.compiling:
            raise KernelError("No unfinished colon definition")
        builder = self._builder
        builder.word.action = tuple(builder.colon_code)
        self._builder = None
        return self._publish(builder.word)

    def _discard(self, owner=_ALL):
        if self.compiling and (owner is _ALL or self._builder.owner is owner):
            self.latest = self._builder.previous
            self._builder = None

    @staticmethod
    def pause():
        return _PAUSE

    def abort(self):
        self.task
        raise _Abort()

    def dictate(self, tib):
        return Task(self, self.evaluate(tib)).resume()

    def execute(self, operation):
        return Task(self, self.call(operation)).resume()

    def call(self, operation):
        self.task  # Calls inside a continuation require active task context.
        operation = self._resolve(operation)
        if isinstance(operation, Literal):
            self.push(operation.value)
            return
        action = operation.action if isinstance(operation, Word) else operation
        if isinstance(action, tuple):
            frame = Frame(operation, action)
            frames = self.task.frames
            frames.append(frame)
            try:
                while frame.ip < len(frame.colon_code):
                    if frame.ip < 0:
                        raise KernelError("Negative execution position")
                    step = frame.colon_code[frame.ip]
                    frame.ip += 1
                    yield from self.call(step)
            finally:
                frames.pop()
        elif callable(action):
            try:
                result = action(self)
                if inspect.isgenerator(result):
                    yield from result
                elif result is _PAUSE:
                    yield _PAUSE
            except KernelError:
                raise
            except Exception as error:
                name = operation.name if isinstance(operation, Word) else repr(operation)
                raise KernelError(f"{name}: {error}") from error
        else:
            raise KernelError(f"Not executable: {operation!r}")

    @staticmethod
    def number(text):
        for parser in (lambda s: int(s, 10), lambda s: int(s, 0), float):
            try:
                return parser(text)
            except ValueError:
                pass
        raise KernelError(f"Unknown input: {text}")

    def evaluate(self, tib):
        source = Input(tib)
        inputs = self.task.inputs
        inputs.append(source)
        try:
            while (token := source.read()) is not None:
                word = self.tick(token)
                if word is None:
                    value = self.number(token)
                    if self.compiling:
                        self.literal(value)
                    else:
                        self.push(value)
                elif self.compiling and not word.immediate:
                    self.comma(word)
                else:
                    yield from self.call(word)
        finally:
            inputs.pop()

    @staticmethod
    def host_boundary(text):
        """Find end-code using Python tokens, excluding strings/comments."""
        offsets = [0]
        for line in text.splitlines(keepends=True):
            offsets.append(offsets[-1] + len(line))
        window = []
        try:
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                window.append(token)
                window = window[-3:]
                if len(window) != 3:
                    continue
                a, b, c = window
                if (a.type, a.string, b.type, b.string, c.type, c.string) != (
                        tokenize.NAME, "end", tokenize.OP, "-", tokenize.NAME, "code"):
                    continue
                if a.end != b.start or b.end != c.start:
                    continue
                start = offsets[a.start[0] - 1] + a.start[1]
                end = offsets[c.end[0] - 1] + c.end[1]
                if start and (text[start-1].isalnum() or text[start-1] in "_-"):
                    continue
                if end < len(text) and (text[end].isalnum() or text[end] in "_-"):
                    continue
                return start, end
        except (tokenize.TokenError, IndentationError):
            pass
        return None

    @staticmethod
    def _wrap_body(body):
        # Preserve continuation lines inside multiline string literals.
        protected = set()
        for token in tokenize.generate_tokens(io.StringIO(body).readline):
            if token.type == tokenize.STRING:
                protected.update(range(token.start[0] + 1, token.end[0] + 1))
        lines = body.splitlines(keepends=True)
        structural = [line for row, line in enumerate(lines, 1)
                      if row not in protected and line.strip()]
        margin = min((len(s) - len(s.lstrip(" \t")) for s in structural), default=0)
        result = "".join(line if row in protected or not line.strip()
                         else "    " + line[margin:]
                         for row, line in enumerate(lines, 1))
        if not structural:
            result += "    pass\n"
        return "def __operation(vm):\n" + result + "\n"

    def _host_definition(self):
        if self.compiling:
            raise KernelError("Cannot build host code inside a colon definition")
        name = self.input.read()
        self._name(name)
        boundary = self.host_boundary(self.input.remaining)
        if boundary is None:
            raise KernelError("Missing end-code (or malformed host body)")
        start, end = boundary
        body = self.input.remaining[:start]
        self.input.consume(end)
        namespace = dict(self.host)
        namespace.setdefault("KernelError", KernelError)
        try:
            source = self._wrap_body(body)
            exec(compile(source, f"<word {name}>", "exec"), namespace)
        except Exception as error:
            raise KernelError(f"Cannot define {name}: {error}") from error
        self.define(name, namespace["__operation"], category="code", source=body)

    @staticmethod
    def _unmatched_end():
        raise KernelError("end-code has no matching code")
