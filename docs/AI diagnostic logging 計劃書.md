# peforth AI Diagnostic Logging 計劃書

## 目標

為 peforth 的 AI transport、SSE stream、tool call 與 approval flow 建立可供 debug 的診斷記錄，讓多個 runtime instance 可以同時寫入並在事後重建事件時序。

Windows 與 WSL 各自使用 SQLite database，不使用一般文字 log file。

本計劃只定義 logging 的資料模型、寫入方式、事件內容與驗證方式；不在本階段修正 timeout、`in_progress` race 或其他 runtime bug。

---

## 1. 設計決策

### 1.1 Windows 與 WSL 分開儲存

建立兩個 execution environment 各自管理的 SQLite log database：

- Windows runtime：寫入 Windows 使用者的 peforth config directory
- WSL runtime：寫入 WSL 使用者的 peforth config directory

預設位置沿用目前的 `PEFORTH_CONFIG_DIR`；例如：

```text
Windows: %USERPROFILE%\\.peforth\\ai-diagnostics.sqlite3
WSL:     ~/.peforth/ai-diagnostics.sqlite3
```

若設定 `PEFORTH_CONFIG_DIR`，database 放在該 directory 下。不要讓 Windows 與 WSL 共用同一個 mounted database file，避免跨 OS SQLite locking、filesystem semantics 與同步問題。

跨 environment 比較時，透過 database export、SQLite attach/read-only 或複製後分析，不在 runtime 期間共用 database。

### 1.2 多 instance 共用同一個 environment database

同一台 Windows 或同一個 WSL environment 內的多個 peforth process 寫入同一個 SQLite database。

SQLite 只允許一個 writer，但會序列化短時間 transaction；每個 event 使用獨立、短小的 insert transaction，不讓 network read、approval wait 或其他長操作包在 database transaction 內。

啟用：

```sql
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;
PRAGMA synchronous = NORMAL;
```

啟動時應設定並驗證這些 pragma。讀取診斷資料時使用 read-only connection 或一般獨立 connection，不阻塞 runtime writer。

### 1.3 不限制診斷內容

本診斷 database 的目標是保留完整 debug 現場。第一版不對 prompt、tool arguments、request/response body、錯誤內容或其他欄位做敏感資訊刪除、遮罩或摘要化。

仍須保留資料型別與長度界線，避免單一異常 response 無限制佔用 database；這是穩定性與可查詢性的限制，不是資訊洩漏政策。

---

## 2. Instance identity

每個 peforth process 啟動時建立一個 `instance_id`，在該 process 生命週期內固定不變。

每筆 log 至少包含：

- `instance_id`：process 唯一識別值，建議 UUID
- `process_id`
- `parent_process_id`（若可取得）
- `environment`：`windows` 或 `wsl`
- `os_name`
- `hostname`
- `username`
- `working_directory`
- `source_path`
- `runtime_path`
- `runtime_version` 或 git revision（若可取得）
- `process_started_at`

`instance_id` 不使用 remote Agents API session ID 取代。多個 local process 可能使用同一個 remote session，而同一個 process 也可能在不同時間使用不同 remote session。

SQLite database 內保留 `instances` table，讓 event 可透過 `instance_id` 還原來源。

---

## 3. Database schema

### 3.1 `instances`

記錄每一個 runtime process。

```sql
CREATE TABLE IF NOT EXISTS instances (
    instance_id TEXT PRIMARY KEY,
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
    process_started_at TEXT NOT NULL,
    process_finished_at TEXT,
    exit_status TEXT,
    metadata_json TEXT
);
```

`environment` 僅允許目前定義的值：

```text
windows
wsl
```

### 3.2 `operations`

記錄一次可追蹤的高階 operation，例如一次 AI turn、一次 API request 或一次 SSE stream。

```sql
CREATE TABLE IF NOT EXISTS operations (
    operation_id TEXT PRIMARY KEY,
    instance_id TEXT NOT NULL,
    parent_operation_id TEXT,
    operation_type TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    started_monotonic_ns INTEGER NOT NULL,
    ended_monotonic_ns INTEGER,
    status TEXT,
    remote_session_id TEXT,
    remote_turn_id TEXT,
    request_id TEXT,
    error_type TEXT,
    error_message TEXT,
    metadata_json TEXT,
    FOREIGN KEY (instance_id) REFERENCES instances(instance_id),
    FOREIGN KEY (parent_operation_id) REFERENCES operations(operation_id)
);
```

