# peforth v2

**peforth is an AI-first Forth environment hosted by Python.** It combines a small extensible Forth kernel, direct access to Python, and an optional AI-assisted terminal REPL in the single `f` command.

> **The best way to get to know peforth is to talk directly to this repository.** The source code and its Git history are our most reliable documentation. Rather than trying to read every document first, open this GitHub repository in Google Chrome and use the Gemini sidebar to talk with it: ask questions or request sample code.
>
> **Be cautious if the answer comes instantly.** Gemini may be hallucinating or answering from general knowledge instead of the repository. A gentle follow-up such as "Could you take a closer look at the relevant source before answering?" may help.

**Version 2 is now the mainline implementation on `master`.** The migration from v1 has been completed; the previous migration branch is no longer required for installation.

## Highlights

- **Forth + Python:** Define Forth words and embed host-side Python through `code ... end-code`. Use Python libraries without a separate foreign-function runtime.
- **Project K kernel:** A Python-hosted Forth VM supporting cooperative Task pause/resume, input streams, dictionary introspection, and extensible words.
- **Interactive REPL:** Enter Forth directly, define your own words, inspect the dictionary, and switch between `forth` and `chat` modes.
- **Optional AI assistant:** The OpenAI Agents API integration provides conversational help and can propose Forth actions in the active VM, subject to local approval.
- **Transparent sources:** Core Forth vocabulary is in `peforth/f/`; host runtime and integrations live in `peforth/*.py`.

> **Compatibility:** peforth v2 is a major rewrite, not a drop-in replacement for v1. Legacy features such as the v1 debugger, Jupyter integration, and `peforth.ok()` are not supported. Use the v1.33 release if your application depends on those interfaces.

## Requirements

- Python **3.10 or newer**
- Git
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended for installation)
- An OpenAI Platform API key **only if you want AI features**. Ordinary Forth execution works without one.

The development installation is sourced from this repository; it is not presented here as a published PyPI release.

## Install

Windows and Ubuntu/WSL should use **separate checkouts and virtual environments**.

### Ubuntu / WSL

```bash
git clone https://github.com/hcchengithub/peforth.git ~/.peforth
cd ~/.peforth
uv venv
uv pip install -e .
~/.peforth/.venv/bin/f
```

To invoke `f` by name from other directories in the current shell:

```bash
export PATH="$HOME/.peforth/.venv/bin:$PATH"
f
```

For WSL, keep this Linux checkout inside its Linux filesystem (for example, `~/.peforth`), not under `/mnt/c`.

### Windows PowerShell

```powershell
git clone https://github.com/hcchengithub/peforth.git "$HOME\.peforth"
Set-Location "$HOME\.peforth"
uv venv
uv pip install -e .
& "$HOME\.peforth\.venv\Scripts\f.exe"
```

To invoke `f` by name from other directories in the current PowerShell session:

```powershell
$env:PATH = "$HOME\.peforth\.venv\Scripts;$env:PATH"
f
```

If `uv` reports `invalid peer certificate: UnknownIssuer` on a managed Windows network, use native Windows certificate handling:

```powershell
uv --native-tls pip install -e .
```

Do not disable TLS certificate verification.

## CLI help and monitoring

Run `f -h` to see the command-line options. The `-e` option executes the remaining arguments as Forth input. Use `-l` or `--load` to include Forth source files; repeat the option to load multiple files. Put all load options before `-e` or `-c`, since those options consume the remaining arguments:

```bash
f -l ./definitions.f --load ./program.f -e run-program
```

For example, start the diagnostic monitor with:

```bash
f -e run-monitor
```

- **Monitor:** Reads the local SQLite diagnostic log in read-only mode and displays existing and new runtime and AI events. It runs in the foreground; press `Ctrl-C` to stop it.

- **Watchdog:** Runs by default inside the Monitor. It alerts when an AI turn makes no objective progress for five minutes or when a runtime being monitored exits unexpectedly. On Windows, including WSL, alerts appear as Windows Message Boxes. It warns but does not cancel a turn or stop a process.

## Quick start

Start `f` and enter ordinary Forth:

```forth
1 2 + . cr
: square dup * ;
5 square . cr
words
```

Define a Forth word directly in Python:

```forth
code double
    vm.push(vm.pop() * 2)
end-code

21 double . cr
```

The host Python code runs in the same process as the Forth VM, so it has the normal permissions of your local user account.

To leave the REPL, enter `bye` or press Ctrl-D. For Forth definitions, introspection, parsing, control structures, and more Python integration examples, see [peforth manual（漂亮字）](docs/user/peforth%20manual.md) and [peforth manual (English)](docs/user/peforth%20manual%20%28English%29.md).

## Optional AI assistant

Set `OPENAI_API_KEY` in the process environment or in `~/.peforth/.env` (Windows: `$HOME\.peforth\.env`). Keep it private and never commit it.

Example local configuration:

```dotenv
OPENAI_API_KEY=your-platform-api-key
# Set this to a model supported by your API project:
# PEFORTH_AI_MODEL=your-model-id
PEFORTH_AI_SKILLS_DIR=skills
```

Inside the REPL:

```forth
ai: Explain what a Forth defining word is.
chat
```

In `chat` mode, subsequent input goes to the selected AI session. Enter `forth` to return to Forth mode. Other commands include `ai-status`, `ai-sessions`, `ai-new`, and `ai-confirm`.

**Local execution is permissioned:** When the assistant proposes Forth code via `peforth_run_forth`, peforth asks for approval. You can approve once, trust only the current AI task, deny, or cancel. Approved code executes in the **live local VM** and can use its Python bridge; review proposals before approving them. See [AI support](docs/user/ai.md) for details about approvals, sessions, configuration, and troubleshooting.

AI API usage is optional and billed according to your OpenAI Platform account and selected model.

## Documentation

See the [documentation index](docs/README.md) for the full map. [User guides](docs/user/) contain the Forth manuals and AI usage guide; [development documents](docs/development/) contain design, diagnostics, plans, and project notes.

## Project layout

| Location | Purpose |
| --- | --- |
| `peforth/projectk.py` | Core Forth VM and Task execution |
| `peforth/f/base.f` | Base vocabulary, defining words, and compiler-level constructs |
| `peforth/f/auxiliary.f` | Auxiliary Forth words |
| `peforth/f/ai.f` | Forth-facing AI words and control flow |
| `peforth/repl.py` | Terminal REPL and runtime initialization |
| `peforth/ai_bridge.py`, `peforth/ai_tools.py` | AI transport, session helpers, and host tools |
| `docs/user/` | User manuals and AI usage guide |
| `docs/development/` | Design, diagnostics, development plans, and project notes |
| `docs/README.md` | Documentation index |
| `skills/`, `plugins/` | Repository-owned AI skill and plugin assets |
| `tests/` | Automated tests |

The `skills/` and `plugins/` source directories are not automatically installed into external AI CLIs.

## Updating and developing

This is an **editable source checkout**. To update, inspect your local changes and pull from `master`:

```bash
cd ~/.peforth
git status
git pull --ff-only
uv pip install -e .
```

Run the test suite from the checkout using your environment's Python; for example:

```bash
.venv/bin/python -m unittest discover -s tests
```

On Windows, use `.venv\Scripts\python.exe` instead.

Do not run `git pull` over uncommitted modifications without reviewing them first. The historical [V2 migration plan](docs/development/v2-migration-plan.md) is retained as background, not as the current installation guide.

## License

[MIT](LICENSE)
