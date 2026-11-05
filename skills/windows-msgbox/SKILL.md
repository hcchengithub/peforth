---
name: windows-msgbox
description: >-
  Display a native Windows top-most Message Box on the user's desktop (works natively on Windows and from WSL).
  Activate this skill when the user wants a desktop popup alert, local reminder, or free alternative
  to LINE notifications on their Windows machine.
---

# Windows MessageBox Notification Skill

This skill pops up a system-wide, top-most Windows dialog box (`System.Windows.Forms.MessageBox` with `ServiceNotification`) on the user's desktop. It works natively under Windows (PowerShell) and cross-environment from WSL.

## Usage in peforth

Check the current active environment (from `=== System Environment ===` or `system_info`):

### 1. Under Windows (PowerShell 7)
Execute directly in PowerShell using `run_pwsh`:

#### Non-blocking popup (Recommended — returns immediately so the Forth REPL is not blocked):
```forth
s" Start-Process powershell.exe -WindowStyle Hidden -ArgumentList '-NoProfile','-Command','Add-Type -AssemblyName System.Windows.Forms; [void][System.Windows.Forms.MessageBox]::Show(''''時間到囉！記得休息一下～'''',''''💡 peforth 提醒'''',''''OK'''',''''Information'''',''''Button1'''',''''ServiceNotification'''')'" run_pwsh stringify . cr
```
Or run the helper script:
```forth
s" pwsh.exe -NoProfile -File ~/.peforth/skills/windows-msgbox/scripts/send_msgbox.ps1 -Message '時間到囉！記得休息一下～'" run_pwsh stringify . cr
```

#### Wait for user to click OK:
```forth
s" Add-Type -AssemblyName System.Windows.Forms; [void][System.Windows.Forms.MessageBox]::Show('請確認後按下確定繼續執行','💡 peforth 提醒','OK','Information','Button1','ServiceNotification')" run_pwsh stringify . cr
```

### 2. Under WSL (Linux -> Windows Desktop)
Execute via `run_bash` using the helper script `send_msgbox.sh`:

#### Non-blocking popup:
```forth
s" bash ~/.peforth/skills/windows-msgbox/scripts/send_msgbox.sh '時間到囉！記得休息一下～'" run_bash stringify . cr
```

#### Custom title and icon:
```forth
s" bash ~/.peforth/skills/windows-msgbox/scripts/send_msgbox.sh --title '🌬️ 頭痛熱敷提醒' --icon Information --message '記得拿吹風機吹吹熱風喔！'" run_bash stringify . cr
```
Supported icon values: `Information` (default), `Warning`, `Error`, `Question`, `None`.

#### Wait for user to click OK:
```forth
s" bash ~/.peforth/skills/windows-msgbox/scripts/send_msgbox.sh --wait '請確認後按下確定繼續執行'" run_bash stringify . cr
```
