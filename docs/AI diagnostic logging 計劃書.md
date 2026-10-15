# peforth AI Diagnostic Logging 計劃書

## 目標

為 peforth 的 AI transport、SSE stream、tool call 與 approval flow 建立可查詢的診斷記錄，支援多個 runtime 同時執行，並能重建每次 AI request 的完整 output 與事件時序。

Windows 與 WSL 各自使用一個 SQLite database：同一 environment 的所有 runtime 共用該 environment 的 database；Windows 與 WSL 不共用 live database。

---

## 1. 名詞與儲存範圍

### 1.1 Runtime

`runtime` 指一個 peforth application process。每個 runtime 啟動時產生一個固定的 `runtime_id`，直到該 process 結束。

同一 environment 可以同時存在多個 runtime。所有 Windows runtime 寫入 Windows database；所有 WSL runtime 寫入 WSL database。

Remote Agents API session ID 不取代 `runtime_id`。一個 runtime 可能使用多個 remote session，多個 runtime 也可能使用同一個 remote session。

### 1.2 Database 位置

沿用 `PEFORTH_CONFIG_DIR`；未設定時使用各 environment 的預設 peforth config directory：

```text
Windows: %USERPROFILE%\\.peforth\\ai-diagnostics.sqlite3
WSL:     ~/.peforth/ai-diagnostics.sqlite3
```

同一 environment 的所有 runtime 寫入同一個 database。Windows database 與 WSL database 分開；跨 environment 比較時使用 read-only 查詢或複製後分析。

---

## 2. 記錄原則

1. 每次 AI turn 都保留一筆 occurrence，即使 prompt 或 output 與其他 turn 完全相同。
2. 完整文字內容以 hash 去重，同一內容只在 `contents` 保存一次。
3. Prompt、instructions、tool arguments、tool result、output 與 partial output 都保存完整內容。
4. SSE timeline 記錄事件與時間，但不保存每次累積 output 的副本。
5. Runtime 維護 output accumulator；AI turn 結束或失敗時保存當時完整 output，若中途 timeout 則保存已收到的 partial output。
6. 正常與 verbose logging 都保存完整 prompt、instructions、tool content、final output 與 partial output；兩者差異只在串流中間事件的詳細程度。
7. 每筆資料即時寫入 SQLite，不等待 runtime 結束。
8. Logging 每次寫入有明確的最大等待時間，不得無界阻塞 SSE reader 或 AI flow。
9. Logging 不得覆蓋原本的 AI、network、SSE 或 Forth error。

---

## 3. Content 去重

### 3.1 `contents` table

完整文字只保存一次；同一 `content_type` 與 hash 只建立一筆資料。

```sql
CREATE TABLE IF NOT EXISTS contents (
    content_id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_hash TEXT NOT NULL,
    content_type TEXT NOT NULL,
    content_text TEXT NOT NULL,
    content_size INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(content_type, content_hash)
);
```

`content_type` 至少支援：

```text
prompt
agent_instructions
output
partial_output
tool_arguments
tool_result
forth_source
forth_stdout
forth_stderr
```

### 3.2 去重寫入

使用 SQLite unique constraint 處理多 runtime 同時寫入相同內容：

```sql
INSERT INTO contents
    (content_hash, content_type, content_text, content_size, created_at)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(content_type, content_hash) DO NOTHING;
```

insert-or-ignore 後取得既有的 `content_id`，再由 occurrence row reference 該 ID。整個流程使用短 transaction。

### 3.3 Occurrence 與 Content 的區別

相同 prompt 只保存一份文字，但每次實際送出仍建立不同的 turn：

```text
turn A -> prompt_content_id = 12
turn B -> prompt_content_id = 12
turn C -> prompt_content_id = 12
```

三個 turn 的 runtime、remote session、時間、狀態與 output 仍可不同。

---

## 4. Database schema

### 4.1 `runtimes`

```sql
CREATE TABLE IF NOT EXISTS runtimes (
    runtime_id TEXT PRIMARY KEY,
    process_id INTEGER NOT NULL,
    parent_process_id INTEGER,
    environment TEXT NOT NULL,
    os_name TEXT NOT NULL,
    hostname TEXT,
    username TEXT,
    working_directory TEXT,
    source_path TEXT,
    runtime_path TEXT,
    runtime_version TEXT,
    git_revision TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    exit_status TEXT,
    metadata_json TEXT
);
```

`environment` 的值為 `windows` 或 `wsl`。

### 4.2 `turns`

每次 AI prompt/response 為一筆 occurrence。

