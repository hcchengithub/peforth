"""Read-only progress supervision for peforth diagnostic databases."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import time

NO_PROGRESS_SECONDS = 5 * 60
REMINDER_SECONDS = 5 * 60


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def collapsed_preview(text: str | None, limit: int = 60) -> str:
    normalized = " ".join((text or "").split())
    if len(normalized) <= limit:
        return normalized or "(none)"
    return normalized[:limit] + "…"


def short_id(value: str | None) -> str:
    return (value or "unknown")[:8]


def _payload(row: dict) -> dict:
    try:
        parsed = json.loads(row.get("payload_json") or "{}")
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _display_time(value: datetime | None) -> str:
    if value is None:
        return "unknown"
    return value.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def _current_environment() -> str:
    if os.name == "nt":
        return "windows"
    try:
        if "microsoft" in Path("/proc/version").read_text(encoding="utf-8").casefold():
            return "wsl"
    except OSError:
        pass
    return "other"


def _process_creation_time(pid: int) -> float | None:
    """Return process creation time as Unix seconds, or None if unavailable."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class FILETIME(ctypes.Structure):
            _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(0x1000, False, int(pid))  # QUERY_LIMITED_INFORMATION
        if not handle:
            error = ctypes.get_last_error()
            return None if error == 5 else 0.0
        try:
            created, exited, kernel, user = FILETIME(), FILETIME(), FILETIME(), FILETIME()
            if not kernel32.GetProcessTimes(handle, ctypes.byref(created), ctypes.byref(exited),
                                            ctypes.byref(kernel), ctypes.byref(user)):
                return None
            ticks = (created.dwHighDateTime << 32) | created.dwLowDateTime
            return ticks / 10_000_000 - 11_644_473_600
        finally:
            kernel32.CloseHandle(handle)

    stat_path = Path(f"/proc/{int(pid)}/stat")
    try:
        stat = stat_path.read_text(encoding="ascii")
        close_paren = stat.rfind(")")
        fields = stat[close_paren + 2:].split()
        start_ticks = int(fields[19])  # proc stat field 22; fields start at field 3
        boot_time = None
        for line in Path("/proc/stat").read_text(encoding="ascii").splitlines():
            if line.startswith("btime "):
                boot_time = int(line.split()[1])
                break
        if boot_time is None:
            return None
        return boot_time + start_ticks / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, IndexError, ZeroDivisionError):
        return 0.0


def process_matches_runtime(runtime: dict) -> bool | None:
    """Check liveness and PID reuse; None means this host cannot verify it."""
    if runtime.get("environment") != _current_environment():
        return None
    pid = runtime.get("process_id")
    if not pid:
        return None
    if runtime.get("hostname"):
        try:
            current_host = os.uname().nodename
        except AttributeError:
            current_host = os.environ.get("COMPUTERNAME")
        if current_host and str(runtime["hostname"]).casefold() != current_host.casefold():
            return None
    created = _process_creation_time(int(pid))
    if created is None:
        return None
    if created == 0.0:
        return False
    started = parse_timestamp(runtime.get("started_at"))
    if started is None:
        return None
    # The runtime row is written by this process after process creation. A PID
    # whose current process started later is reused; allow only small clock/tick
    # rounding, not a lower-age bound (system startup may be slow).
    return created <= started.timestamp() + 0.1


