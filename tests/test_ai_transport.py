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


if __name__ == "__main__":
    unittest.main()