```sql
CREATE TABLE IF NOT EXISTS turns (
    turn_id TEXT PRIMARY KEY,
    runtime_id TEXT NOT NULL,
    remote_session_id TEXT,
    remote_turn_id TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    prompt_content_id INTEGER,
    instructions_content_id INTEGER,
    output_content_id INTEGER,
    output_status TEXT,
    status TEXT,
    error_type TEXT,
    error_message TEXT,
    metadata_json TEXT,
    FOREIGN KEY (runtime_id) REFERENCES runtimes(runtime_id),
    FOREIGN KEY (prompt_content_id) REFERENCES contents(content_id),
    FOREIGN KEY (instructions_content_id) REFERENCES contents(content_id),
    FOREIGN KEY (output_content_id) REFERENCES contents(content_id)
);
```

`output_status` 的值為：

```text
complete
partial
empty
failed_before_output
```

`turn.status` 的值為：

```text
completed
failed
partial
cancelled
```

只有收到 `turn.completed` 且 stream 正常結束時，`turn.status` 才可為 `completed`。

### 4.3 `timeline`

記錄每個 turn 的事件；大型完整文字透過 `content_id` reference 保存，不在每個 event 重複嵌入。

```sql
CREATE TABLE IF NOT EXISTS timeline (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    runtime_id TEXT NOT NULL,
    turn_id TEXT,
    recorded_at TEXT NOT NULL,
    monotonic_ns INTEGER NOT NULL,
    sequence_no INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    session_id TEXT,
    remote_turn_id TEXT,
    call_id TEXT,
    operation TEXT,
    http_method TEXT,
    url TEXT,
    http_status INTEGER,
    local_request_id TEXT,
    provider_request_id TEXT,
    elapsed_ms REAL,
    content_id INTEGER,
    payload_json TEXT,
    error_type TEXT,
    error_message TEXT,
    FOREIGN KEY (runtime_id) REFERENCES runtimes(runtime_id),
    FOREIGN KEY (turn_id) REFERENCES turns(turn_id),
    FOREIGN KEY (content_id) REFERENCES contents(content_id)
);
```

### 4.4 Schema version 與 indexes

使用 SQLite `PRAGMA user_version` 管理 schema version。啟動時依序執行向前 migration；migration 失敗時不得以未完成 schema 繼續寫入，並將錯誤回報給 runtime。

每一條 SQLite connection 建立後都必須設定：

```sql
PRAGMA foreign_keys = ON;
```

建立 indexes：

```sql
CREATE INDEX IF NOT EXISTS idx_turns_runtime_time
    ON turns(runtime_id, started_at, turn_id);
CREATE INDEX IF NOT EXISTS idx_turns_session_time
    ON turns(remote_session_id, started_at, turn_id);
CREATE INDEX IF NOT EXISTS idx_timeline_runtime_time
    ON timeline(runtime_id, recorded_at, event_id);
CREATE INDEX IF NOT EXISTS idx_timeline_turn_time
    ON timeline(turn_id, recorded_at, event_id);
CREATE INDEX IF NOT EXISTS idx_timeline_session_time
    ON timeline(session_id, recorded_at, event_id);
CREATE INDEX IF NOT EXISTS idx_timeline_type_time
    ON timeline(event_type, recorded_at, event_id);
```

---

## 5. Timestamp 與 identity

每筆 runtime、turn 與 timeline record 保存：

- timezone-aware ISO 8601 wall-clock time
- runtime 內用於計算 elapsed time 的 `monotonic_ns`
- `runtime_id`、`process_id` 與 `environment`
- `remote_session_id`、`remote_turn_id`、`call_id`

不同 runtime 的 `monotonic_ns` 不直接互相比較；跨 runtime 排序使用 wall-clock、`event_id` 與 runtime identity。

---

## 6. 必須記錄的事件

### 6.1 Runtime lifecycle

```text
runtime_started
runtime_finished
```

沒有 `runtime_finished` 的 runtime 視為可能異常終止或尚未結束。

### 6.2 AI turn

```text
ai_turn_started
ai_session_selected
ai_session_created
ai_turn_completed
ai_turn_failed
ai_turn_cancel_requested
```

`ai_turn_started` reference prompt 與 instructions content；完成或失敗時 reference final/partial output content。

### 6.3 HTTP request

```text
http_request_started
http_response_received
http_request_failed
http_request_closed
```

記錄 method、URL/path、stream flag、status、elapsed time、headers、request/response payload，以及 `local_request_id` 與 API response 提供的 `provider_request_id`（若有）。每筆 request 應 reference 對應的 turn 或 timeline operation。

### 6.4 SSE stream

Logging mode 有兩種：

- `normal`：記錄 SSE event type、timestamp、session/turn/call ID、delta length、累積 output length、read timing、錯誤與完整 final/partial output。
- `verbose`：在 `normal` 之上記錄 raw SSE line、完整 delta、詳細 headers 與 request/response payload。

