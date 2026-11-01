from __future__ import annotations

import contextlib
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from peforth import ai_bridge, repl as _f_mod
from peforth.session_store import (
    SCHEMA_VERSION,
    SessionStore,
    build_session_description,
    extract_first_sentence,
    extract_first_user_message_text,
    format_description_time,
    is_complete_description,
)


class SessionDescriptionRuleTests(unittest.TestCase):
    def test_format_description_time_uses_local_timezone_static_text(self):
        tz_plus_8 = timezone(timedelta(hours=8))
        ts = int(datetime(2026, 4, 19, 6, 58, 26, tzinfo=tz_plus_8).timestamp())
        self.assertEqual(
            format_description_time(ts, tz=tz_plus_8),
            "2026-04-19 06:58:26",
        )

    def test_extract_first_sentence_breaks_on_newline_and_chinese_or_english_punctuation(self):
        self.assertEqual(
            extract_first_sentence("第一行內容\n第二行內容。"),
            "第一行內容",
        )
        self.assertEqual(
            extract_first_sentence("請幫我檢查 ai.f 的設定。接著跑測試！"),
            "請幫我檢查 ai.f 的設定",
        )
        self.assertEqual(
            extract_first_sentence("為什麼 3.14 會出現錯誤？請看第 2 行"),
            "為什麼 3.14 會出現錯誤",
        )
        self.assertEqual(
            extract_first_sentence("Check version 3.14 in ai.f. Then run tests!"),
            "Check version 3.14 in ai.f",
        )
        self.assertEqual(
            extract_first_sentence("What is inside peforth/ai_bridge.py? Let me know."),
            "What is inside peforth/ai_bridge.py",
        )

    def test_extract_first_sentence_truncates_at_80_unicode_chars_with_ellipsis(self):
        long_clause = "甲" * 80
        self.assertEqual(extract_first_sentence(long_clause + "。後續"), long_clause)

        over_80 = "乙" * 81
        self.assertEqual(
            extract_first_sentence(over_80 + "。後續"),
            ("乙" * 80) + "...",
        )

    def test_extract_first_user_message_skips_non_user_items(self):
        items = [
            {"id": "item_0", "type": "reasoning", "summary": [{"text": "thinking"}]},
            {
                "id": "item_1",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Assistant greeting."}],
            },
            {
                "id": "item_2",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "使用者的第一句話。第二句話。"}],
            },
            {
                "id": "item_3",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "第二則使用者訊息。"}],
            },
        ]
        self.assertEqual(
            extract_first_user_message_text(items),
            "使用者的第一句話。第二句話。",
        )

    def test_build_session_description_placeholder_and_overwrite_protection(self):
        tz_plus_8 = timezone(timedelta(hours=8))
        ts = int(datetime(2026, 4, 19, 6, 58, 26, tzinfo=tz_plus_8).timestamp())

        # No user message yet -> save only the time prefix
        placeholder = build_session_description(ts, [], existing_description=None, tz=tz_plus_8)
        self.assertEqual(placeholder, "2026-04-19 06:58:26")
        self.assertFalse(is_complete_description(placeholder))

        # Later sync brings a user message -> completes the description
        items = [
            {
                "id": "msg_1",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "請實作 AI session 本地副本。"}],
            }
        ]
        completed = build_session_description(ts, items, existing_description=placeholder, tz=tz_plus_8)
        self.assertEqual(completed, "2026-04-19 06:58:26 | 請實作 AI session 本地副本")
        self.assertTrue(is_complete_description(completed))

        # Subsequent syncs or user modifications are never overwritten
        other_items = [
            {
                "id": "msg_1",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "完全不同的訊息。"}],
            }
        ]
        self.assertEqual(
            build_session_description(ts, other_items, existing_description=completed, tz=tz_plus_8),
            completed,
        )
        custom_desc = "手動標記的重要重點 Session"
        self.assertEqual(
            build_session_description(ts, other_items, existing_description=custom_desc, tz=tz_plus_8),
            custom_desc,
        )


class SessionStoreAndSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        self.env_patch = patch.dict(
            "os.environ",
            {
                "PEFORTH_CONFIG_DIR": str(self.config_dir),
                "PEFORTH_AI_LOG_MODE": "disabled",
            },
        )
        self.env_patch.start()
        self.vm = _f_mod.create_vm()

    def tearDown(self):
        self.env_patch.stop()
        self.temp_dir.cleanup()

    def test_schema_creation_and_role_null_for_non_message_items(self):
        db_path = ai_bridge._session_db_path()
        self.assertEqual(db_path, self.config_dir / "sessions" / "sessions.sqlite3")
        with SessionStore(db_path) as store:
            version = store.connection.execute("PRAGMA user_version").fetchone()[0]
            self.assertEqual(version, SCHEMA_VERSION)
            items = [
                {
                    "id": "item_msg_1",
                    "turn_id": "turn_1",
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Hello SQLite mirror!"}],
                },
                {
                    "id": "item_call_1",
                    "turn_id": "turn_1",
                    "type": "function_call",
                    "role": "ignored_for_non_message",
                    "name": "forth_eval",
                    "arguments": "{\"code\": \"words\"}",
                },
            ]
            store.sync_session(
                {
                    "id": "sess_schema_1",
                    "created_at": 1700000000,
                    "last_active_at": 1700000100,
                    "status": "idle",
                    "agent": {"model": "gpt-6-luna"},
                },
                items,
            )
            rows = store.connection.execute(
                "SELECT id, seq, turn_id, type, role, raw_json FROM session_items "
                "WHERE session_id = ? ORDER BY seq ASC",
                ("sess_schema_1",),
            ).fetchall()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["id"], "item_msg_1")
            self.assertEqual(rows[0]["seq"], 0)
            self.assertEqual(rows[0]["role"], "user")
            self.assertEqual(rows[1]["id"], "item_call_1")
            self.assertEqual(rows[1]["seq"], 1)
            self.assertIsNone(rows[1]["role"])

    def test_differential_sync_skips_unchanged_and_marks_remote_deleted(self):
        remote_v1 = [
            {
                "id": "sess_a",
                "created_at": 1700000200,
                "last_active_at": 1700000250,
                "status": "idle",
                "agent": {"model": "gpt-6-luna"},
            },
            {
                "id": "sess_b",
                "created_at": 1700000100,
                "last_active_at": 1700000150,
                "status": "idle",
                "agent": {"model": "gpt-6-luna"},
            },
        ]
        items_by_session = {
            "sess_a": [
                {
                    "id": "a_1",
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Session A first prompt."}],
                }
            ],
            "sess_b": [
                {
                    "id": "b_1",
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Session B first prompt."}],
                }
            ],
        }

        with patch.object(ai_bridge, "_list_remote_sessions", return_value=remote_v1), \
                patch.object(ai_bridge, "_fetch_session_items", side_effect=lambda sid: items_by_session[sid]) as fetch_mock:
            stats1 = ai_bridge.sync_sessions(self.vm)
            self.assertEqual(stats1["synced"], 2)
            self.assertEqual(stats1["skipped"], 0)
            self.assertEqual(stats1["deleted"], 0)
            self.assertEqual(fetch_mock.call_count, 2)

            # Second sync with identical last_active_at makes zero item requests
            fetch_mock.reset_mock()
            stats2 = ai_bridge.sync_sessions(self.vm)
            self.assertEqual(stats2["synced"], 0)
            self.assertEqual(stats2["skipped"], 2)
            self.assertEqual(stats2["deleted"], 0)
            fetch_mock.assert_not_called()

        # Third sync: sess_a has newer last_active_at, sess_b disappeared remotely
        remote_v2 = [
            {
                "id": "sess_a",
                "created_at": 1700000200,
                "last_active_at": 1700000300,
                "status": "idle",
                "agent": {"model": "gpt-6-luna"},
            }
        ]
        items_by_session["sess_a"] = [
            {
                "id": "a_1",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Changed text should not overwrite description."}],
            },
            {
                "id": "a_2",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Second item added."}],
            },
        ]
        with patch.object(ai_bridge, "_list_remote_sessions", return_value=remote_v2), \
                patch.object(ai_bridge, "_fetch_session_items", side_effect=lambda sid: items_by_session[sid]) as fetch_mock:
            stats3 = ai_bridge.sync_sessions(self.vm)
            self.assertEqual(stats3["synced"], 1)
            self.assertEqual(stats3["skipped"], 0)
            self.assertEqual(stats3["deleted"], 1)
            fetch_mock.assert_called_once_with("sess_a")

        with ai_bridge._open_session_store() as store:
            sess_a = store.get_session("sess_a")
            sess_b = store.get_session("sess_b")
            self.assertIsNotNone(sess_a)
            self.assertIsNotNone(sess_b)
            self.assertIn("Session A first prompt", sess_a["description"])
            self.assertEqual(sess_a["remote_deleted"], 0)
            self.assertEqual(len(store.get_session_items("sess_a")), 2)
            # sess_b is marked remote_deleted = 1 but its local data and items are preserved
            self.assertEqual(sess_b["remote_deleted"], 1)
            self.assertEqual(len(store.get_session_items("sess_b")), 1)
            self.assertEqual([r["id"] for r in store.list_sessions(include_deleted=False)], ["sess_a"])
            self.assertEqual(len(store.list_sessions(include_deleted=True)), 2)

    def test_failed_session_sync_is_atomic_and_retried_next_time(self):
        remote = [
            {"id": "sess_ok", "created_at": 1700000200, "last_active_at": 1700000250},
            {"id": "sess_fail", "created_at": 1700000100, "last_active_at": 1700000150},
        ]

        def flaky_fetch(sid):
            if sid == "sess_fail":
                raise RuntimeError("Simulated network failure")
            return [
                {
                    "id": "ok_1",
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "OK session."}],
                }
            ]

        with patch.object(ai_bridge, "_list_remote_sessions", return_value=remote), \
                patch.object(ai_bridge, "_fetch_session_items", side_effect=flaky_fetch):
            with self.assertRaises(RuntimeError):
                ai_bridge.sync_sessions(self.vm)

        with ai_bridge._open_session_store() as store:
            self.assertIsNotNone(store.get_session("sess_ok"))
            self.assertIsNone(store.get_session("sess_fail"))

        # Next sync succeeds and only needs to fetch sess_fail
        with patch.object(ai_bridge, "_list_remote_sessions", return_value=remote), \
                patch.object(
                    ai_bridge,
                    "_fetch_session_items",
                    return_value=[
                        {
                            "id": "fail_recovered_1",
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "Recovered session."}],
                        }
                    ],
                ) as fetch_mock:
            stats = ai_bridge.sync_sessions(self.vm)
            self.assertEqual(stats["synced"], 1)
            self.assertEqual(stats["skipped"], 1)
            fetch_mock.assert_called_once_with("sess_fail")

    def test_forth_words_ai_sync_ai_export_session_and_ai_search(self):
        remote = [
            {
                "id": "sess_export_12345678",
                "created_at": 1700000500,
                "last_active_at": 1700000550,
                "status": "idle",
                "agent": {"model": "gpt-6-luna"},
            }
        ]
        raw_items = [
            {
                "id": "item_u1",
                "turn_id": "turn_1",
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "請備份這個特別的對話紀錄。還有更多細節。"}],
            },
            {
                "id": "item_a1",
                "turn_id": "turn_1",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "好的，已經同步到本地 SQLite 資料庫。"}],
            },
        ]

        with patch.object(ai_bridge, "_list_remote_sessions", return_value=remote), \
                patch.object(ai_bridge, "_fetch_session_items", return_value=raw_items):
            sync_out = io.StringIO()
            with contextlib.redirect_stdout(sync_out):
                self.vm.dictate("ai-sync")
            self.assertIn("Synced AI sessions: 1 updated, 0 unchanged", sync_out.getvalue())

        export_file = self.config_dir / "exported-session.json"
        export_out = io.StringIO()
        with contextlib.redirect_stdout(export_out):
            self.vm.push(1)
            self.vm.push(str(export_file))
            self.vm.execute(self.vm.tick("ai-export-session"))
        self.assertTrue(export_file.is_file())
        exported_data = json.loads(export_file.read_text(encoding="utf-8"))
        self.assertEqual(exported_data, raw_items)

        search_out = io.StringIO()
        with contextlib.redirect_stdout(search_out):
            self.vm.dictate("ai-search 特別的對話紀錄")
        rendered_search = search_out.getvalue()
        self.assertIn("Matched 1 local session(s)", rendered_search)
        self.assertIn("sess_export_12345678", rendered_search)
        self.assertIn("請備份這個特別的對話紀錄", rendered_search)

    def test_readonly_session_search_does_not_require_approval_and_reconcile_prints_final_answer(self):
        with ai_bridge._open_session_store() as store:
            store.sync_session(
                {
                    "id": "sess_hist_1",
                    "created_at": 1700000100,
                    "last_active_at": 1700000150,
                    "status": "idle",
                    "agent": {"model": "gpt-6-luna"},
                },
                [
                    {
                        "id": "u1",
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "--> and ==> 差在哪裡？"}],
                    },
                    {
                        "id": "a1",
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "==> 會先多印一個空白行。"}],
                    },
                ],
            )

        self.assertTrue(ai_bridge._is_readonly_session_search_forth('s" --> ==>" ai-search'))
        self.assertTrue(
            ai_bridge._is_readonly_session_search_forth('s" 亮度" ai-search\ns" 螢幕" ai-search')
        )
        self.assertTrue(ai_bridge._is_readonly_session_search_forth("ai-search 亮度"))
        self.assertFalse(ai_bridge._is_readonly_session_search_forth('s" --> ==>" ai-search 1 ai-cleanup'))
        self.assertFalse(ai_bridge._is_readonly_session_search_forth("42 ."))

        # Simulate a turn where:
        # 1. Pre-tool commentary streams first ("我先查一下以前的紀錄。")
        # 2. AI invokes peforth_run_forth with 's" --> ==>" ai-search' (auto-approved without pausing)
        # 3. Turn completes and reconciles with final answer ("==> 會先多印一個空白行。")
        action = {
            "type": "function_call",
            "turn_id": "turn_reconcile_1",
            "call_id": "call_search_1",
            "name": "peforth_run_forth",
            "arguments": {
                "source": 's" --> ==>" ai-search',
                "purpose": "Recall earlier explanation from local session mirror.",
            },
        }

        def fake_create(_payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess_live_1"}}
            yield {"type": "agent.session.turn.created", "turn": {"id": "turn_reconcile_1"}}
            yield {"type": "agent.session.turn.output_text.delta", "delta": "我先查一下以前的紀錄。"}
            yield {"type": "agent.session.turn.output_text.done", "text": "我先查一下以前的紀錄。"}
            yield {"type": "agent.session.requires_action", "session": {"status": "requires_action"}}
            yield {"type": "agent.session.requires_action", "session": {"status": "idle"}}

        stdout_buf = io.StringIO()
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key", "PEFORTH_AI_POLL_INTERVAL": "0.001"}), \
                patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(
                    ai_bridge,
                    "_current_actions",
                    side_effect=[("requires_action", [action]), ("requires_action", [action]), ("idle", [])],
                ), \
                patch.object(
                    ai_bridge,
                    "_reconcile_stream_turn",
                    return_value=("completed", "你說得對，差別只有 ==> 會先多印一個空白行。"),
                ), \
                patch.object(ai_bridge, "_tool_result") as tool_result_mock, \
                contextlib.redirect_stdout(stdout_buf):
            self.vm.push("--> and ==> 差在哪裡?")
            self.vm.push(True)
            task = self.vm.dictate("(ai)")

        # Task must complete without pausing for approval
        self.assertEqual(task.status, "done")
        self.assertFalse(self.vm.host.get("ai_pending_approval"))
        tool_result_mock.assert_called_once()
        rendered = stdout_buf.getvalue()
        self.assertIn("我先查一下以前的紀錄。", rendered)
        self.assertIn("你說得對，差別只有 ==> 會先多印一個空白行。", rendered)

    def test_peforth_search_sessions_direct_tool_runs_without_approval(self):
        with ai_bridge._open_session_store() as store:
            store.sync_session(
                {
                    "id": "sess_direct_12345678",
                    "created_at": 1700000100,
                    "last_active_at": 1700000150,
                    "status": "idle",
                    "agent": {"model": "gpt-6-luna"},
                },
                [
                    {
                        "id": "u1",
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "調整螢幕亮度到 50%。"}],
                    },
                    {
                        "id": "a1",
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "已將螢幕亮度調到 50%。"}],
                    },
                ],
            )

        action = {
            "type": "function_call",
            "turn_id": "turn_direct_1",
            "call_id": "call_direct_1",
            "name": "peforth_search_sessions",
            "arguments": {"query": "螢幕亮度"},
        }

        def fake_create(_payload, *, diagnostic=None, stream=True):
            yield {"type": "agent.session.created", "session": {"id": "sess_live_2"}}
            yield {"type": "agent.session.turn.created", "turn": {"id": "turn_direct_1"}}
            yield {"type": "agent.session.requires_action", "session": {"status": "requires_action"}}
            yield {"type": "agent.session.turn.output_text.done", "text": "Found it."}
            yield {"type": "agent.session.turn.completed", "turn_id": "turn_direct_1"}

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}), \
                patch.object(ai_bridge, "load_dotenv"), \
                patch.object(ai_bridge, "_agent_instructions", return_value="instructions"), \
                patch.object(ai_bridge, "_create_session", side_effect=fake_create), \
                patch.object(ai_bridge, "_wait_for_current_actions", return_value=("requires_action", [action])), \
                patch.object(ai_bridge, "_tool_result") as tool_result_mock, \
                contextlib.redirect_stdout(io.StringIO()):
            self.vm.push("recall brightness")
            self.vm.push(False)
            task = self.vm.dictate("(ai)")

        self.assertEqual(task.status, "done")
        self.assertEqual(self.vm.pop(), "Found it.")
        tool_result_mock.assert_called_once()
        submitted_json = json.loads(tool_result_mock.call_args.args[3])
        self.assertEqual(len(submitted_json["sessions"]), 1)
        self.assertEqual(submitted_json["sessions"][0]["session_id"], "sess_direct_12345678")


if __name__ == "__main__":
    unittest.main()
