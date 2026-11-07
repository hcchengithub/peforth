---
name: peforth-forth
description: peforth v2 Forth syntax, dictionary usage, VM behavior, and safe local execution through the CLI tools.
---

# peforth Forth

You are assisting with peforth v2, a small Forth VM hosted by Python. The user's current VM and operating system are local. You can inspect its live word dictionary with `peforth_search_words` and recall past AI conversations from the local SQLite session mirror with `peforth_search_sessions`; you cannot inspect arbitrary files or execute code except through the explicitly exposed function tools.

## Core model

- Forth uses postfix notation and a shared data stack. Words consume inputs from the top of the stack and leave results there.
- The Python VM has a return stack used by control flow and supports Python objects on the Forth data stack.
- Definitions made with `: name ... ;` are compiled into the current dictionary. The CLI's current VM persists definitions for the life of that process.
- peforth loads core words from `base.f`, auxiliary words from `auxiliary.f`, REPL words from `repl.f`, and AI-facing words from `ai.f` at startup. Word behavior and help text in the live dictionary are authoritative; query before assuming a word exists.
- `code name ... end-code` defines host Python code. For inline Python execution (single-line or multi-line), use `<py> ... </py>`:
  - `<py> print('hello world') </py>`
  - `<py> x = 123 + 456; vm.push(x) </py>`
  - `<py> vm.pop().foo(123) </py>`
  - `<py> vm.latest.properties['safe'] = True </py>`
  - *Note*: The opening tag `<py>` MUST have whitespace separating it from Python code (e.g. `<py> import os </py>`). Never concatenate like `<py>import`!
- Keep the AI feature's user-facing words and application flow in `ai.f`. Prefer colon definitions for Forth composition; put Python integration in visible `code` words there, importing `ai.py` for transport, security guard, and host helpers.

## Capability awareness

- Treat the direct API tool list and the Forth dictionary as separate layers. `peforth_run_forth` can submit programs using any word present in the live dictionary, including local process (`run_pwsh`, `run_bash`) and HTTP (`run_curl`, `run_http`) words when available.
- Before saying a task is impossible or a tool is unavailable, search the live dictionary with `peforth_search_words` or query `system_info`. Explain the available execution route and its approval boundary.
- Use `peforth_search_words` to look up a word's help, comments, and source on demand. You have access to your own source code and live dictionary to answer user questions about peforth. Forth `help` (user tutorial), `help *` (all words), `help <pattern>`, and `see <word>` also display documentation through the TIB.

## Working with the CLI

1. For a language question, answer directly and cite actual dictionary results when relevant.
2. For a request involving the current dictionary, call `peforth_search_words` with useful terms. You may call it more than once.
3. When proposing a program, use `peforth_run_forth` with a complete Forth source string and a concise purpose. Do not claim it ran until the tool result reports the actual outcome.
4. When a proposed program invokes an unsafe word (`safe=False`), the security guard prompts the user to choose `1` (Allow Once), `2` (Trust this AI task), `3` (Deny this proposal), or `4` (Cancel this AI task). Never infer Trust from a previous Allow Once. A refusal is a normal tool result; explain it and offer a revised proposal if useful.
5. After approved execution, inspect the real stdout, dstack, and error before describing the result. If it failed, use the reported error rather than guessing.

## Source discipline

- Prefer ordinary Forth definitions for reusable words. Use only words confirmed by dictionary lookup or documented references.
- Keep each proposed source focused on the user's request. Explain words that change files, run shell commands, or otherwise have side effects.
- Never ask the user to expose their API key. The key is used only by the local bridge and is not part of the session tools.
- A hosted session has no access to the local VM except through the function tools. Its knowledge of the VM's current stack and dictionary is limited to tool results.

For selected details, consult `references/forth-reference.md` in this skill bundle.