兩種 mode 都保存完整 prompt、instructions、tool content、final output 與 partial output。`verbose` 只增加串流中間資料，不改變 turn 的完整內容保存契約。

每個 SSE stream 記錄：

```text
sse_open_started
sse_opened
sse_line_received
sse_event_received
sse_heartbeat_received
sse_stream_ended
sse_stream_failed
sse_stream_closed
```

reader 是逐行或逐 buffer 取得資料，因此第一版只宣稱：

- `last_read_at`：最後一次從 response iterator 取得 raw line/buffer 的時間。
- `last_event_at`：最後一次解析出完整 SSE event 的時間。

不宣稱 application layer 能精確觀察最後一個 socket byte 的時間。

每個 SSE event 記錄 event type、session/turn/call ID、timestamp、length，以及 since-last-read 和 since-last-event elapsed time。verbose mode 另保存 raw SSE data 或 parsed payload。

不保存每次 output delta 的完整累積文字；完整 output 在 turn record 的 `output_content_id` 保存一次。可記錄每次 delta 的長度與累積長度。

### 6.5 AI output

```text
ai_output_delta
ai_output_done
```

Runtime 必須維護 output accumulator。`ai_output_delta` 在 normal mode 保存時間、delta 長度與累積長度；verbose mode 可保存完整 delta。`ai_output_done` 或 turn failure 時保存完整 accumulated output。

若 stream 在 `turn.completed` 前 EOF、timeout、network error、parser error 或其他 exception 結束，不得標記 turn 為成功；應保存目前 accumulator 並標示 `partial` 或相應 failure status。

### 6.6 Tool call

```text
tool_call_received
tool_call_arguments_parsed
tool_call_started
tool_call_completed
tool_call_failed
tool_result_submitted
tool_result_submit_failed
```

完整 arguments、local result 與 result submission response 透過 `contents` 或 `payload_json` 保存，並保留 tool name、session ID、turn ID、call ID。

### 6.7 Approval

```text
approval_requested
approval_wait_started
approval_decision_received
approval_wait_ended
approval_cancelled
approval_expired
```

保存 proposal purpose、Forth source、decision、session/turn/call ID 與 approval wait duration。Forth source 可 reference `contents`。

### 6.8 Local Forth execution

```text
forth_execution_started
forth_execution_completed
forth_execution_failed
```

保存 source、stdout、stderr、stack snapshot、Task status 與 elapsed time。大型文字使用 `contents` 去重。

---

## 7. 兩個 debug case 的查詢需求

### 7.1 PowerShell SSE read timeout

依 `runtime_id` 與 `turn_id` 顯示 runtime start、AI turn start、HTTP request、SSE events、最後 output delta、stream failure 與 AI turn failure。

報告至少包含：runtime、process、environment、remote session、turn、stream start、last byte、last event、failure time、idle durations、exception type/message、output status 與 output content reference。

`output_content_id` 必須能還原 timeout 前已收到的完整 partial output。

### 7.2 WSL `requires_action` / `in_progress`

依 `runtime_id` 與 `turn_id` 依序顯示：

```text
sse_event_received(event_type=agent.session.requires_action)
current_actions_request_started
current_actions_response_received(status=...)
current_actions_payload
approval_requested
```

查詢結果必須可比較 SSE event 與後續 request 的 session ID、call ID、timestamp、response status、required actions，以及 runtime、process 與 environment identity。

---

## 8. SQLite writer

每個 runtime 建立自己的 SQLite connection，但連線指向該 environment 的共用 database。不同 runtime 不共用 Python connection object。

```sql
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
```

`busy_timeout` 是上限設定，不代表每筆 logging 都可以等待五秒。每次 logging write 都必須有更短的 logger-level deadline；超過 deadline 即放棄該筆 diagnostic write，並不得阻塞 SSE reader 或 AI flow。retry/backoff 只能在該 deadline 內進行。

每次 content、turn 或 timeline 寫入使用短 transaction。不得讓 network read、SSE iteration、approval wait 或 Forth execution 包在 SQLite transaction 內。

逐行 SSE logging 僅在 `verbose` mode 啟用。normal mode 只記錄必要的 event、timing、delta 長度與完整 final/partial output。

對短暫 database busy 採有限次數 retry/backoff；logger 失敗不得覆蓋原始 runtime error。已 commit 的資料必須保留；尚未 commit 的最後一筆資料可以遺失。

### 8.1 Partial-output checkpoint

為降低 hard crash 造成的 output 遺失，runtime 可依固定 delta 數量或時間間隔保存 partial-output checkpoint；checkpoint policy 必須有上限，不得每個 output delta 都強制 commit。