class Watchdog:
    """Maintain only current candidate state while consuming events by ID."""

    def __init__(self, connection, *, orphan_lookback_hours: float = 24,
                 process_checker=process_matches_runtime, now=utc_now):
        value = float(orphan_lookback_hours)
        if not math.isfinite(value) or value <= 0:
            raise ValueError("orphan-lookback-hours must be a positive finite number")
        self.connection = connection
        self.lookback_hours = value
        self.process_checker = process_checker
        self.now = now
        self.cursor = 0
        self.runtimes: dict[str, dict] = {}
        self.turns: dict[str, dict] = {}
        self.orphans: dict[str, dict] = {}

    def _cutoff(self, now: datetime) -> datetime:
        try:
            return now - timedelta(hours=self.lookback_hours)
        except OverflowError:
            return datetime.min.replace(tzinfo=timezone.utc)

    def _load_runtime(self, runtime_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT * FROM runtimes WHERE runtime_id = ?", (runtime_id,)
        ).fetchone()
        return dict(row) if row else None

    def _last_runtime_activity(self, runtime_id: str) -> str | None:
        row = self.connection.execute(
            "SELECT recorded_at FROM timeline WHERE runtime_id = ? "
            "ORDER BY recorded_at DESC, event_id DESC LIMIT 1", (runtime_id,)
        ).fetchone()
        return row[0] if row else None

    def _load_turn(self, turn_id: str) -> dict | None:
        row = self.connection.execute(
            """SELECT t.*, c.content_text AS prompt_text
               FROM turns AS t LEFT JOIN contents AS c ON c.content_id = t.prompt_content_id
               WHERE t.turn_id = ?""", (turn_id,)
        ).fetchone()
        if not row or row["ended_at"] is not None:
            return None
        turn = dict(row)
        turn["last_activity_at"] = turn["started_at"]
        turn["last_progress_at"] = turn["started_at"]
        turn["last_progress_type"] = "ai_turn_started"
        turn["last_heartbeat"] = ""
        turn["remote_states"] = {}
        turn["call_ids"] = set()
        turn["output_lengths"] = {}
        self.turns[turn_id] = turn
        return turn

    def _apply_event(self, row: dict) -> None:
        runtime_id = row.get("runtime_id")
        recorded = parse_timestamp(row.get("recorded_at"))
        runtime = self.runtimes.get(runtime_id)
        if runtime is not None and recorded is not None:
            previous = parse_timestamp(runtime.get("last_activity_at"))
            if previous is None or recorded > previous:
                runtime["last_activity_at"] = row.get("recorded_at")

        turn_id = row.get("turn_id")
        if row.get("event_type") == "ai_turn_started" and turn_id:
            turn = self.turns.get(turn_id) or self._load_turn(turn_id)
        else:
            turn = self.turns.get(turn_id) if turn_id else None
        if turn is None:
            return
        if recorded is not None:
            previous_activity = parse_timestamp(turn.get("last_activity_at"))
            if previous_activity is None or recorded > previous_activity:
                turn["last_activity_at"] = row.get("recorded_at")
        kind = row.get("event_type") or ""
        payload = _payload(row)
        if kind == "ai_heartbeat":
            turn["last_heartbeat"] = str(payload.get("message") or "")
            return

        progressed = False
        progress_type = None
        call_id = row.get("call_id")
        if call_id and call_id not in turn["call_ids"]:
            turn["call_ids"].add(call_id)
            progressed, progress_type = True, "new_call_id"

        remote_event = payload.get("event_type") if kind == "sse_event_received" else None
        state = None
        if isinstance(remote_event, str) and remote_event.startswith("agent.session.turn."):
            state = remote_event.rsplit(".", 1)[-1]
        if state in {"in_progress", "requires_action", "completed", "failed", "cancelled", "incomplete"}:
            state_key = row.get("remote_turn_id") or payload.get("remote_turn_id") or turn_id
            if turn["remote_states"].get(state_key) != state:
                turn["remote_states"][state_key] = state
                progressed, progress_type = True, f"remote_turn_{state}"

        if kind == "tool_result_submitted":
            progressed, progress_type = True, "tool_result_accepted"

        if kind == "sse_event_received":
            length = payload.get("output_length")
            if isinstance(length, (int, float)):
                length_key = row.get("remote_turn_id") or turn_id
                previous_length = turn["output_lengths"].get(length_key, 0)
                if length > previous_length:
                    turn["output_lengths"][length_key] = length
                    progressed, progress_type = True, "assistant_output_growth"
            elif isinstance(payload.get("delta_length"), (int, float)) and payload["delta_length"] > 0:
                progressed, progress_type = True, "assistant_output_growth"

        if progressed and recorded is not None:
            turn["last_progress_at"] = row.get("recorded_at")
            turn["last_progress_type"] = progress_type

        if kind in {"ai_turn_completed", "ai_turn_failed", "ai_turn_cancel_requested"}:
            self.turns.pop(turn_id, None)

    def initialize(self) -> int:
        row = self.connection.execute("SELECT COALESCE(MAX(event_id), 0) FROM timeline").fetchone()
        self.cursor = int(row[0])
        now = self.now()
        cutoff = self._cutoff(now)
        runtimes = self.connection.execute(
            """SELECT r.*,
                      (SELECT recorded_at FROM timeline AS e WHERE e.runtime_id = r.runtime_id
                       ORDER BY e.recorded_at DESC, e.event_id DESC LIMIT 1) AS last_activity_at
               FROM runtimes AS r WHERE r.finished_at IS NULL"""
        ).fetchall()
        dead_candidates = []
        for row in runtimes:
            runtime = dict(row)
            runtime_id = runtime["runtime_id"]
            alive = self.process_checker(runtime)
            if alive is True:
                self.runtimes[runtime_id] = runtime
            elif alive is False:
                activity = parse_timestamp(runtime.get("last_activity_at")) or parse_timestamp(runtime.get("started_at"))
                if activity is not None and activity >= cutoff:
                    dead_candidates.append(runtime)

        candidate_ids = list(self.runtimes) + [item["runtime_id"] for item in dead_candidates]
        if candidate_ids:
            placeholders = ",".join("?" for _ in candidate_ids)
            rows = self.connection.execute(
                f"""SELECT t.turn_id FROM turns AS t
                     WHERE t.ended_at IS NULL AND t.runtime_id IN ({placeholders})""",
                tuple(candidate_ids),
            ).fetchall()
            for row in rows:
                self._load_turn(row["turn_id"])

        for runtime in dead_candidates:
            self._consider_orphan(runtime, now, cutoff)

        for turn in list(self.turns.values()):
            if turn.get("runtime_id") not in self.runtimes:
                continue
            events = self.connection.execute(
                """SELECT event_id, runtime_id, turn_id, recorded_at, event_type,
                          remote_turn_id, call_id, payload_json
                   FROM timeline WHERE turn_id = ? AND event_id <= ?
                     AND event_type IN ('ai_turn_started', 'ai_heartbeat',
                                        'sse_event_received', 'current_actions_response_received',
                                        'tool_call_started', 'tool_result_submitted')
                   ORDER BY event_id""",
                (turn["turn_id"], self.cursor),
            ).fetchall()
            for event in events:
                self._apply_event(dict(event))

        self._refresh_open_turns()
        return self.cursor

    def _consider_orphan(self, runtime: dict, now: datetime, cutoff: datetime) -> None:
        runtime_id = runtime.get("runtime_id")
        last_activity = parse_timestamp(runtime.get("last_activity_at"))
        if last_activity is None:
            last_activity = parse_timestamp(runtime.get("started_at"))
        if last_activity is None or last_activity < cutoff:
            return
        open_turn = next((turn for turn in self.turns.values()
                          if turn.get("runtime_id") == runtime_id), None)
        key = f"orphan:{runtime_id}"
        self.orphans[key] = {
            "key": key, "kind": "orphan", "runtime_id": runtime_id,
            "turn_id": open_turn.get("turn_id") if open_turn else None,
            "prompt_text": open_turn.get("prompt_text") if open_turn else "",
            "last_activity_at": last_activity,
            "age_seconds": max(0.0, (now - last_activity).total_seconds()),
        }

    def _refresh_open_turns(self) -> None:
        for turn_id in list(self.turns):
            row = self.connection.execute(
                "SELECT ended_at FROM turns WHERE turn_id = ?", (turn_id,)
            ).fetchone()
            if row is None or row[0] is not None:
                self.turns.pop(turn_id, None)

    def poll(self) -> list[dict]:
        rows = self.connection.execute(
            "SELECT * FROM timeline WHERE event_id > ? ORDER BY event_id", (self.cursor,)
        ).fetchall()
        events = [dict(row) for row in rows]
        for row in events:
            self.cursor = max(self.cursor, int(row["event_id"]))
            runtime_id = row.get("runtime_id")
            kind = row.get("event_type")
            if kind == "runtime_started" and runtime_id not in self.runtimes:
                runtime = self._load_runtime(runtime_id)
                if runtime and runtime.get("finished_at") is None:
                    runtime["last_activity_at"] = row.get("recorded_at")
                    alive = self.process_checker(runtime)
                    if alive is True:
                        self.runtimes[runtime_id] = runtime
                    elif alive is False:
                        now = self.now()
                        self._consider_orphan(runtime, now, self._cutoff(now))
            if kind == "runtime_finished":
                self.runtimes.pop(runtime_id, None)
                self.orphans.pop(f"orphan:{runtime_id}", None)
                for turn_id, turn in list(self.turns.items()):
                    if turn.get("runtime_id") == runtime_id:
                        self.turns.pop(turn_id, None)
                continue
            self._apply_event(row)
            if kind in {"ai_turn_completed", "ai_turn_failed", "ai_turn_cancel_requested"}:
                self.turns.pop(row.get("turn_id"), None)
        self._refresh_open_turns()

        now = self.now()
        cutoff = self._cutoff(now)
        for runtime_id, runtime in list(self.runtimes.items()):
            alive = self.process_checker(runtime)
            if alive is False:
                self.runtimes.pop(runtime_id, None)
                self._consider_orphan(runtime, now, cutoff)
        for key, orphan in list(self.orphans.items()):
            if orphan["last_activity_at"] < cutoff:
                self.orphans.pop(key, None)
        return events

    def current_issues(self, now: datetime | None = None) -> dict[str, dict]:
        now = now or self.now()
        issues = dict(self.orphans)
        for turn_id, turn in self.turns.items():
            runtime = self.runtimes.get(turn.get("runtime_id"))
            if runtime is None:
                continue
            last_progress = parse_timestamp(turn.get("last_progress_at"))
            if last_progress is None:
                last_progress = parse_timestamp(turn.get("started_at")) or now
            age = (now - last_progress).total_seconds()
            if age < NO_PROGRESS_SECONDS:
                continue
            key = f"no-progress:{turn_id}"
            prompt = collapsed_preview(turn.get("prompt_text"))
            heartbeat = collapsed_preview(turn.get("last_heartbeat"))
            message = (
                "No objective AI progress for 5 minutes\n"
                f"Runtime: {short_id(turn.get('runtime_id'))} | Turn: {short_id(turn_id)}\n"
                f"Prompt: {prompt}\n"
                f"No progress: {_duration(age)}\n"
                f"Last progress: {_display_time(last_progress)} ({turn.get('last_progress_type') or 'unknown'})\n"
                f"Heartbeat: {heartbeat}"
            )
            issues[key] = {
                "key": key, "kind": "no-progress", "runtime_id": turn.get("runtime_id"),
                "turn_id": turn_id, "prompt_text": prompt,
                "last_progress_at": last_progress,
                "last_progress_type": turn.get("last_progress_type"),
                "last_heartbeat": heartbeat, "age_seconds": age,
                "title": "peforth Watchdog — no progress", "message": message,
            }
        for issue in self.orphans.values():
            last_activity = issue["last_activity_at"]
            age = (now - last_activity).total_seconds()
            message = (
                "Runtime ended unexpectedly\n"
                f"Runtime: {short_id(issue['runtime_id'])}\n"
                f"Last activity: {_display_time(last_activity)} ({_duration(age)} ago)"
            )
            if issue.get("turn_id"):
                message += (
                    f"\nOpen turn: {short_id(issue['turn_id'])}"
                    f"\nPrompt: {collapsed_preview(issue.get('prompt_text'))}"
                )
            issue.update({"title": "peforth Watchdog — orphaned runtime", "message": message,
                          "age_seconds": age})
        return issues


