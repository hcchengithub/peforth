# peforth 2.1.0 AI User Manual

> [!TIP]
> **Explore the repository with AI.** Please make full use of GitHub Copilot or the Gemini sidebar in Chrome to discuss peforth directly with its source code. This manual is an overview, not an exhaustive reference: ask AI to explain any feature, trace its implementation, or explore design decisions in as much detail as you like.
>
> You can even ask AI to help design and implement new Forth words. In peforth's chat mode, a leading `/` passes the rest of the input to the Forth interpreter, so a new word can also become a new slash-invoked capability. The possibilities extend far beyond a fixed list of commands. Give the assistant access to the repository and relevant files so it can ground its explanations and suggestions in the actual implementation.

peforth 2.1.0 integrates an AI assistant directly into its Forth-driven environment. The Python host communicates with language models using standard HTTP client mechanisms, streaming responses into the interactive REPL while safely delegating tool invocations (such as dictionary queries and Forth code execution) back to the local VM.

---

## 1. Overview & Architectural Highlights

In peforth 2.1.0, AI support is built on four core pillars:

1. **Stateless & Stateful Dual Modes**:
   - **Stateless Mode**: Uses standard OpenAI-compatible `/chat/completions` endpoints. Ideal for lightweight queries, multi-turn chat, fast prompt evaluation, and compatibility with local or alternative model providers (Gemini, Groq, Ollama, vLLM).
   - **Stateful Mode**: Leverages OpenAI Agents API sessions with remote turn and state tracking, SSE streaming, and persistent cloud sessions.
2. **Multi-Provider & Profile Management (`providers.yaml`)**:
   - Declare any number of profiles with specific API endpoints, model IDs, token limits, and custom parameters.
   - Built-in automatic fallback to the first configured stateless profile if credentials for the active profile are unavailable.
3. **Word-Level Task Security Guard**:
   - Every word in the Forth dictionary carries a `safe=True` or `safe=False` property.
   - Pure, side-effect-free words execute transparently without interruption.
   - Any word performing disk I/O, process spawning, network calls, or dictionary mutations triggers the interactive security approval gate (`allow_once`, `trust_task`, `deny`, `cancel`).
4. **Local SQLite Session Mirror & Diagnostics**:
   - Remote and local sessions are synchronized incrementally into a local SQLite database (`sessions.sqlite3`).
   - Every diagnostic event and progress heartbeat is logged to `ai-diagnostics.sqlite3`, enabling live terminal emoji monitoring and watchdog stall supervision.

---

## 2. Configuration

