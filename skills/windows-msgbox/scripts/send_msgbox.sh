#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash send_msgbox.sh "message text"
  bash send_msgbox.sh --title "Custom Title" --icon Information --message "message text"
  bash send_msgbox.sh --message-file /path/to/file.txt

Options:
  --message <text>        Message body to display
  --message-file <path>   Read message body from file
  --title <text>          Dialog box title (default: "💡 Antigravity 提醒")
  --icon <type>           Information | Warning | Error | Question | None (default: Information)
  --wait                  Wait for the user to click OK before returning (default: non-blocking)
EOF
}

MESSAGE=""
TITLE="💡 Antigravity 提醒"
ICON="Information"
WAIT_FOR_CLICK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --message)
      [[ $# -ge 2 ]] || { echo "ERROR: --message requires a value" >&2; exit 2; }
      MESSAGE="$2"
      shift 2
      ;;
    --message-file)
      [[ $# -ge 2 ]] || { echo "ERROR: --message-file requires a path" >&2; exit 2; }
      [[ -f "$2" ]] || { echo "ERROR: message file not found: $2" >&2; exit 2; }
      MESSAGE="$(<"$2")"
      shift 2
      ;;
    --title)
      [[ $# -ge 2 ]] || { echo "ERROR: --title requires a value" >&2; exit 2; }
      TITLE="$2"
      shift 2
      ;;
    --icon)
      [[ $# -ge 2 ]] || { echo "ERROR: --icon requires a value" >&2; exit 2; }
      ICON="$2"
      shift 2
      ;;
    --wait)
      WAIT_FOR_CLICK=1
      shift
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "ERROR: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$MESSAGE" ]]; then
        echo "ERROR: message already provided" >&2
        exit 2
      fi
      MESSAGE="$1"
      shift
      ;;
  esac
done

if [[ -z "$MESSAGE" && $# -gt 0 ]]; then
  MESSAGE="$*"
fi

if [[ -z "$MESSAGE" ]]; then
  echo "ERROR: message text is required" >&2
  usage >&2
  exit 2
fi

POWERSHELL_EXE="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
CMD_EXE="/mnt/c/Windows/System32/cmd.exe"

if [[ ! -x "$POWERSHELL_EXE" ]]; then
  echo "ERROR: powershell.exe not found at $POWERSHELL_EXE" >&2
  exit 1
fi

# Ensure WSL_INTEROP points to a live interop socket (never rely on a stale socket)
ensure_wsl_interop() {
  if [[ -n "${WSL_INTEROP:-}" && -S "${WSL_INTEROP}" ]]; then
    if timeout 1 "$CMD_EXE" /c rem </dev/null >/dev/null 2>&1; then
      return 0
    fi
  fi
  for s in /run/WSL/*_interop; do
    [[ -S "$s" ]] || continue
    if timeout 1 env WSL_INTEROP="$s" "$CMD_EXE" /c rem </dev/null >/dev/null 2>&1; then
      export WSL_INTEROP="$s"
      return 0
    fi
  done
  echo "ERROR: Could not find an active WSL_INTEROP socket in /run/WSL/" >&2
  return 1
}

ensure_wsl_interop

# Build PowerShell script using Base64 UTF-16LE (-EncodedCommand) to avoid any quote/newline escaping issues
ENCODED_INNER=$(python3 - "$MESSAGE" "$TITLE" "$ICON" <<'PY'
import base64, sys

msg, title, icon = sys.argv[1], sys.argv[2], sys.argv[3]
ps_escape = lambda s: s.replace("'", "''")

ps_code = (
    "Add-Type -AssemblyName System.Windows.Forms; "
    f"[void][System.Windows.Forms.MessageBox]::Show('{ps_escape(msg)}', '{ps_escape(title)}', "
    f"'OK', '{ps_escape(icon)}', 'Button1', 'ServiceNotification')"
)
print(base64.b64encode(ps_code.encode("utf-16-le")).decode("ascii"))
PY
)

if [[ "$WAIT_FOR_CLICK" == "1" ]]; then
  "$POWERSHELL_EXE" -NoProfile -NonInteractive -WindowStyle Hidden -EncodedCommand "$ENCODED_INNER" </dev/null >/dev/null 2>&1
else
  "$POWERSHELL_EXE" -NoProfile -NonInteractive -Command \
    "Start-Process powershell.exe -WindowStyle Hidden -ArgumentList '-NoProfile -NonInteractive -EncodedCommand $ENCODED_INNER'" \
    </dev/null >/dev/null 2>&1
fi

echo "Windows MessageBox displayed (socket: ${WSL_INTEROP})."
