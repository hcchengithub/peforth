#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

usage() {
  cat <<'EOF'
Usage:
  bash send_line_message.sh "message text"
  bash send_line_message.sh --message "message text"
  bash send_line_message.sh --message-file /path/to/file.txt

Optional environment variables:
  LINE_CHANNEL_ACCESS_TOKEN   Required LINE Messaging API channel access token
  LINE_USER_ID                Required target LINE user ID
  LINE_API_ENDPOINT           default: https://api.line.me/v2/bot/message/push
  LINE_NOTIFY_DISABLED        if set to 1, print payload only and do not send
  LINE_CURL_MAX_TIME          default: 30
  LINE_CURL_CONNECT_TIMEOUT   default: 10
  LINE_VERBOSE                if set to 1, enable extra curl verbose output
  LINE_INSECURE_SSL           if set to 1, pass -k to curl (temporary workaround)
  LINE_CA_CERT_FILE           custom CA bundle path for curl --cacert
EOF
}

MESSAGE=""

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

: "${LINE_CHANNEL_ACCESS_TOKEN:?ERROR: LINE_CHANNEL_ACCESS_TOKEN is required}"
: "${LINE_USER_ID:?ERROR: LINE_USER_ID is required}"

LINE_API_ENDPOINT="${LINE_API_ENDPOINT:-https://api.line.me/v2/bot/message/push}"
LINE_NOTIFY_DISABLED="${LINE_NOTIFY_DISABLED:-0}"
LINE_CURL_MAX_TIME="${LINE_CURL_MAX_TIME:-30}"
LINE_CURL_CONNECT_TIMEOUT="${LINE_CURL_CONNECT_TIMEOUT:-10}"
LINE_VERBOSE="${LINE_VERBOSE:-0}"
LINE_INSECURE_SSL="${LINE_INSECURE_SSL:-0}"
LINE_CA_CERT_FILE="${LINE_CA_CERT_FILE:-}"

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

log "Preparing LINE push request"
log "Endpoint: ${LINE_API_ENDPOINT}"
log "Target user id suffix: ${LINE_USER_ID: -6}"
log "Message length: ${#MESSAGE}"
log "Curl connect timeout: ${LINE_CURL_CONNECT_TIMEOUT}s, max time: ${LINE_CURL_MAX_TIME}s"
if [[ "$LINE_INSECURE_SSL" == "1" ]]; then
  log "SSL verification: INSECURE (-k enabled)"
elif [[ -n "$LINE_CA_CERT_FILE" ]]; then
  log "SSL verification: custom CA bundle ${LINE_CA_CERT_FILE}"
else
  log "SSL verification: system CA bundle"
fi

MESSAGE_JSON=$(printf '%s' "$MESSAGE" | json_escape)
USER_JSON=$(printf '%s' "$LINE_USER_ID" | json_escape)

PAYLOAD=$(cat <<EOF
{
  "to": ${USER_JSON},
  "messages": [
    {
      "type": "text",
      "text": ${MESSAGE_JSON}
    }
  ]
}
EOF
)

if [[ "$LINE_NOTIFY_DISABLED" == "1" ]]; then
  log "LINE_NOTIFY_DISABLED=1, skip sending"
  printf '%s\n' "$PAYLOAD"
  exit 0
fi

TMP_BODY=$(mktemp)
trap 'rm -f "$TMP_BODY"' EXIT

CURL_ARGS=(
  -sS
  -o "$TMP_BODY"
  -w '%{http_code}'
  -X POST "$LINE_API_ENDPOINT"
  -H 'Content-Type: application/json'
  -H "Authorization: Bearer ${LINE_CHANNEL_ACCESS_TOKEN}"
  --connect-timeout "$LINE_CURL_CONNECT_TIMEOUT"
  --max-time "$LINE_CURL_MAX_TIME"
  --data "$PAYLOAD"
)

if [[ "$LINE_INSECURE_SSL" == "1" ]]; then
  CURL_ARGS=(-k "${CURL_ARGS[@]}")
fi

if [[ -n "$LINE_CA_CERT_FILE" ]]; then
  CURL_ARGS=(--cacert "$LINE_CA_CERT_FILE" "${CURL_ARGS[@]}")
fi

if [[ "$LINE_VERBOSE" == "1" ]]; then
  CURL_ARGS=(-v "${CURL_ARGS[@]}")
fi

log "Sending request to LINE API"
set +e
HTTP_CODE=$(curl "${CURL_ARGS[@]}")
CURL_RC=$?
set -e
if [[ "$CURL_RC" -ne 0 ]]; then
  log "curl failed with exit code ${CURL_RC}"
  case "$CURL_RC" in
    6) log "Diagnosis: DNS resolution failed" ;;
    7) log "Diagnosis: TCP connection failed/refused" ;;
    28) log "Diagnosis: connection or transfer timeout" ;;
    35) log "Diagnosis: TLS handshake failed" ;;
    60) log "Diagnosis: TLS certificate verify failed; try LINE_INSECURE_SSL=1 as a temporary test or provide LINE_CA_CERT_FILE" ;;
  esac
  if [[ -s "$TMP_BODY" ]]; then
    log "Partial response body:"
    cat "$TMP_BODY" >&2
    printf '\n' >&2
  fi
  exit "$CURL_RC"
fi

log "Received HTTP status: ${HTTP_CODE}"
printf 'HTTP %s\n' "$HTTP_CODE"
if [[ -s "$TMP_BODY" ]]; then
  log "Response body:"
  cat "$TMP_BODY"
  printf '\n'
else
  log "Response body: <empty>"
fi

if [[ "$HTTP_CODE" =~ ^2 ]]; then
  log "LINE push succeeded"
  exit 0
fi

log "LINE push failed"
exit 1
