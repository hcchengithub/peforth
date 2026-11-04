"""peforth - AI Extension Module (v2.1.0)

Implements:
- Security Guard Decorator for vm.call (Task-level approval scope)
- Tools: peforth_search_words, peforth_run_forth
- (ai) cooperative turn generator with OpenAI-compatible SSE streaming
"""

import io
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


def load_dotenv(env_path=None):
    """Load environment variables from .env file using only standard library."""
    if env_path is None:
        candidates = [
            Path.cwd() / ".env",
            Path(__file__).resolve().parent / ".env",
            Path(__file__).resolve().parent.parent / ".env",
        ]
        for c in candidates:
            if c.exists():
                env_path = c
                break
    if env_path and os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key, val)


class TeeOutput(io.StringIO):
    """Mirror stdout to both the original stream and an internal buffer."""
    def __init__(self, target):
        super().__init__()
        self.target = target

    def write(self, s):
        try:
            self.target.write(s)
            self.target.flush()
        except Exception:
            pass
        return super().write(s)


def install_security_guard(vm):
    """Install security decorator on vm.call to protect against unsafe AI execution."""
    if getattr(vm, "_security_guard_installed", False):
        return
    vm._security_guard_installed = True

    original_call = vm.call

    def security_aware_call(operation):
        task = vm.task
        in_ai_task = vm.host.get("in_ai_task")

        # Security check applies only when running inside an AI Task context
        if in_ai_task is not None and task is in_ai_task:
            trusted_tasks = vm.host.setdefault("trusted_ai_tasks", set())
            if task not in trusted_tasks:
                resolved = vm._resolve(operation)
                is_safe = False
                if hasattr(resolved, "properties") and resolved.properties.get("safe"):
                    is_safe = True
                elif callable(resolved) and getattr(resolved, "_safe", False):
                    is_safe = True

                if not is_safe:
                    name = getattr(resolved, "name", repr(resolved))
                    sys.__stdout__.write(f"\n[Security] Word '{name}' is not marked as safe.\n")
                    sys.__stdout__.write("Task paused for review. Type 'resume' for single step, 'trust-task resume' to trust this task.\n")
                    sys.__stdout__.flush()

                    vm.host["pending_ai_task"] = task
                    yield vm.pause()

        yield from original_call(operation)

    vm.call = security_aware_call


TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "peforth_search_words",
            "description": "Search the current Forth dictionary (words, category, help, comments, source). Pure read-only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword to search in word names, help strings, or comments."
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "peforth_run_forth",
            "description": "Propose Forth source code to execute in the user's local VM. Subject to task security review.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Forth source code to evaluate in the VM."
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Clear explanation of why this Forth code is being executed."
                    }
                },
                "required": ["source", "purpose"],
                "additionalProperties": False,
            },
        },
    },
]


def tool_search_words(vm, query):
    """Search words in vm.words matching query (supports multi-token relevance scoring)."""
    tokens = [t.strip().lower() for t in query.split() if t.strip()]
    if not tokens:
        tokens = [query.strip().lower()]

    scored = []
    for name, word in vm.words.items():
        score = 0
        name_lower = name.lower()
        help_text = getattr(word, "help", "") or ""
        help_lower = help_text.lower()
        comment = getattr(word, "comment", "") or ""
        comment_lower = comment.lower()
        source = getattr(word, "source", "") or ""
        source_lower = source.lower()

        for tok in tokens:
            if tok == name_lower:
                score += 100
            elif tok in name_lower:
                score += 30
            if tok in help_lower:
                score += 20
            if tok in comment_lower:
                score += 10
            if tok in source_lower:
                score += 5

        if score > 0:
            scored.append((score, {
                "name": name,
                "category": getattr(word, "category", "host"),
                "help": help_text,
                "comment": comment,
                "safe": word.properties.get("safe", False) if hasattr(word, "properties") else False
            }))

    scored.sort(key=lambda item: item[0], reverse=True)
    matches = [item[1] for item in scored[:30]]
    return {"query": query, "count": len(matches), "words": matches}