class ReminderManager:
    """Process-local reminder state; only one notifier child may be open."""

    def __init__(self, start_notifier, *, now=time.monotonic, log=print):
        self.start_notifier = start_notifier
        self.now = now
        self.log = log
        self.states: dict[str, dict] = {}
        self.child = None
        self.child_key = None

    def update(self, issues: dict[str, dict]) -> None:
        now = self.now()
        for key in list(self.states):
            state = self.states[key]
            if key not in issues:
                state["resolved"] = True
                if key != self.child_key:
                    self.states.pop(key, None)
        for key, issue in issues.items():
            if key not in self.states:
                self.states[key] = {"issue": issue, "next_due": now, "resolved": False}
            else:
                self.states[key]["issue"] = issue
                self.states[key]["resolved"] = False
        self._reap_child(now)
        if self.child is not None:
            return
        ready = [(state["next_due"], key, state) for key, state in self.states.items()
                 if not state["resolved"] and state["next_due"] <= now]
        if not ready:
            return
        _, key, state = min(ready, key=lambda item: (item[0], item[1]))
        try:
            self.child = self.start_notifier(state["issue"])
            self.child_key = key
        except Exception as exc:
            self.log(f"peforth watchdog notification failed: {exc}")
            state["next_due"] = now + REMINDER_SECONDS

    def _reap_child(self, now: float) -> None:
        if self.child is None or self.child.poll() is None:
            return
        code = self.child.returncode
        key = self.child_key
        self.child = None
        self.child_key = None
        if code:
            self.log(f"peforth watchdog notifier exited with status {code}")
        if key is None:
            return
        state = self.states.get(key)
        if state is None:
            return
        if state["resolved"]:
            self.states.pop(key, None)
        else:
            state["next_due"] = now + REMINDER_SECONDS


def validate_lookback_hours(value: str | float) -> float:
    try:
        hours = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("orphan-lookback-hours must be a positive finite number") from exc
    if not math.isfinite(hours) or hours <= 0:
        raise ValueError("orphan-lookback-hours must be a positive finite number")
    return hours
