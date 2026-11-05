---
name: line-notify
description: >-
  Send LINE push messages or notifications to the user via the LINE Messaging API.
  Activate this skill whenever the user asks to send a LINE message, notify them on LINE,
  or push task completion/status alerts to their LINE account.
---

# LINE Notification Skill

This skill sends push messages directly to the user's LINE account using the LINE Messaging API. It works natively under Windows (PowerShell 7) and under Linux / WSL.

## Prerequisites & Environment Variables

Make sure the following environment variables are set in your current environment:
- `LINE_CHANNEL_ACCESS_TOKEN`: The LINE Messaging API Channel Access Token (Bearer).
- `LINE_USER_ID`: The target LINE User ID (starts with `U...`).

## Usage in peforth

Check the current active environment (from `=== System Environment ===` or `system_info`):

### 1. Under Windows (PowerShell 7)
Execute directly in PowerShell using `run_pwsh`:

#### Send a direct text message:
```forth
s" pwsh.exe -NoProfile -File ~/.peforth/skills/line-notify/scripts/send_line_message.ps1 'Your message text here'" run_pwsh stringify . cr
```
Or directly using inline PowerShell:
```forth
s" $body = @{ to = $env:LINE_USER_ID; messages = @(@{ type = 'text'; text = 'Hello from peforth!' }) } | ConvertTo-Json -Depth 5 -Compress; $headers = @{ Authorization = 'Bearer ' + $env:LINE_CHANNEL_ACCESS_TOKEN }; $res = Invoke-WebRequest -Uri 'https://api.line.me/v2/bot/message/push' -Method Post -Headers $headers -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($body)); Write-Output ('LINE HTTP status: ' + [int]$res.StatusCode)" run_pwsh stringify . cr
```

#### Send a multi-line message from a file:
```forth
s" pwsh.exe -NoProfile -File ~/.peforth/skills/line-notify/scripts/send_line_message.ps1 -MessageFile 'path/to/report.txt'" run_pwsh stringify . cr
```

### 2. Under Linux / WSL (Bash)
Execute via `run_bash` using the helper script `send_line_message.sh`:

#### Send a direct text message:
```forth
s" bash ~/.peforth/skills/line-notify/scripts/send_line_message.sh 'Your message text here'" run_bash stringify . cr
```

#### Send a multi-line message from a file:
```forth
s" bash ~/.peforth/skills/line-notify/scripts/send_line_message.sh --message-file /path/to/report.txt" run_bash stringify . cr
```