SYSTEM_PROMPT = """You are an intelligent AI pair programmer embedded inside the peforth Forth environment.
peforth is an AI-first Forth environment hosted by Python. It seamlessly bridges Forth with Python: you can run native Forth, write Python host definitions, and execute Python code directly inside Forth!

You have access to two tools:
1. peforth_search_words: search available Forth vocabulary, words, help strings, and comments.
   *IMPORTANT*: peforth is a rich, evolving environment. When unsure whether a word exists, ALWAYS search the dictionary first!
2. peforth_run_forth: propose and execute Forth source code in the user's local VM.

=== Python Interoperability (You CAN execute Python directly!) ===
When the user asks you to run Python, write Python, or perform operations best suited for Python, DO NOT say you cannot run Python! Instead, propose Forth code using peforth's Python interoperability words inside peforth_run_forth:
- py: <statement>
    Execute a single-line Python statement.
    Example: py: print("Hello, World!")
    Example: py: import math; print(math.pi)
- py:: <line>
    Execute Python code up to the end of the line.
    Example: py:: print("Hello from py::")
- py> <expression>
    Evaluate a Python expression and push its result onto the Forth data stack.
    Example: py> 2**10 . cr
    Example: py> [x*x for x in range(5)] . cr
- <py> ... </py>
    Execute a multi-line Python code block.
    Example:
        <py>
        for i in range(3):
            print(f"Count: {i}")
        </py>
- <py> ... </pyV>
    Evaluate a multi-line Python expression and push its result onto the data stack.
- :: <method/statement>
    Invoke a method or statement on the Python object at the top of the data stack WITHOUT pushing a return value (in-place mutation, attribute assignment, void methods).
    Example: py> [3, 1, 2] dup :: sort() ( list is sorted in-place )
    Example: py> [1, 2] dup :: append(3)
    Example: ' myword :: safe=True
- :> <method/property>
    Invoke a method or property on the Python object at the top of the data stack and push its return value onto the stack.
    Example: s" hello world" :> upper() . cr
    Example: py> [1, 2, 3] :> __len__() . cr
- code <name> <python-body> end-code
    Define a new Forth word implemented directly in Python.
    Example:
        code greet
            print("Hello from custom Python word!")
        end-code
        greet

=== Forth Vocabulary & Fundamentals ===
- Stack manipulation: dup, drop, swap, over, rot, -rot, nip, 2dup, 2drop, depth, dropall, pick, roll, slice.
- Return/Temp stacks (task-private): >r, r>, r@, rdrop, >t, t@, t>.
- Math: +, -, *, /, mod, 1+, 1-, 2+, 2-, abs, negate, max, min.
- Comparisons: =, <>, !=, ==, <, >, <=, >=, 0=, 0<, within.
- Logic & Bitwise: not, and, or, AND, OR, NOT, XOR, <<, >>.
- Strings & Types: s" text", ." text", char <tok>, BL, CR, none, "", int, float, bool, str, list, dict, set, tuple, type, {}, [].
- Output: '.' prints TOS without newline (both numbers and strings); '.s' displays stack; 'cr' prints newline; 'space' prints a space.
- Colon definitions: ': name ... ;'
- Control structures:
    if ... else ... then
    for ... next (r@ is loop index)
    begin ... until
    begin ... while ... repeat
    case ... of ... endof ... endcase
- Defining words: constant, variable, value, to, create, does>.

=== Important Rules ===
- When executing code, always explain your purpose and propose clean Forth source code.
- If your proposed code executes non-safe words (such as <py>, file operations, or system commands), the VM task-level security guard will pause and ask the user for approval. This is normal and expected.
- Be concise, accurate, and helpful.
"""


def _sanitize_messages(messages):
    """Ensure every assistant message with tool_calls is properly closed by tool messages."""
    sanitized = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        sanitized.append(msg)
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            expected_ids = {tc["id"] for tc in msg["tool_calls"] if "id" in tc}
            j = i + 1
            tool_msgs = []
            while j < len(messages) and messages[j].get("role") == "tool":
                tool_msgs.append(messages[j])
                j += 1
            responded_ids = {tm.get("tool_call_id") for tm in tool_msgs}
            missing_ids = expected_ids - responded_ids
            for mid in missing_ids:
                tool_msgs.append({
                    "role": "tool",
                    "tool_call_id": mid,
                    "content": json.dumps({"error": "Tool execution was not completed."}, ensure_ascii=False)
                })
            sanitized.extend(tool_msgs)
            i = j
        else:
            i += 1
    return sanitized


