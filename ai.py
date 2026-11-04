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
    """Search words in vm.words matching query."""
    q = query.lower()
    matches = []
    for name, word in vm.words.items():
        help_text = getattr(word, "help", "")
        comment = getattr(word, "comment", "")
        source = getattr(word, "source", "")
        if (q in name.lower() or
            q in help_text.lower() or
            q in comment.lower() or
            q in source.lower()):
            matches.append({
                "name": name,
                "category": getattr(word, "category", "host"),
                "help": help_text,
                "comment": comment,
                "safe": word.properties.get("safe", False) if hasattr(word, "properties") else False
            })
    return {"query": query, "count": len(matches), "words": matches[:30]}


SYSTEM_PROMPT = """You are an intelligent AI pair programmer embedded inside peforth VM.
You have access to two tools:
1. peforth_search_words: search available Forth vocabulary, words, and documentation.
2. peforth_run_forth: propose and execute Forth code in the user's local VM.

Important Rules:
- When asked to perform calculations, check dictionary, or solve problems in Forth, propose Forth code using peforth_run_forth.
- peforth stack words include: dup, drop, swap, over, rot, pick, roll, depth, dropall.
- Math words include: +, -, *, /, mod, =, <, >, 0=, 0<, 1+, 1-, not, and, or.
- Display words include: ., .s, cr, space, words, see.
- To print numbers or strings, use '.' (e.g. 's" text" .' or '123 .'). There is no 'type' word; '.' prints both strings and numbers without a trailing newline. Use 'cr' for newline.
- Colon definitions use ': name ... ;'.
- If your code uses non-safe words, the user will be prompted to approve the execution.
- Be concise, accurate, and helpful.
"""


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
    messages.append({"role": "user", "content": prompt})

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
                    if stream_response:
                        sys.stdout.write(f"\n[AI Proposes Forth Code]\nPurpose: {purpose}\nSource:\n{source.strip()}\n---\n")
                        sys.stdout.flush()

                    # Set in_ai_task so security decorator inspects words
                    prev_ai_task = vm.host.get("in_ai_task")
                    vm.host["in_ai_task"] = vm.task

                    tee = TeeOutput(sys.stdout)
                    old_stdout = sys.stdout
                    error_msg = None
                    try:
                        sys.stdout = tee
                        # Yield from evaluate so any security pause or words pause cooperative execution
                        yield from vm.evaluate(source)
                    except Exception as e:
                        error_msg = f"{type(e).__name__}: {e}"
                        sys.__stdout__.write(f"\n[Execution Error] {error_msg}\n")
                        sys.__stdout__.flush()
                    finally:
                        sys.stdout = old_stdout
                        vm.host["in_ai_task"] = prev_ai_task

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
