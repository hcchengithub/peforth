# peforth Herdr pane 存取規格與設計

## 目的與決策

本文件是 peforth Herdr pane 存取的唯一設計與介面規格。

保留 AI 可直接呼叫的 `computer_read_screen`、`computer_operate`，以及現有 Herdr Forth words。Herdr skill 提供操作流程和注意事項；Tools 提供結構化的 pane 能力。AI 可使用任一介面；使用者要求時，AI 也可在 Forth 程式中使用 Forth words。

兩個 Tools 都可指定任意 Herdr named session，並存取該 session 內的所有 pane。省略 `session` 時使用 `default`。不以 caller pane、workspace 或 session 限制目標範圍。

## AI Tools 規格

輸入和回傳均為 JSON object。實際提供給 AI 的 Tool 定義必須符合本文件列出的名稱、欄位、型別、預設值、驗證規則和回傳欄位。

### `computer_read_screen`

免批准讀取 pane 輸出。此 Tool 唯讀，不得送文字、按鍵或命令。

**輸入欄位**

| 欄位 | 型別 | 必要 | 預設值與限制 |
|---|---|---:|---|
| `session` | string | 否 | `default`；1–256 字元，不可有首尾空白、控制字元，且不可用 `-` 開頭；須為存在的 Herdr session |
| `pane_id` | string | 是 | 指定 session 中現存的 pane，例如 `w1:p2`；格式為 `w<英數字>:p<英數字>` |
| `source` | string | 否 | `visible`；只接受 `visible` 或 `recent-unwrapped` |
| `lines` | integer | 否 | 預設 80；必須大於 0；實際讀取最多 1000 行 |

拒絕未列出的欄位。

**回傳欄位**

- `session`、`pane_id`、`source`：實際使用的 session、pane 和讀取模式。
- `captured_at`：ISO 8601 擷取時間。
- `text`：pane 文字。
- `line_count`、`lines_requested`：回傳行數和原始要求行數。
- `truncated`：是否因行數或輸出位元組上限而截斷。
- `result`：Herdr 結果摘要，包含 `exit_code`、`stderr`、`truncated`。

### `computer_operate`

每次呼叫只執行一項 pane 操作。每個提案須明列目標 session、pane、操作種類和完整參數。

**輸入欄位**

| 欄位 | 型別 | 必要 | 預設值與限制 |
|---|---|---:|---|
| `session` | string | 否 | `default`；1–256 字元，不可有首尾空白、控制字元，且不可用 `-` 開頭；須為存在的 Herdr session |
| `pane_id` | string | 是 | 指定 session 中現存的 pane；格式為 `w<英數字>:p<英數字>` |
| `operation` | string | 是 | 只接受 `send_text`、`send_keys`、`run` |
| `text` | string | 條件式 | 只有 `send_text` 必須提供；1–10000 字元 |
| `keys` | array of strings | 條件式 | 只有 `send_keys` 必須提供；1–32 個按鍵名稱，每個 1–32 字元 |
| `command` | string | 條件式 | 只有 `run` 必須提供；1–10000 字元 |

`operation` 必須對應且只對應一個參數欄位：`send_text` 使用 `text`、`send_keys` 使用 `keys`、`run` 使用 `command`。拒絕缺少、錯配或多出的欄位。

**回傳欄位**

- `session`、`pane_id`、`operation`：實際使用的 session、pane 和操作。
- 與操作相符的單一參數欄位：`text`、`keys` 或 `command`。
- `success`：成功旗標。
- `result`：Herdr 結果，包含 `exit_code`、`response`、`stderr`、`truncated`。

輸入無效或使用者拒絕時不得執行 pane 操作。若執行結果無法確認，需回報此狀態並先檢查目標 pane，再決定是否重試。

## Forth words

以下都是普通 Forth words，可在互動式 REPL、Forth 定義和程式中使用與組合。不得因呼叫者是人或 AI 而隱藏、過濾或阻擋。

| Word | Stack effect | 行為 |
|---|---|---|
| `herdr-current-pane` | `( -- pane-id )` | 回傳目前 caller pane ID |
| `herdr-screen-read` | `( pane-id [line-count] -- snapshot )` | 讀取可見輸出；行數預設 80 |
| `herdr-screen-tail` | `( pane-id [line-count] -- snapshot )` | 讀取最近的未換行輸出；行數預設 80 |
| `herdr-screen-send-text` | `( pane-id text -- result )` | 傳送文字到 pane |
| `herdr-screen-send-keys` | `( pane-id keys -- result )` | 傳送 1–32 個 Herdr 按鍵名稱 |
| `herdr-screen-run` | `( pane-id command -- result )` | 在 pane 執行命令 |

Forth 操作 words 與 `computer_operate` 共用下方的 `ai-approve` 流程；沒有 AI-only guard，也沒有另一套 Computer Use 核准機制。

## 核准與 Trust

所有 pane 操作提案都使用共用的 `ai-approve`，並顯示目標 session、pane、操作和完整參數。選項為 Allow Once、Trust this AI task、Deny、Cancel。

- Allow Once 只批准當次提案。
- Trust this AI task 適用於目前 peforth AI Task 的後續提案；Task 完成、失敗或取消時失效。
- Runtime Trust 適用於目前 peforth runtime，包括透過 Tools 和 Forth words 發起的 pane 操作；直到執行 `ai-confirm` 或 process 結束才失效。
- 不另設 Computer Use 專用核准流程。

## 輸出限制、錯誤與隱私

- 單次讀取最多要求 1000 行；Herdr process 輸出上限為 64 KiB，結果會標示截斷。
- 執行讀取或操作前，依指定 Herdr session 驗證 pane ID。
- pane 存取不改變 UI 焦點，也不建立、移動或關閉 pane。
- Herdr 逾時、命令失敗或操作結果無法確認時回報錯誤；結果不明時先檢查目標 pane，不盲目重送。
- pane 文字和操作結果會回傳 Agents API，可能保留在遠端 session history。成功的讀取與操作結果正文不寫入本機 SQLite diagnostics database。

## 完成條件

- `computer_read_screen` 可免批准讀取指定 session 的任意 pane，預設 session 為 `default`，且保持唯讀。
- `computer_operate` 接受本文件列出的操作變體和 session，並遵循共用 `ai-approve`、Task Trust 與 Runtime Trust。
- 六個 Herdr Forth words 維持普通、可組合的 words，可供 REPL 與 Forth 程式使用。
- 提供給 AI 的 Tool 定義符合本文件 SPEC。