def read_numbered_choice(
    prompt: str = "Choose 1-4: ",
    choices: tuple = ("1", "2", "3", "4"),
    default: str = "1",
    *,
    labels: dict = None,
    styles: dict = None,
) -> str:
    """Read a single-key or numbered choice with prompt_toolkit, falling back to input()."""
    labels = labels or {
        "1": "Allow Once",
        "2": "Trust this AI task",
        "3": "Deny this proposal",
        "4": "Cancel this AI task",
    }
    styles = styles or {}

    if not sys.stdin.isatty():
        return default

    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.keys import Keys
        from prompt_toolkit.formatted_text import ANSI
        import asyncio

        selected_index = [choices.index(default) if default in choices else 0]
        bindings = KeyBindings()

        def _confirm(event):
            event.current_buffer.text = choices[selected_index[0]]
            event.current_buffer.validate_and_handle()

        @bindings.add("c-m", eager=True)
        def _enter(event):
            _confirm(event)

        @bindings.add(" ", eager=True)
        def _space(event):
            _confirm(event)

        def _move_selection(event, step):
            selected_index[0] = (selected_index[0] + step) % len(choices)
            event.app.invalidate()

        @bindings.add(Keys.Up, eager=True)
        def _prev(event):
            _move_selection(event, -1)

        @bindings.add(Keys.Down, eager=True)
        def _next(event):
            _move_selection(event, 1)

        def _confirm_selected_choice(app, buffer):
            async def confirm_after_render():
                await asyncio.sleep(0.05)
                buffer.validate_and_handle()
            app.create_background_task(confirm_after_render())

        for choice in choices:
            def _select(event, selected=choice):
                selected_index[0] = choices.index(selected)
                event.current_buffer.text = selected
                event.app.invalidate()
                _confirm_selected_choice(event.app, event.current_buffer)
            bindings.add(choice, eager=True)(_select)

        def choice_prompt():
            selected = choices[selected_index[0]]
            selected_style = "\x1b[1;48;2;255;255;255;38;2;0;100;0m"
            reset = "\x1b[0m"
            rows = []
            for choice in choices:
                style = selected_style if choice == selected else styles.get(choice, "")
                suffix = reset if style else ""
                rows.append(f"{style}{choice}. {labels.get(choice, choice)}{suffix}")
            rows.extend(("", prompt))
            return ANSI("\n".join(rows))

        session = PromptSession(multiline=False, key_bindings=bindings)
        result = session.prompt(choice_prompt)
        return result.strip() if result and result.strip() in choices else default
    except Exception:
        for choice in choices:
            print(f"{choice}. {labels.get(choice, choice)}")
        try:
            val = input(prompt).strip()
            return val if val in choices else default
        except Exception:
            return default