建議的 `operation_type`：

- `ai_turn`
- `http_request`
- `sse_stream`
- `tool_call`
- `approval_wait`
- `local_forth_execution`

### 3.3 `events`

事件表是主要的 append-only timeline。

```sql
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id TEXT NOT NULL,
    operation_id TEXT,
    recorded_at TEXT NOT NULL,
    monotonic_ns INTEGER NOT NULL,
    sequence_no INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    direction TEXT,
    remote_session_id TEXT,
    remote_turn_id TEXT,
    call_id TEXT,
    event_name TEXT,
    http_method TEXT,
    url TEXT,
    http_status INTEGER,
    elapsed_ms REAL,
    payload_json TEXT,
    error_type TEXT,
    error_message TEXT,
    FOREIGN KEY (instance_id) REFERENCES instances(instance_id),
    FOREIGN KEY (operation_id) REFERENCES operations(operation_id)
);
```

`sequence_no` 由每個 instance 在 memory 中遞增；database 的 `event_id` 則提供跨 instance 的 SQLite insertion order。分析時主要依 `recorded_at`、`monotonic_ns`、`event_id` 與 instance identity 判斷，不把不同 process 的 monotonic clock 直接互相比較。

### 3.4 常用 indexes

```sql
CREATE INDEX IF NOT EXISTS idx_events_instance_time
    ON events(instance_id, recorded_at, event_id);

CREATE INDEX IF NOT EXISTS idx_events_operation_time
    ON events(operation_id, recorded_at, event_id);

CREATE INDEX IF NOT EXISTS idx_events_session_time
    ON events(remote_session_id, recorded_at, event_id);

CREATE INDEX IF NOT EXISTS idx_events_type_time
    ON events(event_type, recorded_at, event_id);

CREATE INDEX IF NOT EXISTS idx_operations_instance_time
    ON operations(instance_id, started_at, operation_id);
```

---

## 4. Timestamp 規則

每筆 record 同時保存兩種時間：

### 4.1 Wall-clock time

`recorded_at`、`started_at`、`ended_at` 使用 timezone-aware ISO 8601 字串，保留 offset。

用途：

- 跨 process、跨 Windows/WSL database 比較
- 人類閱讀
- 對照外部 API 或 terminal 時間

### 4.2 Monotonic time

`monotonic_ns` 使用 process 內的 monotonic clock。

用途：

- 計算 request、stream、approval wait 的 elapsed time
- 避免系統時間調整造成 duration 錯誤

跨 process 不直接比較 monotonic value；跨 environment 的排序以 wall-clock 與 database event ordering 為主。

---

## 5. 必須記錄的事件

### 5.1 Process lifecycle

```text
instance_started
instance_finished
```

`instance_started` 必須在任何 AI request 前寫入；`instance_finished` 應在正常退出時寫入。異常退出無法保證寫入，因此分析工具必須能依未結束 instance 判斷可能是 crash 或強制終止。

### 5.2 HTTP request

每次 `_request()` 建立或完成 request 時記錄：

```text
http_request_started
http_response_received
http_request_failed
http_request_closed
```

欄位至少包含：

- operation ID
- parent operation ID
- HTTP method
- URL/path
- `stream` flag
- response status
- request start/end time
- elapsed time
- exception type/message
- response headers（若取得）
- request/response payload

Authorization credential 不需在 logging 層特別遮罩；payload 與 headers 的保存規則依本計劃採完整診斷記錄。

### 5.3 SSE stream

每個 SSE stream 記錄：

```text
sse_open_started
sse_opened
sse_bytes_received
sse_line_received
sse_event_received
sse_heartbeat_received
sse_stream_ended
sse_stream_failed
sse_stream_closed
```

` sse_bytes_received` 不必每個 byte 一筆 row；以每次 `readline()` 或每個完整 raw line 為一筆即可。

每個 stream event 至少保留：

- raw line 或完整 SSE data block
- parsed event type
- session ID
- turn ID
- call ID
- received timestamp
- bytes/line length
- accumulated event count
- since-last-byte milliseconds
- since-last-event milliseconds

這是 PowerShell timeout investigation 的核心資料。

### 5.4 AI turn

