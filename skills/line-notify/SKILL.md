---
name: line-notify
description: >-
  Send LINE push messages or notifications to the user via the LINE Messaging API.
  Activate this skill whenever the user asks to send a LINE message, notify them on LINE,
  or push task completion/status alerts to their LINE account.
---

# LINE Notification Skill

This skill sends push messages directly to the user's LINE account using its bundled script [send_line_message.sh](./scripts/send_line_message.sh).

## Usage

### 1. Send a direct text message

```bash
bash ~/.peforth/skills/line-notify/scripts/send_line_message.sh "Your message text here"
```

### 2. Send a multi-line message from a file

For longer or multi-line reports, write the message to a temporary file and pass `--message-file`:

```bash
tmp_msg=$(mktemp)
cat <<'EOF' > "$tmp_msg"
✅ Task Completed
- Item 1: PASS
- Item 2: PASS
EOF
bash ~/.peforth/skills/line-notify/scripts/send_line_message.sh --message-file "$tmp_msg"
rm -f "$tmp_msg"
```

## Windows and WSL

If the skill script runs in WSL but LINE_CHANNEL_ACCESS_TOKEN and LINE_USER_ID are set in Windows, pass those variables to WSL for this PowerShell process with WSLENV. This does not persist the setting or print the credentials.

    $forwardVars = 'LINE_CHANNEL_ACCESS_TOKEN:LINE_USER_ID'
    if ($env:WSLENV) {
        $env:WSLENV = $env:WSLENV + ':' + $forwardVars
    } else {
        $env:WSLENV = $forwardVars
    }

    # Replace Hello World!! with the message to send.
    $bashCommand = 'bash ~/.peforth/skills/line-notify/scripts/send_line_message.sh $''Hello World!!'''
    & wsl.exe --exec bash -lc $bashCommand
    if ($LASTEXITCODE -ne 0) {
        throw ('LINE script failed with exit code ' + $LASTEXITCODE)
    }

The doubled single quotes in the PowerShell string produce Bash's $'...' quoted message argument. Check for HTTP 200 and LINE push succeeded in the script output. If the credentials are already set inside WSL, use the Bash examples above and do not forward them.



When invoking this from Windows through peforth run_pwsh, keep the PowerShell source ASCII-only: non-ASCII message literals sent through PowerShell stdin may be corrupted. For non-ASCII text, encode each character as a Bash ANSI-C escape in the message argument; Bash decodes \uNNNN for BMP characters and \UNNNNNNNN for supplementary characters. For example, the code points U+5403 U+98EF U+4E86 can be passed as:

    $bashCommand = 'bash ~/.peforth/skills/line-notify/scripts/send_line_message.sh $''\u5403\u98ef\u4e86'''

## Configuration

Set `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_USER_ID` in the environment before sending. The script has no embedded credential defaults; do not commit tokens to the repository.

## Troubleshooting & Environment Variables

- **Dry Run**: Set `LINE_NOTIFY_DISABLED=1` to print the JSON payload without sending; the required token and user ID must still be set.
- **SSL Certificate Error (curl exit code 60)**: In corporate proxy/VPN environments (e.g., Netskope) where the system CA bundle might fail TLS verification, retry with `LINE_INSECURE_SSL=1` or specify `LINE_CA_CERT_FILE=/path/to/cert.pem`.
- **Verification**: Check that the script outputs `HTTP 200` and `LINE push succeeded` with exit code `0`.