def _http_chat_stream(base_url, api_key, model, messages, tools):
    """Send streaming Chat Completion request to OpenAI-compatible endpoint."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "stream": True,
    }

    # Automatically set reasoning_effort to "none" for reasoning models when using tools
    reasoning_effort = os.environ.get("OPENAI_REASONING_EFFORT")
    if reasoning_effort is None:
        if any(prefix in model.lower() for prefix in ("o1", "o3", "gpt-6")):
            reasoning_effort = "none"
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        return urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        if "reasoning_effort" in err_body:
            if "Unrecognized request argument" in err_body:
                payload.pop("reasoning_effort", None)
            else:
                payload["reasoning_effort"] = "none"
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            return urllib.request.urlopen(req, timeout=60)
        raise


def ai_turn(vm, prompt, stream_response):
    """Cooperative generator for one AI conversation turn."""
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        msg = ("\n[AI] OPENAI_API_KEY is not set.\n"
               "Please configure OPENAI_API_KEY in your environment or in a .env file.\n"
               "Example: export OPENAI_API_KEY=\"sk-...\"\n")
        if stream_response:
            sys.stdout.write(msg)
            sys.stdout.flush()
        else:
            vm.push(msg)
        return

    # Initialize or continue conversation session
    messages = vm.host.setdefault("ai_messages", [
        {"role": "system", "content": SYSTEM_PROMPT}
    ])
    messages = _sanitize_messages(messages)
    messages.append({"role": "user", "content": prompt})
    vm.host["ai_messages"] = messages

    accumulated_full_text = []

    # Outer loop for handling multi-turn tool calling
    while True:
        try:
            response = _http_chat_stream(base_url, api_key, model, messages, TOOLS_DEFINITION)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            err_msg = f"\n[AI Error] HTTP {e.code}: {err_body}\n"
            if stream_response:
                sys.stdout.write(err_msg)
                sys.stdout.flush()
            else:
                vm.push(err_msg)
            return
        except Exception as e:
            err_msg = f"\n[AI Error] Network request failed: {e}\n"
            if stream_response:
                sys.stdout.write(err_msg)
                sys.stdout.flush()
            else:
                vm.push(err_msg)
            return

        assistant_content = ""
        tool_calls_map = {}  # index -> {id, name, arguments}

        with response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line or not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                choices = chunk.get("choices", [])
                if not choices:
                    continue
                delta = choices[0].get("delta", {})

                # Text streaming
                content_chunk = delta.get("content")
                if content_chunk:
                    assistant_content += content_chunk
                    if stream_response:
                        sys.stdout.write(content_chunk)
                        sys.stdout.flush()

                # Tool calls streaming
                if "tool_calls" in delta:
                    for tc in delta["tool_calls"]:
                        idx = tc.get("index", 0)
                        if idx not in tool_calls_map:
                            tool_calls_map[idx] = {
                                "id": "",
                                "name": "",
                                "arguments": ""
                            }
                        if tc.get("id"):
                            tool_calls_map[idx]["id"] += tc["id"]
                        fn = tc.get("function", {})
                        if fn.get("name"):
                            tool_calls_map[idx]["name"] += fn["name"]
                        if fn.get("arguments"):
                            tool_calls_map[idx]["arguments"] += fn["arguments"]

        if assistant_content:
            accumulated_full_text.append(assistant_content)

        # Build assistant message object
        assistant_msg = {"role": "assistant"}
        if assistant_content:
            assistant_msg["content"] = assistant_content
        else:
            assistant_msg["content"] = None

        if tool_calls_map:
            formatted_tool_calls = []
            for idx in sorted(tool_calls_map.keys()):
                entry = tool_calls_map[idx]
                formatted_tool_calls.append({
                    "id": entry["id"] or f"call_{idx}",
                    "type": "function",
                    "function": {
                        "name": entry["name"],
                        "arguments": entry["arguments"],
                    }
                })
            assistant_msg["tool_calls"] = formatted_tool_calls
            messages.append(assistant_msg)

            # Execute each tool call
            for tc in formatted_tool_calls:
                call_id = tc["id"]
                fn_name = tc["function"]["name"]
                args_str = tc["function"]["arguments"]
                try:
                    args = json.loads(args_str) if args_str else {}
                except json.JSONDecodeError:
                    args = {}

                if fn_name == "peforth_search_words":
                    query = args.get("query", "")
                    if stream_response:
                        sys.stdout.write(f"\n[AI Tool] Searching dictionary for: {query!r}...\n")
                        sys.stdout.flush()
                    result_data = tool_search_words(vm, query)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": json.dumps(result_data, ensure_ascii=False)
                    })

                elif fn_name == "peforth_run_forth":
                    source = args.get("source", "")
                    purpose = args.get("purpose", "")

                    trusted_tasks = vm.host.get("trusted_ai_tasks", set())
                    is_trusted = (vm.task in trusted_tasks) or vm.host.get("ai_trusted", False)

                    decision = "allow_once"
                    if not is_trusted:
                        approval_word = vm.tick("ai-approve")
                        if approval_word:
                            stack_depth = len(vm.dstack)
                            vm.push({"purpose": purpose, "source": source})
                            yield from vm.call(approval_word)
                            decision = vm.pop() if len(vm.dstack) > stack_depth else "deny"
                        else:
                            if stream_response:
                                sys.stdout.write(f"\n[AI Proposes Forth Code]\nPurpose: {purpose}\nSource:\n{source.strip()}\n---\n")
                                sys.stdout.flush()

                    if decision == "trust_task":
                        vm.host.setdefault("trusted_ai_tasks", set()).add(vm.task)
                    elif decision == "deny":
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps({
                                "stdout": "",
                                "dstack": [repr(x) for x in vm.dstack],
                                "error": "User denied this proposal."
                            }, ensure_ascii=False)
                        })
                        continue
                    elif decision == "cancel":
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call_id,
                            "content": json.dumps({
                                "stdout": "",
                                "dstack": [repr(x) for x in vm.dstack],
                                "error": "User cancelled the AI task."
                            }, ensure_ascii=False)
                        })
                        return

                    # Execute the Forth code
                    prev_ai_task = vm.host.get("in_ai_task")
                    vm.host["in_ai_task"] = vm.task

                    trusted_set = vm.host.setdefault("trusted_ai_tasks", set())
                    was_in_trusted = vm.task in trusted_set
                    trusted_set.add(vm.task)

                    tee = TeeOutput(sys.stdout)
                    old_stdout = sys.stdout
                    error_msg = None
                    try:
                        sys.stdout = tee
                        yield from vm.evaluate(source)
                    except Exception as e:
                        error_msg = f"{type(e).__name__}: {e}"
                        sys.__stdout__.write(f"\n[Execution Error] {error_msg}\n")
                        sys.__stdout__.flush()
                    finally:
                        sys.stdout = old_stdout
                        vm.host["in_ai_task"] = prev_ai_task
                        if not was_in_trusted and decision != "trust_task":
                            trusted_set.discard(vm.task)

                    exec_result = {
                        "stdout": tee.getvalue(),
                        "dstack": [repr(x) for x in vm.dstack],
                        "error": error_msg
                    }
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": json.dumps(exec_result, ensure_ascii=False)
                    })
                else:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "content": json.dumps({"error": f"Unknown tool: {fn_name}"})
                    })
            # Continue loop to stream the assistant's follow-up
            continue
        else:
            # No tool calls; turn is complete
            messages.append(assistant_msg)
            break

    # Clean up trusted task status once turn is done
    trusted_tasks = vm.host.get("trusted_ai_tasks")
    if trusted_tasks and vm.task in trusted_tasks:
        trusted_tasks.remove(vm.task)
    vm.host["pending_ai_task"] = None

    if stream_response:
        sys.stdout.write("\n")
        sys.stdout.flush()
    else:
        vm.push("\n".join(accumulated_full_text))