```text
ai_turn_started
ai_session_selected
ai_session_created
ai_turn_output_delta
ai_turn_output_done
ai_requires_action_received
ai_turn_completed
ai_turn_failed
ai_turn_cancel_requested
```

`ai_turn_output_delta` 可逐 delta 記錄完整內容；不應只記最後累積字串，否則無法知道最後一次 output 的時間。

### 5.5 Tool call

```text
tool_call_received
tool_call_arguments_parsed
tool_call_started
tool_call_completed
tool_call_failed
tool_result_submitted
tool_result_submit_failed
```

至少包含：

- tool name
- arguments
- call ID
- turn ID
- session ID
- local execution operation ID
- result
- result submission response

### 5.6 Approval flow

```text
approval_requested
approval_wait_started
approval_decision_received
approval_wait_ended
approval_expired
approval_cancelled
```

至少包含：

- AI Task identity
- session/turn/call ID
- proposal purpose
- proposed Forth source
- decision：`allow_once`、`trust_task`、`deny`、`cancel`
- approval wait duration

### 5.7 Local Forth execution

```text
forth_execution_started
forth_execution_completed
forth_execution_failed
```

記錄 source、stdout、stderr、stack snapshot、Task status 與 elapsed time。

---

## 6. 兩個目前 debug case 的必要查詢能力

### 6.1 PowerShell SSE read timeout

分析查詢必須能依 instance 與 operation 顯示：

```text
instance_started
ai_turn_started
sse_opened
所有 sse_event_received
最後 sse_bytes_received
最後 sse_event_received
approval_wait_started / ended（若有）
sse_stream_failed
ai_turn_failed
```

最重要的報告欄位：

```text
environment
instance_id
process_id
remote_session_id
operation_id
stream_started_at
last_byte_at
last_event_at
failure_at
idle_since_last_byte_ms
idle_since_last_event_ms
exception_type
exception_message
```

### 6.2 WSL `requires_action` / `in_progress`

分析查詢必須能把下列事件依序列出：

```text
sse_event_received(type=agent.session.requires_action)
current_actions_request_started
current_actions_response_received(status=...)
current_actions_payload
approval_requested
```

至少比較：

- event 的 session ID 與 GET 使用的 session ID
- event 的 call ID 與 GET response 中的 call ID
- event timestamp 與 GET response timestamp
- GET response status
- GET response required actions
- 是否存在 retry
- process/environment/instance identity

不能只保存最後錯誤文字，否則無法判斷是 API eventual consistency、session mismatch、重複 event 或 client ordering 問題。

---

## 7. SQLite writer 設計

### 7.1 Connection policy

每個 process 建立自己的 SQLite connection；不跨 process 共用 Python connection object。

連線設定：

- `check_same_thread` 依實際 thread model 決定；若 logger 只在同一 thread 使用，維持預設。
- 每次寫入使用短 transaction。
- 使用 parameterized SQL。
- 以 `busy_timeout` 處理其他 instance 短暫持有 writer lock。
- 不在 exception handler 中無限 retry。
- 若 database 暫時 busy，採有限次數、短暫 backoff；最終失敗時要將 logger failure 寫到 stderr，不能讓 AI runtime 因 logging failure 崩潰。

### 7.2 Logger failure isolation

Diagnostic logging 是觀測功能，不得成為 AI runtime 的必要依賴。

下列情況不得覆蓋原始 AI error：

- SQLite database locked
- disk full
- database directory 不可寫
- schema migration 失敗
- JSON serialization 失敗
- connection error

logger 應回報自身錯誤，並讓原本的 network、SSE、approval 或 Forth exception 照常傳遞。

### 7.3 Crash resilience

每個 event 寫入後即可被其他 connection 讀取；不要累積到 process 結束才 flush。

對於 process 被強制終止的 case：

- 已 commit 的 event 必須保留。
- 尚未 commit 的最後一筆 event 可以遺失。
- analysis 工具應把沒有 `instance_finished` 的 instance 標示為 incomplete。

---

## 8. 讀取與分析工具

第一版至少需要一個 read-only CLI 或 Python utility，支援：

```text
list instances
show instance timeline
show operation timeline
show remote session timeline
find failed streams
find read timeouts
find requires_action followed by in_progress
export selected timeline to JSON or Markdown
```

建議查詢輸出必須帶有：

```text
recorded_at
environment
instance_id
process_id
operation_id
event_type
remote_session_id
remote_turn_id
call_id
elapsed_ms
error_type
error_message
```