若 process 在最近一次 checkpoint 後被強制終止，checkpoint 後尚未 commit 的 output 可能遺失。正常 timeout、EOF、network error 或 parser error 路徑則必須在 exception handling 中保存當時 accumulator 的完整 partial output。

### 8.2 Snapshot 限制

stack snapshot 必須有明確大小上限。超過上限時保存截斷內容，並記錄 `stack_truncated = true` 與原始估計大小；不得因 stack 中含大型 object 而無界增加 log payload。

---

## 9. 查詢與分析

提供 read-only 查詢工具或既有 CLI command，至少支援：

```text
list runtimes
show runtime timeline
show turn timeline
show remote session timeline
find failed streams
find read timeouts
find requires_action followed by in_progress
show complete prompt/output by turn
export selected turn timeline
```

查詢工具可以讀 Windows 或 WSL database；runtime writer 仍在使用時使用 read-only connection。需要搬移 database 時，先建立一致性 snapshot。

---

## 10. 實作檔案規劃

新增：

```text
peforth/diagnostic_log.py
tools/ai_diagnostics.py
tests/test_diagnostic_log.py
tests/test_ai_diagnostics.py
```

修改：

```text
peforth/ai_bridge.py
peforth/f/ai.f
peforth/repl.py
```

`diagnostic_log.py` 負責 database path、schema、runtime identity、content 去重、turn occurrence、timeline event 與 logger failure isolation。

`ai_bridge.py` 負責 HTTP request、SSE line/event、stream close/failure 與 timing 記錄；`ai.f` 與 `repl.py` 負責 AI turn、tool、Forth execution 與 approval 記錄。

---

## 11. 測試計劃

### 11.1 Content deduplication

驗證相同內容只產生一筆 `contents`，相同內容的多次 turn 各自保留 occurrence，不同 runtime 同時 insert 相同 content 不產生 duplicate。

### 11.2 Multi-runtime SQLite write

建立多個 process 同時寫入同一 environment database，驗證所有 runtime 與 timeline rows 都保留、payload 不損壞、正常 contention 不產生未處理的 `database is locked`，且 WAL database 可同時讀取與寫入。

### 11.3 Complete and partial output

驗證正常 `output_done` 保存完整 output；stream timeout 保存已收到的完整 partial output；沒有 output 時標記 `failed_before_output`；重複 output 只保存一份 content，但每次 turn 均可還原。

### 11.4 SSE instrumentation

使用 fake response 驗證 output delta、heartbeat、requires_action、`[DONE]`、socket read timeout、malformed JSON 與 response close，每種情況都產生相應 timeline event。

### 11.5 Case correlation

建立 Windows 與 WSL、多個 runtime、多個 remote session 的 fixture，驗證查詢不會依 remote session ID 錯誤合併 local runtime。

### 11.6 Logging overhead 與 lock contention

驗證：

- logging disabled、normal、verbose 三種 mode 的 AI turn 與 SSE event processing elapsed time。
- logger-level maximum wait time 在 database busy 時仍有上限。
- 多個 process 同時寫入同一 environment database。
- 多個 runtime 同時 insert 相同 content。
- 大量 timeline events 與 read-only query 同時執行。
- logger write 失敗時原始 AI flow 仍可回報原始 error。

### 11.7 回歸

```bash
pytest -q
```

並測試 database 不可寫、logger exception、正常 AI flow 與既有 Forth flow。

---

## 12. 驗收標準

1. Windows 所有 runtime 可同時寫入 Windows SQLite database。
2. WSL 所有 runtime 可同時寫入 WSL SQLite database。
3. 每筆資料可追溯到 runtime、process、environment 與 turn。
4. 相同完整文字只保存一次；每次實際使用仍有獨立 occurrence。
5. 每次 AI turn 都可還原完整 prompt 與完整或 partial output。
6. HTTP、SSE、AI turn、tool call、approval 與 Forth execution 的關鍵時序可查詢。
7. 可以重建 PowerShell case 的 SSE activity 到 read timeout 的時間線。
8. 可以重建 WSL case 的 `requires_action` 到 `in_progress` response 的時間線。
9. logger failure 不會取代或吞掉原始 runtime error。
10. 已 commit 的 log 在 runtime crash 後仍保留。
11. 提供 read-only timeline、turn 與完整 content 查詢。
12. normal 與 verbose mode 的 logging wait time 有明確上限，且 verbose mode 的中間 SSE 詳細度高於 normal mode。
13. schema version、foreign-key enforcement、request ID 與 stack snapshot 大小限制均可驗證。

---

## 13. 不包含的行為變更

本計劃只加入診斷記錄與查詢，不改變：

- SSE timeout 設定
- network retry policy
- `in_progress` 狀態處理
- Agents API request contract
- approval decision semantics
- Forth execution semantics