peforth reads its runtime settings from two files located in your runtime configuration directory (Windows: `$HOME\.peforth\`, Ubuntu/WSL: `~/.peforth/`).

### 2.1 Environment Variables (`.env`)

Create `.env` by copying `.env.example`:

```dotenv
# API Keys for Model Providers
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Runtime and Path Overrides (Optional)
PEFORTH_CONFIG_DIR=~/.peforth
PEFORTH_AI_SKILLS_DIR=skills
PEFORTH_WSL_DISTRO=Ubuntu
PEFORTH_PWSH_PATH=

# Transport Timeouts (in seconds)
PEFORTH_AI_REQUEST_TIMEOUT=120
PEFORTH_AI_STREAM_TIMEOUT=300
PEFORTH_AI_POLL_INTERVAL=0.5
```

> [!IMPORTANT]
> Keep `.env` private and never commit it to source control. The bridge sends API keys only as HTTP `Bearer` authorization headers to the configured endpoints.

### 2.2 Multi-Provider Configuration (`providers.yaml`)

Define available providers and profiles in `providers.yaml`:

```yaml
default_profile: gemini-flash

profiles:
  gemini-flash:
    mode: stateless
    provider: gemini
    base_url: https://generativelanguage.googleapis.com/v1beta/openai
    api_key_env: GEMINI_API_KEY
    model: gemini-2.5-flash
    temperature: 0.7

  openai-gpt4o:
    mode: stateless
    provider: openai
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    model: gpt-4o
    temperature: 0.7

  openai-agent:
    mode: stateful
    provider: openai
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    model: gpt-4o

  local-ollama:
    mode: stateless
    provider: ollama
    base_url: http://localhost:11434/v1
    api_key_env: OLLAMA_API_KEY # Can be dummy or omitted
    model: qwen2.5-coder:latest
```

#### Startup Fallback Behavior
When peforth starts up, if the configured `default_profile` lacks an available API key in the environment, the runtime automatically falls back to the first available stateless profile that has valid credentials or requires no authentication (e.g. local Ollama).

---

## 3. Interactive REPL & Mode Switching

peforth 2.1.0 features a unified, dual-mode REPL controlled by Forth (`repl.f`).

```
peforth 2.1.0 [chat mode] (Provider: gemini-flash)
chat> 
```

### 3.1 Switching Modes
- **`chat` mode (`chat> ` prompt)**:
  - Every input line (or multiline block) submitted via Enter is automatically treated as a prompt and sent to the active AI session.
  - Type `/forth` to switch to Forth execution mode. In chat mode, a leading `/` sends the entire remaining input to the Forth interpreter; it is not limited to a predefined command list.
- **`forth` mode (`> ` prompt)**:
  - Standard Forth prompt where text is compiled or interpreted as Forth words.
  - Type `chat` to switch to chat mode.

### 3.2 Slash as a Gateway to the Full Forth Language

Many AI agents offer a fixed set of slash commands for leaving conversation mode or invoking system actions. peforth takes a more expressive approach: in chat mode, **the leading `/` passes the rest of the entire Terminal Input Buffer (TIB) to Forth**. The implementation in `repl.f` strips the leading slash and executes the remainder with `vm.dictate()`.

This is not a restricted command menu. You can run Forth expressions, define new words, and execute programs without first leaving chat mode:

```forth
chat> /1 2 + .
3
chat> /: square dup * ;
chat> /5 square .
25
chat> /forth
>
```

The slash is therefore a direct bridge to the extensible Forth language itself. `/forth` switches to the persistent Forth REPL; `/chat` is also available to return to chat mode.

### 3.3 Invoking AI from Forth Mode
- **`ai: <prompt>`**:
  Submits everything following `ai:` up to the end of the input buffer to the AI assistant and streams the response directly to the terminal:
  ```forth
  > ai: Write a Forth word to compute the Fibonacci sequence
  ```
- **`(ai)` Forth Word**:
  Low-level Forth bridge word:
  ```forth
  ( prompt-string stream? -- [response-string] )
  ```
  - `stream? = true`: Streams assistant tokens to `stdout` in real time.
  - `stream? = false`: Pushes the full assistant answer string onto the Data Stack.
  ```forth
  s" What is 123 * 456 in Forth?" false (ai) . cr
  ```

### 3.4 Command-Line One-Shot Mode (`f -c`)
Run prompts directly from your shell without launching the interactive REPL:
```bash
# Ask a one-shot question
f -c "Explain the role of projectk.py in peforth"

# Continue a specific session
f -id sess_abc123 -c "Now optimize the function you provided"
```

---

## 4. Fine-Grained Task Security Model

Security in peforth 2.1.0 is implemented directly at the vocabulary level.

### 4.1 Word Safety Annotations
- In `base.f` and extension vocabularies, safe, pure arithmetic, stack, and query words are explicitly marked:
  ```forth
  last :: safe=True
  ```
- Words that access the filesystem, shell out, establish network connections, or modify the compiler state (e.g., `code`, `system`, `file-write`, `re-define`) are unannotated or marked `safe=False`.

### 4.2 Approval in Practice

When AI-generated Forth reaches a word that requires approval, peforth pauses the Task and presents the proposed code and its purpose. The current interface offers four choices:

```text
[AI Proposes Forth Code]
Purpose: Print Hello World using Python.
Source:
<py> print("Hello World") </py>

1. Allow Once
2. Trust this AI task
3. Deny this proposal
4. Cancel this AI task

Choose 1-4:
```

**Allow Once** approves the current checkpoint; another checkpoint may require another approval, even during the same Task. **Trust this AI task** allows the remaining execution of that Task. **Deny** rejects the proposal, while **Cancel** stops the AI Task.

This concise example illustrates the user-facing interaction; the exact proposals and number of prompts depend on the code being executed. For implementation details, inspect the security handling in `ai.py` and `ai.f` with GitHub Copilot or the Gemini sidebar in Chrome.

---

## 5. Local Session Store & Synchronization

All interactive conversations can be synchronized and inspected using the local SQLite mirror located at `<PEFORTH_CONFIG_DIR>/sessions/sessions.sqlite3`.

| Forth Command | Stack Effect | Description |
| :--- | :--- | :--- |
| `ai-sessions` | `( -- )` | Incrementally syncs sessions and prints a numbered list with IDs and timestamps. |
| `ai-sync` | `( -- )` | Runs incremental SQLite sync quietly and prints a short summary. |
| `n ai-session` | `( n -- )` | Inspects full message history and tool calls for session number `n`. |
| `n ai-use` | `( n -- )` | Selects session `n` as the active session for the current VM. |
| `n ai-export-session` | `( n [path] -- )` | Exports session `n` to a clean JSON document. |
| `ai-search <query>` | `( "query" -- )` | Searches message content and descriptions across all stored sessions. |
| `n ai-cleanup` | `( n -- )` | Permanently deletes session `n` and marks it `remote_deleted` locally. |
| `ai-cancel` | `( -- )` | Cancels an ongoing generation turn. |

---

## 6. Live Diagnostics & Progress Watchdog

peforth 2.1.0 records fine-grained diagnostic events in `ai-diagnostics.sqlite3`.

### 6.1 Diagnostic Logging Monitor
Run the logging monitor from the repository or runtime directory:
```bash
python tools/peforth_logging_monitor.py
```
- Streams real-time emoji events (💬 user prompt, 🤖 assistant chunk, ⚙️ tool call, 🔒 security review).
- Displays latency and token usage statistics.

### 6.2 Progress Watchdog
The watchdog supervises long-running AI turns to detect hangs or stalled network connections:
```bash
python tools/peforth_watchdog.py
```
- Monitors objective progress (new tool call IDs, expanding token streams, or state transitions).
- Alerts via terminal messages or desktop notifications if an active turn produces no objective progress within the threshold (default: 5 minutes).

---

## 7. Troubleshooting & FAQ

- **`No API key configured for profile <name>`**:
  Check that the corresponding environment variable (e.g., `OPENAI_API_KEY`, `GEMINI_API_KEY`) is exported in your shell or present in `~/.peforth/.env`.
- **Switching Models on the Fly**:
  Simply ask the AI in natural language; there is no need to memorize Forth commands or edit `providers.yaml` for an ordinary model switch. For example:
  ```forth
  > ai: Switch the active LLM to Google Gemini 3.8 Flash
  ```
  The requested model must be available through a configured provider and valid credentials.
- **Permission Denied on Security Prompt**:
  If a proposal was rejected, you can inspect what the model attempted by running `ai-status` or checking `tools/peforth_logging_monitor.py`.
- **WSL PowerShell Interoperability**:
  On Ubuntu/WSL, set `PEFORTH_PWSH_PATH` in `.env` if automatic detection of `pwsh.exe` fails.