分析工具可以讀 Windows database 或 WSL database，但不應在 runtime writer 正在使用時直接搬動 database；使用 SQLite read-only connection，或先建立一致性 snapshot。

---

## 9. 實作範圍與檔案規劃

### 第一階段：logger 基礎層

預計新增：

```text
peforth/diagnostic_log.py
```

責任：

- resolve database path
- open/configure SQLite connection
- initialize schema
- register instance
- create/finish operation
- append event
- close instance
- handle logger failures

不在這一層加入 AI-specific interpretation。

### 第二階段：AI bridge instrumentation

修改：

```text
peforth/ai_bridge.py
```

加入：

- HTTP request lifecycle events
- SSE raw line/event timing
- stream close/failure events
- session/turn/call correlation fields

### 第三階段：Forth AI flow instrumentation

修改：

```text
peforth/f/ai.f
```

加入：

- AI turn lifecycle
- requires_action event
- tool execution
- tool result submission
- local Forth execution
- output delta/completion

### 第四階段：REPL approval instrumentation

修改：

```text
peforth/repl.py
```

加入：

- approval request
- approval wait start/end
- decision
- cancellation
- approval failure

### 第五階段：分析工具與測試

預計新增：

```text
tools/ai_diagnostics.py
```

測試：

```text
tests/test_diagnostic_log.py
tests/test_ai_diagnostics.py
```

以上是 implementation plan，不代表本階段已修改這些檔案。

---

## 10. 測試計劃

### 10.1 SQLite concurrency

建立多個 process 同時 append events，驗證：

- 所有 process 的 events 都保留。
- `instance_id` 不重複。
- event payload 不交錯或損壞。
- database 不因正常 contention 產生 `database is locked` 未處理錯誤。
- WAL database 可同時讀取與寫入。

### 10.2 Crash handling

模擬 process 在 event write 前後終止，驗證：

- 已 commit 的 row 可讀取。
- incomplete instance 可辨識。
- logger failure 不會改寫原始 runtime exception。

### 10.3 SSE instrumentation

用 fake response 產生：

- 多個 SSE lines
- comment heartbeat
- output delta
- requires_action
- `[DONE]`
- socket read timeout
- malformed JSON
- response close

驗證每個關鍵時序都有對應 event。

### 10.4 Cross-instance correlation

建立 Windows/WSL 格式不同的 instance metadata fixture，確認查詢可以依：

- environment
- instance_id
- process_id
- remote session ID
- operation ID

正確分組，不把兩個 application 的事件合併成同一條 local process flow。

### 10.5 完整回歸

執行：

```bash
pytest -q
```

Logging disabled、database 不可寫、database locked、正常 AI flow 都必須有明確測試結果。

---

## 11. 驗收標準

1. Windows 與 WSL 各有自己的 SQLite diagnostic database。
2. 同一 environment 的多個 peforth process 可以同時寫入同一 database。
3. 每筆 event 可追溯到明確的 `instance_id`、process、environment 與 operation。
4. HTTP、SSE、AI turn、tool call、approval、local Forth execution 都有可查詢的 lifecycle events。
5. SSE 每次有效 event 與 read failure 都保存 timing。
6. 可以重建 PowerShell case 的最後一次 SSE activity 到 timeout 的時間線。
7. 可以重建 WSL case 的 `requires_action` 到 `_current_actions()` 回覆 `in_progress` 的時間線。
8. logger failure 不會取代或吞掉原始 runtime error。
9. 強制終止後，已 commit 的 events 保留，未完成 instance 可辨識。
10. 提供 read-only timeline 查詢與 export 能力。
11. 本階段只加入 logging，不改變 timeout、retry、API status 判斷或 approval 行為。

---

## 12. 本計劃明確不做的事

- 不在 logging implementation 中修正 300 秒 SSE timeout。
- 不在 logging implementation 中對 `in_progress` 做 retry 或重新判斷。
- 不把 Windows 與 WSL database 合併成單一 live database。
- 不使用一般文字 log file 作為主要儲存。
- 不依賴 process 結束時才寫入 log。
- 不讓 logging transaction 包住 network request 或 approval wait。
- 不把不同 instance 僅依 remote session ID 合併。
- 不以 logging 自動重試 AI request、tool call 或 Forth execution。
- 不在本計劃內改動 AI API contract。
