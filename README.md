# peforth v2.1.0

**peforth is an AI-first Forth programming environment hosted by Python.**

> **"Forth drives Forth; Python provides host primitives."**

In peforth 2.1.0, the environment shifts from a Python-centric monolithic supervisor to a pure Forth-driven architecture:
- **Minimal Bootloader (`main.py`)**: A tiny 9-line bootstrap shim.
- **Dependency-Free Micro-Kernel (`projectk.py`)**: Zero external dependencies, strictly 2 seed words (`code` and `end-code`), uniform `KernelError`, and generator coroutines.
- **Forth-Level REPL (`repl.f`)**: Multiline interactive input accumulation and dual-mode switching (`chat>` and `>`).
- **Word-Oriented Security (`ai.py`)**: Fine-grained task security where vocabulary words carry `safe=True` annotations. Pure Forth words run freely without friction; only unsafe words trigger the interactive `ai-approve` review workflow.
- **Integrated AI Assistant**: Conversational answers stream directly to the terminal; Forth code execution is delegated to `peforth_run_forth`.
- **SQLite Diagnostics & Live Monitoring**: Comprehensive event tracking in `ai-diagnostics.sqlite3` with terminal emoji live streaming (`peforth-monitor` / `tools/peforth_logging_monitor.py`) and watchdog progress supervision (`tools/peforth_watchdog.py`).

---

## Architecture: Repo vs. Runtime

peforth distinguishes between the **development repository** and **runtime execution environments**:

- **Repository (`.../peforth`)**:
  Used solely for codebase development, Git version control, and running the contract test suite (`test_all.py`).
- **Runtimes (`~/.peforth` or `$HOME\.peforth`)**:
  Dedicated, standalone checkouts and virtual environments where peforth runs day-to-day.
  Windows and Ubuntu/WSL runtimes are kept strictly separate.

---

## Requirements

- Python **3.10 or newer**
- Git
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended for fast virtual environment management)
- An OpenAI-compatible API key (optional; only needed for AI chat and pair programming)

---

## Runtime Installation

### 1. Ubuntu / WSL Runtime

For WSL, keep this Linux checkout inside its native Linux filesystem (`~/.peforth`), not under `/mnt/c`:

```bash
git clone -b develop-210 https://github.com/hcchengithub/peforth.git ~/.peforth
cd ~/.peforth
uv venv
uv pip install --python .venv -e .
~/.peforth/.venv/bin/f
```

To invoke `f` by name from anywhere in your shell:

```bash
export PATH="$HOME/.peforth/.venv/bin:$PATH"
f
```

---

### 2. Windows PowerShell Runtime

```powershell
git clone -b develop-210 https://github.com/hcchengithub/peforth.git "$HOME\.peforth"
Set-Location "$HOME\.peforth"
uv venv
uv pip install --python .venv -e .
& "$HOME\.peforth\.venv\Scripts\f.exe"
```

To invoke `f` by name from anywhere in PowerShell:

```powershell
$env:PATH = "$HOME\.peforth\.venv\Scripts;$env:PATH"
f
```

> **Note for managed corporate networks**: If `uv` reports certificate errors, use native Windows certificate handling:
> ```powershell
> uv --native-tls pip install -e .
> ```

---

## Configuration (`.env`)

Copy `.env.example` to `.env` in your runtime directory (Windows: `$HOME\.peforth\.env`, Ubuntu/WSL: `~/.peforth/.env`):

```env
# AI Assistant configuration
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
# OPENAI_REASONING_EFFORT=none

# Diagnostic logging mode: normal (default), verbose, or disabled
PEFORTH_AI_LOG_MODE=normal

# Custom config/database directory (optional; defaults to ~/.peforth)
# PEFORTH_CONFIG_DIR=~/.peforth
```


---

## Quick Start

Launch `f` to enter the interactive Forth REPL:

```forth
\ Basic arithmetic and stack operations
1 2 + . cr
: square dup * ;
5 square . cr

\ Dictionary inspection
words py >>
help nokia

\ Audio chime notification (Windows & WSL)
nokia
nokia2
nokia-full

\ Switch to conversational AI Chat mode
chat
chat> tell me a joke
chat> forth
```

Or ask the AI directly from Forth mode:
```forth
ai: calculate 355 113 / in Forth
```

To exit peforth:
```forth
bye
```

---

## Diagnostics & Watchdog Monitoring

In a separate terminal or Herdr pane, launch the live diagnostic monitor:

```bash
peforth-monitor
# or:
python tools/peforth_logging_monitor.py
```

The monitor connects to `~/.peforth/ai-diagnostics.sqlite3` in read-only mode and displays live emoji events:
- 🚀 `runtime started` / 🏁 `runtime finished`
- 🌐 `HTTP request started` / ✅ `HTTP response received`
- 📡 `SSE stream opened` / 📨 `SSE event received`
- 🛠️ `tool call started` / 📤 `tool result submitted`
- 🙋 `approval requested` / 👍 `approval received`
- ▶️ `Forth execution started` / ⏹️ `Forth execution finished`

The embedded **Watchdog** alerts with a Windows Message Box if an active AI turn makes no objective progress for 5 minutes.

---

## Testing & Quality Assurance

To verify architectural contracts, kernel purity, security approval flow, and diagnostics:

```bash
python test_all.py
```
