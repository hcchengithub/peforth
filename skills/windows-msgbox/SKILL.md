---
name: windows-msgbox
description: >-
  Display a native Windows top-most Message Box on the user's desktop from WSL using PowerShell.
  Activate this skill when the user wants a desktop popup alert, local reminder, or free alternative
  to LINE notifications on their Windows machine.
---

# Windows MessageBox Notification Skill (WSL -> Windows)

This skill pops up a system-wide, top-most Windows dialog box (`System.Windows.Forms.MessageBox` with `ServiceNotification`) from inside WSL using [send_msgbox.sh](./scripts/send_msgbox.sh).

It automatically probes `/run/WSL/*_interop` to find a live WSL interop socket (avoiding hangs when `WSL_INTEROP` in a long-running shell session becomes stale) and encodes the PowerShell payload in UTF-16LE Base64 (`-EncodedCommand`) so multi-line text, quotes, and emojis render cleanly.

## Usage

### 1. Non-blocking popup (returns immediately while dialog stays on screen)

```bash
bash ~/.gemini/config/skills/windows-msgbox/scripts/send_msgbox.sh "時間到囉！記得休息一下～"
```

### 2. Custom title and icon

```bash
bash ~/.gemini/config/skills/windows-msgbox/scripts/send_msgbox.sh \
  --title "🌬️ 頭痛熱敷提醒" \
  --icon Information \
  --message "記得拿吹風機給頭痛吹吹熱風喔！"
```

Supported `--icon` values: `Information` (default), `Warning`, `Error`, `Question`, `None`.

### 3. Wait for user to click OK (`--wait`)

```bash
bash ~/.gemini/config/skills/windows-msgbox/scripts/send_msgbox.sh --wait "請確認後按下確定繼續執行"
```
