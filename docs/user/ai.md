# peforth 2.1.0 AI User Manual

> [!TIP]
> **Explore the repository with AI.** Please make full use of GitHub Copilot or the Gemini sidebar in Chrome to discuss peforth directly with its source code. This manual is an overview, not an exhaustive reference: ask AI to explain any feature, trace its implementation, or explore design decisions in as much detail as you like.
>
> You can even ask AI to help design and implement new Forth words. In peforth's chat mode, a leading `/` passes the rest of the input to the Forth interpreter, so a new word can also become a new slash-invoked capability. The possibilities extend far beyond a fixed list of commands. Give the assistant access to the repository and relevant files so it can ground its explanations and suggestions in the actual implementation.

peforth 2.1.0 is an AI-first environment where you don't need to memorize complex commands or syntax to get real work done. You simply talk to the assistant in natural language, and it uses its built-in skills, vision capabilities, terminal controls, and Forth tools to help you inspect, automate, and control your computer.

---

## 1. Zero-Burden Interaction: Just Chat, or Use `/` for Forth

When you launch `f`, peforth starts directly in **`chat>` mode** whenever a usable AI provider key is configured:

```text
p e f o r t h   v 2
2.1.0

Talk with our GitHub repo using Copilot for help, code samples, and the whys behind peforth.
Chat with AI directly. Type '/help' for instructions, '/forth' for Forth mode.

[Enter] submits / [Ctrl+J] adds a line / [Esc] interrupt
chat>
```

- **Natural Language First**: Type what you want in plain language and press **Enter**. Use **Ctrl+J** (or **Esc** then **Enter**) to add multiple lines.
- **Slash (`/`) as a Gateway to Full Forth**: Many AI tools only give you a fixed menu of slash commands. In peforth, **a leading `/` sends the rest of your input directly to the Forth interpreter**:
  ```forth
  chat> /1 2 + .
  3
  chat> /: square dup * ;
  chat> /5 square .
  25
  chat> /forth
  >
  ```
  You can run calculations, invoke any Forth word, or define new words on the fly without leaving `chat>` mode. Type `/forth` to switch to the `>` Forth prompt, and `chat` to return.

---

## 2. Vision & Screen Perception: See Images, Photos, and Your Live Desktop

peforth AI is not limited to text—it can **see**.

- **View Local Photos & Online Images**:
  Ask the AI to inspect any local image file (screenshots, diagrams, photos) or an HTTPS image URL. Just mention the file path or URL in your prompt:
  - *"Look at `D:\screenshots\error.png` and tell me what went wrong."*
  - *"Compare the chart in this image with our latest test results."*
- **Live Desktop Capture (See Your Screen)**:
  You don't even have to take a screenshot manually. Ask peforth AI to capture and look at your live Windows desktop—either the full virtual screen or a specific region:
  - *"Take a look at my screen right now—what is the dialog box asking?"*
  - *"Capture the top-right quarter of my desktop and read the status numbers."*

---

## 3. Text-Mode Computer Use: Inspect and Control Herdr Panes

When running inside a **Herdr** terminal workspace, peforth AI supports full **text-mode Computer Use**:

- **See Its Own Screen**: The AI can read the visible text and scrollback of its own terminal pane to review prior output or verify how a display rendered.
- **Observe Neighboring Panes & Background Tasks**: It can look across your workspace to read what is happening in other panes or tabs—such as a running web server, a build log, a debugger, or another coding agent.
  - *"Check the server log running in the right-hand pane and see why the request failed."*
  - *"Show the pane IDs on all borders so we can refer to them easily."*
- **Operate Other Panes**: With your approval, peforth AI can type text, send keystrokes (like `Enter` or `Ctrl-C`), launch commands in other panes, or coordinate tasks with other agents running in parallel.
  - *"Run the test suite in pane `w1:p2` and let me know when it finishes."*

---

## 4. Self-Diagnosis & Conversation Memory

peforth AI keeps detailed records of its own operations and past conversations, and knows how to analyze them for you:

- **Analyze Its Own Diagnostic Logs**:
  Every turn, tool call, heartbeat, and error is recorded in a local SQLite diagnostic database (`ai-diagnostics.sqlite3`). If something felt slow or a request failed, simply ask:
  - *"Inspect your own diagnostic logs from the last session and tell me why that turn timed out."*
  - *"Check the WSL peforth diagnostic database and summarize today's conversations."*
- **Search & Reuse Past Conversations**:
  All sessions are mirrored locally in SQLite (`sessions.sqlite3`). You can ask the AI to search past discussions by keyword, review previous solutions, or export a conversation to JSON.
- **Promote Local Chat to Cloud Session**:
  Start chatting quickly in lightweight **Stateless** mode. Whenever a conversation becomes important enough to preserve as a long-running cloud session, ask the AI (or run `/ai-promote`) to distill the context and promote it into a **Stateful** Agents API session.

---

## 5. Mobile Notifications & Desktop Alerts

Walk away from your desk while peforth handles a long job—it has several ways to reach you:

- **LINE Messenger Notifications to Your Phone**:
  peforth can send push messages straight to your phone via the LINE Messaging API:
  - *"Run this benchmark, and send me a LINE notification with the summary when it's done."*
- **Audio Chimes (Nokia Tune)**:
  When an AI turn takes longer than 30 seconds, peforth automatically plays a gentle Nokia phrase so you know it has finished. You can also ask it to play a chime (`/nokia`, `/nokia2`, `/nokia-full`) anytime.
- **Top-Most Windows Message Box**:
  Need an unmissable visual alert or a quick Yes/No decision on screen? peforth can pop up a native Windows dialog box on top of all windows.
- **System Clipboard Integration**:
  Ask the AI to read what you just copied to your clipboard, or have it place generated code and summaries directly into your clipboard (`/clipboard@` and `/clipboard!`) with full Unicode and emoji support.

---

## 6. Switch AI Brains Anytime

peforth supports multiple AI providers (OpenAI, Google Gemini, Groq, and local Ollama models) and seamlessly manages them for you:

- **Switch Models in Plain Language**:
  No need to edit config files or remember command syntax to change models. Just tell the AI:
  - *"Switch the active LLM to Google Gemini 3.8 Flash"*
  - *"Switch to OpenAI GPT-5.4 with medium reasoning"*
  - *"What AI providers and profiles are available right now?"*
- **Automatic Startup Fallback**:
  If your default provider's API key isn't set in `.env`, peforth automatically checks your configured profiles in `providers.yaml` and falls back to the first provider with valid credentials (or keyless local Ollama) so you land in `chat>` mode ready to work.

---

## 7. Security That Stays Out of Your Way

Because peforth AI can run real code and control your system, it includes a built-in safety gate that protects you without slowing you down:

- **Safe Operations Run Automatically**: Reading the dictionary, doing math, inspecting panes, or capturing the screen are marked `safe=True` and run immediately without nagging you.
- **Clear 1–4 Approval Prompt for System Actions**: Whenever the AI proposes running shell commands, modifying files, or controlling another terminal pane, it pauses and shows you the exact code and purpose:

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

Choose **1 (Allow Once)** for a single step, or **2 (Trust this AI task)** to let the AI finish the rest of the current task uninterrupted.

---

## 8. Quick Setup & Live Monitor

### Minimal `.env` Setup
In your runtime directory (`~/.peforth/.env` on Linux/WSL, or `$HOME\.peforth\.env` on Windows), copy `.env.example` to `.env` and fill in only the keys you use:

```dotenv
# Configure one or more AI providers
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key

# Optional: Receive mobile notifications on LINE
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_token
LINE_USER_ID=your_line_user_id
```

*(See `providers.yaml.example` if you want to customize model profiles or add local Ollama models.)*

### Watching the Live Monitor & Watchdog
Want to see a live emoji stream of what the AI is doing behind the scenes (prompts, streaming chunks, tool calls, token usage) and get alerted if a turn stalls for more than 5 minutes?

1. **Open a new terminal window.**
2. **Run:**
   ```bash
   f -e run-monitor
   ```
Press `Ctrl-C` anytime to close the monitor.
