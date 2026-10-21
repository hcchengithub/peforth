import contextlib
import io
import json
import os
import unittest
from unittest.mock import patch

from peforth import ai_bridge, repl


class FakeResponse:
    status = 202
    headers = {}

    def __init__(self, body=b"{}"):
        self.body = body
        self.closed = False

    def read(self, size=-1):
        return self.body if size < 0 else self.body[:size]

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class NonStreamingTransportTests(unittest.TestCase):
    def test_cli_chat_selects_one_shot_non_stream_transport(self):
        class RecordingVM:
            def __init__(self):
                self.host = {}
                self.stack = []
                self.task = object()

            def push(self, value):
                self.stack.append(value)

            def tick(self, name):
                return name

            def execute(self, word):
                self.executed = (word, self.stack[:])
                self.stack.clear()
                return self.task

        vm = RecordingVM()
        with patch.object(repl, "create_vm", return_value=vm), \
                patch.object(ai_bridge, "_list_remote_sessions", return_value=[]), \
                patch.object(repl, "repl"):
            self.assertEqual(repl.main(["-c", "tell", "me", "a", "joke"]), 0)

        self.assertFalse(vm.host["ai_transport_stream_once"])
        self.assertEqual(vm.executed, ("(ai)", ["tell me a joke", True]))

    def test_turn_start_log_separates_terminal_and_api_stream_modes(self):
        class RecordingLogger:
            def store_content(self, *_):
                return 1

            def start_turn(self, *_args, **_kwargs):
                pass

            def append_event(self, _runtime_id, _turn_id, event_type, **kwargs):
                self.event_type = event_type
                self.payload = kwargs["payload"]

        class FakeVM:
            def __init__(self):
                self.host = {}

        vm = FakeVM()
        logger = RecordingLogger()
        vm.host.update(diagnostic_log=logger, diagnostic_runtime_id="runtime-1")

        ai_bridge._diagnostic_start_turn(
            vm, "a prompt", session_id="sess-1",
            terminal_output_stream=True, api_transport_stream=False,
        )

        self.assertEqual(logger.event_type, "ai_turn_started")
        self.assertEqual(logger.payload, {
            "terminal_output_stream": True,
            "api_transport_stream": False,
        })

    def test_create_session_nonstream_returns_session_then_polls(self):
        response = FakeResponse(b'{"id":"sess-new","status":"in_progress"}')
        payload = {"input": "tell me a joke", "stream": True}
        poll_events = [{"type": "agent.session.turn.completed"}]
        with patch.object(ai_bridge, "_request", return_value=response) as request, \
                patch.object(ai_bridge, "_poll_session_events", return_value=iter(poll_events)) as poll:
            events = list(ai_bridge._create_session(payload, stream=False))

        self.assertEqual(request.call_args.args[:2], ("POST", "/sessions"))
        self.assertFalse(request.call_args.args[2]["stream"])
        self.assertFalse(request.call_args.kwargs.get("stream", False))
        self.assertEqual(events[0], {
            "type": "agent.session.created",
            "session": {"id": "sess-new", "status": "in_progress"},
        })
        poll.assert_called_once()
        self.assertEqual(poll.call_args.args[0], "sess-new")
        self.assertTrue(response.closed)

    def test_followup_posts_prompt_without_opening_sse_and_recovers_saved_answer(self):
        order = []
        turn_pages = [
            {"data": [{"id": "turn-old", "status": "completed"}]},
            {"data": [{"id": "turn-new", "status": "completed"}]},
        ]
        response = FakeResponse()

        def api_get(path, **kwargs):
            order.append(("GET", path))
            if "/turns" in path:
                return turn_pages.pop(0)
            if "/items" in path:
                return {
                    "data": [{
                        "id": "msg-final", "type": "message", "role": "assistant",
                        "phase": "final_answer", "turn_id": "turn-new",
                        "content": [{"type": "output_text", "text": "A short joke."}],
                    }],
                    "has_more": False, "last_id": "msg-final",
                }
            if path.endswith("/sessions/sess-1"):
                return {"id": "sess-1", "status": "idle", "required_actions": []}
            self.fail(f"Unexpected API GET: {path}")

        def request(method, path, payload=None, **kwargs):
            order.append((method, path, payload))
            if method == "GET" and "events?stream=true" in path:
                raise TimeoutError("simulated delayed SSE response")
            return response

        with patch.dict(os.environ, {
                "PEFORTH_AI_REQUEST_TIMEOUT": "1",
                "PEFORTH_AI_TURN_TIMEOUT": "1",
                "PEFORTH_AI_POLL_INTERVAL": "0.001",
        }), patch.object(ai_bridge, "_api_get", side_effect=api_get), \
                patch.object(ai_bridge, "_request", side_effect=request):
            events = list(ai_bridge._stream(
                "sess-1", {"type": "agent.session.input.message", "input": []},
                stream=False,
            ))

        post_index = next(i for i, entry in enumerate(order) if entry[0] == "POST")
        self.assertEqual(order[post_index][1], "/sessions/sess-1/events")
        self.assertFalse(any("events?stream=true" in str(entry) for entry in order))
        self.assertIn({"type": "agent.session.turn.output_text.delta", "delta": "A short joke."}, events)
        self.assertIn({"type": "agent.session.turn.output_text.done", "text": "A short joke."}, events)
        self.assertEqual(events[-1]["type"], "agent.session.turn.completed")
        self.assertTrue(response.closed)

    def test_poll_timeout_is_explicit_after_prompt_was_accepted(self):
        order = []
        response = FakeResponse()

        def api_get(path, **kwargs):
            order.append(("GET", path))
            if "/turns" in path:
                return {"data": [{"id": "turn-new", "status": "in_progress"}]}
            if path.endswith("/sessions/sess-timeout"):
                return {"id": "sess-timeout", "status": "in_progress", "required_actions": []}
            self.fail(f"Unexpected API GET: {path}")

        def request(method, path, payload=None, **kwargs):
            order.append((method, path, payload))
            return response

        with patch.dict(os.environ, {
                "PEFORTH_AI_REQUEST_TIMEOUT": "1",
                "PEFORTH_AI_TURN_TIMEOUT": "0.02",
                "PEFORTH_AI_POLL_INTERVAL": "0.001",
        }), patch.object(ai_bridge, "_api_get", side_effect=api_get), \
                patch.object(ai_bridge, "_request", side_effect=request):
            with self.assertRaisesRegex(RuntimeError, "timed out.*prompt was accepted"):
                list(ai_bridge._stream(
                    "sess-timeout", {"type": "agent.session.input.message", "input": []},
                    stream=False,
                ))

        self.assertTrue(any(entry[0] == "POST" for entry in order))
        self.assertTrue(response.closed)

    def test_polling_surfaces_required_action_once_and_then_final_answer(self):
        states = [
            {"id": "sess-action", "status": "requires_action", "required_actions": [
                {"type": "function_call", "call_id": "call-1", "turn_id": "turn-1"},
            ]},
            {"id": "sess-action", "status": "requires_action", "required_actions": [
                {"type": "function_call", "call_id": "call-1", "turn_id": "turn-1"},
            ]},
            {"id": "sess-action", "status": "idle", "required_actions": []},
        ]
        turns = [
            {"data": [{"id": "turn-1", "status": "waiting"}]},
            {"data": [{"id": "turn-1", "status": "waiting"}]},
            {"data": [{"id": "turn-1", "status": "completed"}]},
        ]

        def api_get(path, **kwargs):
            if path.endswith("/sessions/sess-action"):
                return states.pop(0)
            if "/turns" in path:
                return turns.pop(0)
            if "/items" in path:
                return {
                    "data": [{
                        "type": "message", "role": "assistant", "phase": "final_answer",
                        "turn_id": "turn-1",
                        "content": [{"type": "output_text", "text": "Done."}],
                    }],
                    "has_more": False,
                }
            self.fail(f"Unexpected API GET: {path}")

        with patch.dict(os.environ, {
                "PEFORTH_AI_TURN_TIMEOUT": "1",
                "PEFORTH_AI_POLL_INTERVAL": "0.001",
        }), patch.object(ai_bridge, "_api_get", side_effect=api_get), \
                patch.object(ai_bridge.time, "sleep"):
            events = ai_bridge._poll_session_events("sess-action")
            first = next(events)
            remaining = list(events)

        self.assertEqual(first["type"], "agent.session.requires_action")
        self.assertFalse(any(event["type"] == "agent.session.requires_action" for event in remaining))
        self.assertEqual(remaining[0]["delta"], "Done.")
        self.assertEqual(remaining[-1]["type"], "agent.session.turn.completed")

    def test_http_timeout_has_operation_and_configured_duration(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}), \
                patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge.urllib.request, "urlopen", side_effect=TimeoutError("timed out")):
            with self.assertRaisesRegex(RuntimeError, r"timed out after 0\.01s.*GET /sessions/sess-1"):
                ai_bridge._request("GET", "/sessions/sess-1", timeout=0.01)

    def test_sse_read_timeout_closes_response_and_has_clear_message(self):
        class TimeoutResponse(FakeResponse):
            def __iter__(self):
                raise TimeoutError("read timed out")

        response = TimeoutResponse()
        with self.assertRaisesRegex(RuntimeError, "SSE stream timed out"):
            list(ai_bridge._event_stream(response, timeout=0.01))
        self.assertTrue(response.closed)

    def test_one_shot_deadline_covers_create_poll_and_every_saved_item_page(self):
        deadline = ai_bridge._OneShotDeadline(timeout=5)
        diagnostic = {"_one_shot_deadline": deadline}
        response = FakeResponse(b'{"id":"sess-budget","status":"in_progress"}')
        pages = []

        def api_get(path, **kwargs):
            pages.append((path, kwargs.get("deadline")))
            if path.endswith("/sessions/sess-budget"):
                return {"id": "sess-budget", "status": "idle", "required_actions": []}
            if "/turns" in path:
                return {"data": [{"id": "turn-budget", "status": "completed"}]}
            if "/items" in path and len([p for p in pages if "/items" in p[0]]) == 1:
                return {"data": [{"id": "item-1"}], "has_more": True, "last_id": "item-1"}
            if "/items" in path:
                return {"data": [{
                    "id": "item-2", "type": "message", "role": "assistant",
                    "phase": "final_answer", "turn_id": "turn-budget",
                    "content": [{"type": "output_text", "text": "Done."}],
                }], "has_more": False, "last_id": "item-2"}
            self.fail(f"Unexpected API GET: {path}")

        with patch.object(ai_bridge, "_request", return_value=response) as request, \
                patch.object(ai_bridge, "_api_get", side_effect=api_get):
            events = list(ai_bridge._create_session(
                {"input": "prompt"}, diagnostic=diagnostic, stream=False
            ))

        self.assertTrue(deadline.prompt_accepted)
        self.assertIs(request.call_args.kwargs["deadline"], deadline)
        self.assertTrue(request.call_args.kwargs["prompt_submission"])
        self.assertEqual([p[1] for p in pages], [deadline] * len(pages))
        self.assertEqual(events[-1]["type"], "agent.session.turn.completed")
        self.assertEqual(events[-2], {
            "type": "agent.session.turn.output_text.done", "text": "Done."
        })

    def test_one_shot_caps_request_and_each_body_read_to_remaining_budget(self):
        class FakeSocket:
            def __init__(self):
                self.timeouts = []

            def settimeout(self, value):
                self.timeouts.append(value)

        class FakeResponse:
            status = 200
            headers = {}

            def __init__(self):
                self.closed = False
                self.sock = FakeSocket()
                self.fp = type("FP", (), {"raw": type("Raw", (), {"_sock": self.sock})()})()
                self.parts = [b"a", b"b", b""]

            def read1(self, _size):
                import time
                time.sleep(0.02)
                return self.parts.pop(0)

            def close(self):
                self.closed = True

        deadline = ai_bridge._OneShotDeadline(timeout=5)
        deadline.deadline = ai_bridge.time.monotonic() + 0.3
        response = FakeResponse()
        with patch.dict(os.environ, {
                "OPENAI_API_KEY": "test-key",
                "PEFORTH_AI_REQUEST_TIMEOUT": "5",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge.urllib.request, "urlopen", return_value=response) as urlopen:
            logged = ai_bridge._request(
                "GET", "/bounded", diagnostic={"_one_shot_deadline": deadline}
            )
            self.assertEqual(logged.read(), b"ab")
            logged.close()

        self.assertGreater(urlopen.call_args.kwargs["timeout"], 0)
        self.assertLessEqual(urlopen.call_args.kwargs["timeout"], 0.3)
        self.assertEqual(len(response.sock.timeouts), 3)
        self.assertTrue(all(0 < value <= 0.3 for value in response.sock.timeouts))
        self.assertGreater(response.sock.timeouts[0], response.sock.timeouts[-1])

    def test_timed_out_one_shot_post_reports_uncertainty_without_retry(self):
        deadline = ai_bridge._OneShotDeadline(timeout=5)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}), \
                patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge.urllib.request, "urlopen",
                             side_effect=TimeoutError("simulated timeout")) as urlopen:
            with self.assertRaisesRegex(RuntimeError, "outcome may be unknown"):
                ai_bridge._request(
                    "POST", "/sessions", {"input": "prompt"},
                    diagnostic={"_one_shot_deadline": deadline},
                    prompt_submission=True,
                )
        urlopen.assert_called_once()
        self.assertTrue(deadline.prompt_submission_started)
        self.assertFalse(deadline.prompt_accepted)

    def test_one_shot_post_body_timeout_reports_uncertain_acceptance(self):
        class DelayedResponse(FakeResponse):
            def read1(self, _size):
                import time
                time.sleep(0.05)
                return b"{}"

        deadline = ai_bridge._OneShotDeadline(timeout=1)
        deadline.deadline = ai_bridge.time.monotonic() + 0.02
        response = DelayedResponse()
        with patch.dict(os.environ, {
                "OPENAI_API_KEY": "test-key", "PEFORTH_AI_REQUEST_TIMEOUT": "5",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge.urllib.request, "urlopen", return_value=response) as urlopen:
            with self.assertRaisesRegex(RuntimeError, "prompt submission outcome is unknown"):
                with ai_bridge._request(
                        "POST", "/sessions", {"input": "prompt"},
                        diagnostic={"_one_shot_deadline": deadline},
                        prompt_submission=True) as logged:
                    logged.read()
        urlopen.assert_called_once()
        self.assertTrue(response.closed)
        self.assertTrue(deadline.prompt_submission_started)
        self.assertFalse(deadline.prompt_accepted)

    def test_wait_for_current_actions_retries_transitional_status(self):
        action = {"call_id": "call-ready", "name": "peforth_search_words"}
        with patch.object(ai_bridge, "_current_actions", side_effect=[
                ("in_progress", []), ("requires_action", [action])]) as current, \
                patch.object(ai_bridge.time, "sleep") as sleep, \
                patch.object(ai_bridge, "_poll_interval", return_value=0.01):
            status, actions = ai_bridge._wait_for_current_actions("sess-transition")

        self.assertEqual(status, "requires_action")
        self.assertEqual(actions, [action])
        self.assertEqual(current.call_count, 2)
        sleep.assert_called_once_with(0.01)

    def test_wait_for_current_actions_stops_after_bounded_attempts(self):
        with patch.object(ai_bridge, "_current_actions", return_value=("in_progress", [])) as current, \
                patch.object(ai_bridge.time, "sleep"), \
                patch.object(ai_bridge, "_poll_interval", return_value=0.01):
            status, actions = ai_bridge._wait_for_current_actions("sess-still-running")

        self.assertEqual(status, "in_progress")
        self.assertEqual(actions, [])
        self.assertEqual(current.call_count, 3)

    def test_ai_defers_required_action_event_when_session_is_still_in_progress(self):
        with patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"}):
            vm = repl.create_vm()

        def fake_create(_payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess-transition"}}
            yield {"type": "agent.session.requires_action", "session": {"status": "requires_action"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "Done."}
            yield {"type": "agent.session.turn.output_text.done", "text": "Done."}
            yield {"type": "agent.session.turn.completed"}

        with patch.dict(os.environ, {
                "PEFORTH_AI_LOG_MODE": "disabled", "OPENAI_API_KEY": "test-key",
                "PEFORTH_AI_POLL_INTERVAL": "0.001",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(ai_bridge, "_current_actions", return_value=("in_progress", [])) as current, \
                patch.object(ai_bridge.time, "sleep"), \
                contextlib.redirect_stdout(io.StringIO()):
            vm.push("handle a stale action event")
            vm.push(False)
            task = vm.dictate("(ai)")

        self.assertEqual(task.status, "done")
        self.assertEqual(current.call_count, 3)

    def test_reconcile_stream_turn_retries_until_terminal_status(self):
        with patch.object(ai_bridge, "_latest_turn", side_effect=[
                {"id": "turn-check", "status": "in_progress"},
                {"id": "turn-check", "status": "completed"}]) as latest, \
                patch.object(ai_bridge, "_session_turn_output_text", return_value="Saved answer.") as output, \
                patch.object(ai_bridge.time, "sleep") as sleep, \
                patch.object(ai_bridge, "_poll_interval", return_value=0.01):
            status, text = ai_bridge._reconcile_stream_turn("sess-check", "turn-check")

        self.assertEqual(status, "completed")
        self.assertEqual(text, "Saved answer.")
        self.assertEqual(latest.call_count, 2)
        output.assert_called_once()
        sleep.assert_called_once_with(0.01)

    def test_tool_result_then_in_progress_to_idle_reconciles_completed_turn(self):
        with patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"}):
            vm = repl.create_vm()
        action = {
            "type": "function_call", "turn_id": "turn-exact", "call_id": "call-search",
            "name": "peforth_search_words", "arguments": {"query": "run_pwsh"},
        }

        def fake_create(_payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess-exact"}}
            yield {"type": "agent.session.turn.created", "turn": {"id": "turn-exact"}}
            yield {"type": "agent.session.requires_action", "session": {"status": "requires_action"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "Brightness set to 50%."}
            yield {"type": "agent.session.turn.output_text.done", "text": "Brightness set to 50%."}
            yield {"type": "agent.session.requires_action", "session": {"status": "idle"}}

        with patch.dict(os.environ, {
                "PEFORTH_AI_LOG_MODE": "disabled", "OPENAI_API_KEY": "test-key",
                "PEFORTH_AI_POLL_INTERVAL": "0.001",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(ai_bridge, "_current_actions", side_effect=[
                    ("requires_action", [action]), ("in_progress", []),
                    ("in_progress", []), ("idle", []),
                ]), patch.object(ai_bridge, "_reconcile_stream_turn", return_value=("completed", "Brightness set to 50%.") ) as reconcile, \
                patch.object(ai_bridge, "_tool_result") as tool_result, \
                patch.object(ai_bridge.time, "sleep"), \
                contextlib.redirect_stdout(io.StringIO()):
            vm.push("set brightness")
            vm.push(False)
            task = vm.dictate("(ai)")

        self.assertEqual(task.status, "done")
        self.assertEqual(vm.pop(), "Brightness set to 50%.")
        tool_result.assert_called_once()
        reconcile.assert_called_once()

    def test_idle_required_action_is_reconciled_against_completed_turn(self):
        with patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"}):
            vm = repl.create_vm()

        def fake_create(_payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess-idle"}}
            yield {"type": "agent.session.turn.created", "turn": {"id": "turn-done"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "Done."}
            yield {"type": "agent.session.turn.output_text.done", "text": "Done."}
            yield {"type": "agent.session.requires_action", "session": {"status": "idle"}}

        with patch.dict(os.environ, {
                "PEFORTH_AI_LOG_MODE": "disabled", "OPENAI_API_KEY": "test-key",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(ai_bridge, "_current_actions", return_value=("idle", [])), \
                patch.object(ai_bridge, "_reconcile_stream_turn", return_value=("completed", "Done.")) as reconcile, \
                contextlib.redirect_stdout(io.StringIO()):
            vm.push("reconcile a stale idle action event")
            vm.push(False)
            task = vm.dictate("(ai)")

        self.assertEqual(task.status, "done")
        self.assertEqual(vm.pop(), "Done.")
        reconcile.assert_called_once_with(
            "sess-idle", "turn-done", diagnostic=reconcile.call_args.kwargs["diagnostic"]
        )

    def test_idle_action_event_defers_until_turn_completed_event(self):
        with patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"}):
            vm = repl.create_vm()

        def fake_create(_payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess-wait"}}
            yield {"type": "agent.session.turn.created", "turn": {"id": "turn-wait"}}
            yield {"type": "agent.session.requires_action", "session": {"status": "idle"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "Done."}
            yield {"type": "agent.session.turn.completed", "turn_id": "turn-wait"}

        with patch.dict(os.environ, {
                "PEFORTH_AI_LOG_MODE": "disabled", "OPENAI_API_KEY": "test-key",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(ai_bridge, "_current_actions", return_value=("idle", [])), \
                patch.object(ai_bridge, "_reconcile_stream_turn", return_value=("in_progress", None)) as reconcile, \
                contextlib.redirect_stdout(io.StringIO()):
            vm.push("wait for authoritative turn completion")
            vm.push(False)
            task = vm.dictate("(ai)")

        self.assertEqual(task.status, "done")
        self.assertEqual(vm.pop(), "Done.")
        reconcile.assert_called_once()

    def test_clean_sse_end_reconciles_completed_remote_turn(self):
        with patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"}):
            vm = repl.create_vm()

        def fake_create(_payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess-end"}}
            yield {"type": "agent.session.turn.created", "turn": {"id": "turn-end"}}
            yield {"type": "agent.session.turn.output_text.done", "text": ""}

        with patch.dict(os.environ, {
                "PEFORTH_AI_LOG_MODE": "disabled", "OPENAI_API_KEY": "test-key",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(ai_bridge, "_reconcile_stream_turn", return_value=("completed", "Recovered answer.")) as reconcile, \
                contextlib.redirect_stdout(io.StringIO()):
            vm.push("recover final answer from completed turn")
            vm.push(False)
            task = vm.dictate("(ai)")

        self.assertEqual(task.status, "done")
        self.assertEqual(vm.pop(), "Recovered answer.")
        reconcile.assert_called_once()

    def test_sse_timeout_recovers_completed_turn_from_saved_output(self):
        with patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"}):
            vm = repl.create_vm()

        def fake_create(_payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess-timeout"}}
            yield {"type": "agent.session.turn.created", "turn": {"id": "turn-timeout"}}
            raise RuntimeError("Agents API SSE stream timed out after 1s without data.")

        with patch.dict(os.environ, {
                "PEFORTH_AI_LOG_MODE": "disabled", "OPENAI_API_KEY": "test-key",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(ai_bridge, "_reconcile_stream_turn", return_value=("completed", "Recovered answer.")) as reconcile, \
                contextlib.redirect_stdout(io.StringIO()):
            vm.push("recover a completed turn after an SSE timeout")
            vm.push(False)
            task = vm.dictate("(ai)")

        self.assertEqual(task.status, "done")
        self.assertEqual(vm.pop(), "Recovered answer.")
        reconcile.assert_called_once()

    def test_one_shot_deadline_pauses_only_during_manual_approval(self):
        with patch.dict(os.environ, {"PEFORTH_AI_LOG_MODE": "disabled"}):
            vm = repl.create_vm()
        vm.host["ai_transport_stream_once"] = False
        action = {
            "type": "function_call", "turn_id": "turn-approval", "call_id": "call-approval",
            "name": "peforth_run_forth",
            "arguments": {"source": "42 .", "purpose": "print a value"},
        }
        captured = {}

        def fake_create(_payload, *, diagnostic=None, stream=True):
            captured["diagnostic"] = diagnostic
            yield {"type": "agent.session.created", "session": {"id": "sess-approval"}}
            yield {"type": "agent.session.requires_action", "session": {"status": "requires_action"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "Done"}
            yield {"type": "agent.session.turn.output_text.done", "text": "Done"}
            yield {"type": "agent.session.turn.completed"}

        with patch.dict(os.environ, {
                "PEFORTH_AI_LOG_MODE": "disabled", "OPENAI_API_KEY": "test-key",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(ai_bridge, "_current_actions", side_effect=[
                    ("requires_action", [action]), ("requires_action", [action]),
                ]), patch.object(ai_bridge, "_tool_result"), \
                contextlib.redirect_stdout(io.StringIO()):
            vm.push("Run a local proposal")
            vm.push(False)
            task = vm.dictate("(ai)")
            self.assertEqual(task.status, "paused")
            deadline = captured["diagnostic"]["_one_shot_deadline"]
            self.assertIsNotNone(deadline.paused_at)
            paused_remaining = deadline.remaining()
            import time
            time.sleep(0.03)
            self.assertAlmostEqual(deadline.remaining(), paused_remaining, delta=0.005)
            vm.host.pop("ai_pending_approval")
            vm.host["ai_approval_result"] = True
            task.resume()
            self.assertEqual(task.status, "done")
            self.assertIsNone(deadline.paused_at)

    def test_forth_ai_consumes_transport_flag_and_still_prints_final_text(self):
        vm = repl.create_vm()
        vm.host["ai_active_session_id"] = "sess-1"
        vm.host["ai_transport_stream_once"] = False
        events = [
            {"type": "agent.session.turn.output_text.delta", "delta": "A short joke."},
            {"type": "agent.session.turn.output_text.done", "text": "A short joke."},
            {"type": "agent.session.turn.completed"},
        ]
        with patch.object(ai_bridge, "_stream", return_value=iter(events)) as stream, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            vm.push("tell me a joke")
            vm.push(True)
            task = vm.execute(vm.tick("(ai)"))

        self.assertEqual(task.status, "done")
        self.assertFalse(stream.call_args.kwargs["stream"])
        self.assertNotIn("ai_transport_stream_once", vm.host)
        self.assertIn("A short joke.", output.getvalue())

    def test_streaming_followup_submits_post_only_after_sse_headers_open(self):
        import time

        request_order = []
        newline = bytes((10,))
        post_response = FakeResponse(b"{}")

        class StreamResponse(FakeResponse):
            status = 200

            def __iter__(self):
                return iter([
                    b'data: {"type":"agent.session.turn.output_text.delta","delta":"Hi"}' + newline,
                    newline,
                    b'data: {"type":"agent.session.turn.completed"}' + newline,
                    newline,
                ])

        sse_response = StreamResponse()

        def fake_urlopen(request, timeout=None):
            if request.get_method() == "GET" and "events?stream=true" in request.full_url:
                time.sleep(0.02)
                request_order.append("GET-open")
                return sse_response
            if request.get_method() == "POST" and request.full_url.endswith("/events"):
                request_order.append("POST-prompt")
                return post_response
            self.fail(f"Unexpected request: {request.get_method()} {request.full_url}")

        with patch.dict(os.environ, {
                "OPENAI_API_KEY": "test-key",
                "PEFORTH_AI_SSE_OPEN_GRACE": "0.5",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge.urllib.request, "urlopen", side_effect=fake_urlopen):
            events = list(ai_bridge._stream(
                "sess-buffered",
                {"type": "agent.session.input.message", "input": []},
                stream=True,
            ))

        self.assertEqual(request_order, ["GET-open", "POST-prompt"])
        self.assertEqual(events[0], {"type": "agent.session.turn.output_text.delta", "delta": "Hi"})
        self.assertEqual(events[-1]["type"], "agent.session.turn.completed")
        self.assertTrue(post_response.closed)
        self.assertTrue(sse_response.closed)

    def test_sse_handshake_timeout_falls_back_to_single_post_then_poll(self):
        order = []
        post_response = FakeResponse(b"{}")
        events = [{"type": "agent.session.turn.completed", "turn_id": "turn-new"}]

        def fake_request(method, path, payload=None, **kwargs):
            order.append((method, path))
            if method == "GET":
                raise RuntimeError("Agents API request timed out after 0.02s: GET " + path)
            return post_response

        with patch.dict(os.environ, {
                "OPENAI_API_KEY": "test-key",
                "PEFORTH_AI_REQUEST_TIMEOUT": "1",
                "PEFORTH_AI_TURN_TIMEOUT": "1",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_request", side_effect=fake_request), \
                patch.object(ai_bridge, "_latest_turn", return_value={"id": "turn-old"}) as latest, \
                patch.object(ai_bridge, "_poll_session_events", return_value=iter(events)) as poll:
            result = list(ai_bridge._stream(
                "sess-fallback", {"type": "agent.session.input.message", "input": []},
                stream=True,
            ))

        self.assertEqual([method for method, _ in order], ["GET", "POST"])
        self.assertEqual(order[-1][1], "/sessions/sess-fallback/events")
        latest.assert_called_once()
        poll.assert_called_once()
        poll_args, poll_kwargs = poll.call_args
        self.assertEqual(poll_args[:2], ("sess-fallback", "turn-old"))
        self.assertEqual(poll_kwargs["deadline"], latest.call_args.kwargs["deadline"])
        self.assertEqual(poll_kwargs["diagnostic"]["session_id"], "sess-fallback")
        self.assertEqual(result, events)
        self.assertTrue(post_response.closed)

    def test_sse_http_error_does_not_fallback_or_submit_prompt(self):
        order = []

        def fake_request(method, path, payload=None, **kwargs):
            order.append(method)
            raise RuntimeError("Agents API HTTP 500: internal_error")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}), \
                patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_request", side_effect=fake_request), \
                patch.object(ai_bridge, "_latest_turn") as latest:
            with self.assertRaisesRegex(RuntimeError, "Agents API HTTP 500"):
                list(ai_bridge._stream(
                    "sess-http-error", {"type": "agent.session.input.message", "input": []},
                    stream=True,
                ))

        self.assertEqual(order, ["GET"])
        latest.assert_not_called()

    def test_stream_response_timeout_is_restored_after_open_handshake(self):
        class TimeoutSocket:
            value = None

            def settimeout(self, value):
                self.value = value

        response = FakeResponse()
        response.status = 200
        response._sock = TimeoutSocket()
        with patch.dict(os.environ, {
                "OPENAI_API_KEY": "test-key", "PEFORTH_AI_STREAM_TIMEOUT": "12",
        }), patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge.urllib.request, "urlopen", return_value=response):
            with ai_bridge._request(
                    "GET", "/sessions/sess-timeout/events?stream=true",
                    stream=True, timeout=0.02) as opened:
                self.assertEqual(opened.status, 200)

        self.assertEqual(response._sock.value, 12.0)

    def test_reset_after_sse_open_does_not_resubmit_prompt(self):
        request_order = []
        post_response = FakeResponse(b"{}")
        newline = bytes((10,))

        class ResetResponse(FakeResponse):
            status = 200

            def __iter__(self):
                raise ConnectionResetError("peer reset")
                yield newline

        sse_response = ResetResponse()

        def fake_urlopen(request, timeout=None):
            if request.get_method() == "GET" and "events?stream=true" in request.full_url:
                request_order.append("GET-open")
                return sse_response
            if request.get_method() == "POST" and request.full_url.endswith("/events"):
                request_order.append("POST-prompt")
                return post_response
            self.fail(f"Unexpected request: {request.get_method()} {request.full_url}")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}), \
                patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge.urllib.request, "urlopen", side_effect=fake_urlopen):
            with self.assertRaisesRegex(ConnectionResetError, "peer reset"):
                list(ai_bridge._stream(
                    "sess-reset", {"type": "agent.session.input.message", "input": []},
                    stream=True,
                ))

        self.assertEqual(request_order, ["GET-open", "POST-prompt"])
        self.assertTrue(post_response.closed)
        self.assertTrue(sse_response.closed)

    def test_corrupted_session_http_500_includes_actionable_recovery_hint(self):
        sse_response = FakeResponse()

        def fake_request(method, path, payload=None, **kwargs):
            if method == "GET":
                return sse_response
            raise RuntimeError("Agents API HTTP 500: {\"error\":{\"code\":\"internal_error\"}}")

        with patch.object(ai_bridge, "_request", side_effect=fake_request):
            with self.assertRaisesRegex(
                    RuntimeError,
                    r"Agents API HTTP 500[\s\S]*sess-corrupt[\s\S]*ai-use[\s\S]*ai-cleanup"):
                list(ai_bridge._stream(
                    "sess-corrupt",
                    {"type": "agent.session.input.message", "input": []},
                    stream=True,
                ))
        self.assertTrue(sse_response.closed)


class DotenvEmptyValueTests(unittest.TestCase):
    def test_empty_process_key_is_filled_from_dotenv(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("OPENAI_API_KEY=key-from-dotenv\n", encoding="utf-8")
            with patch.dict(os.environ, {"PEFORTH_CONFIG_DIR": tmp, "OPENAI_API_KEY": ""}):
                ai_bridge.load_dotenv()
                self.assertEqual(os.environ["OPENAI_API_KEY"], "key-from-dotenv")

    def test_nonempty_process_key_is_not_overridden_by_dotenv(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("OPENAI_API_KEY=key-from-dotenv\n", encoding="utf-8")
            with patch.dict(os.environ, {"PEFORTH_CONFIG_DIR": tmp, "OPENAI_API_KEY": "key-from-process"}):
                ai_bridge.load_dotenv()
                self.assertEqual(os.environ["OPENAI_API_KEY"], "key-from-process")


if __name__ == "__main__":
    unittest.main()
