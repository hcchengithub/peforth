# Computer Use：設計與實作計畫

狀態：核心功能已實作；268 個 unittest 通過；live Herdr 手動驗收與推出待完成
日期：2026-10-28

## 目標

讓 AI 在 peforth 工作流程中讀取並操作使用者指定的 Herdr 終端 pane。讀取用於了解輸出、錯誤和工作脈絡；會改變 pane 狀態的輸入、按鍵和命令必須逐次取得使用者批准。可重用的介面以 Forth words 提供，方便在 VM 中維護、組合與實驗。

## 架構

- Agents API 的 `computer_read_screen` tool 提供唯讀螢幕讀取，不需要批准。
- Agents API 的 `computer_operate` tool 提供有限的 pane 操作，每次操作都需要批准。
- `ai.f` 負責 Forth words 與 AI tool 流程；`ai_tools.py` 負責 Herdr CLI 呼叫及輸入、輸出處理。
- 讀取與操作都要確認 peforth 執行環境位於 Herdr pane，並驗證 pane ID 是有效的 live pane。

## 已實作的 Forth words

- `herdr-current-pane ( -- pane-id )`：回傳目前呼叫端的 Herdr pane ID。
- `herdr-screen-read ( pane-id [line-count] -- snapshot )`：讀取 pane 畫面；未提供行數時使用 80 行。
- `herdr-screen-tail ( pane-id [line-count] -- snapshot )`：讀取 pane 最近的輸出；未提供行數時使用 80 行。
- `herdr-screen-run ( pane-id command -- result )`：在 pane 執行命令。
- `herdr-screen-send-text ( pane-id text -- result )`：傳送文字到 pane。
- `herdr-screen-send-keys ( pane-id keys -- result )`：傳送 Herdr CLI 支援的命名按鍵；keys 是 1 到 32 個非空按鍵名稱的清單。

Read 與 tail 支援 `visible`、`recent`、`recent-unwrapped` 來源。單次讀取最多要求 1000 行；CLI 輸出也受 64 KiB 上限約束，超出時會標示截斷。Snapshot 記錄 pane、來源、擷取時間、文字、行數、截斷狀態與 CLI 結果。

操作結果會包含 pane ID、操作種類、實際命令／文字／按鍵、成功狀態及 Herdr 回應，包括 exit code、stderr 和截斷狀態。

## 批准邊界

1. `computer_read_screen` 只呼叫唯讀能力，不接受命令、按鍵或任意 Forth source。
2. `computer_operate` 將操作送入 peforth 的批准流程。畫面顯示目標 pane、操作種類和完整參數，使用者可允許一次、拒絕或取消。
3. 每次允許只授權畫面所列的 pane、操作與參數。參數改變就需要重新批准。
4. Computer Use 使用 `computer_use` kind 的一次性批准；Task Trust 與 Runtime Trust 都不能略過這道批准。
5. AI 透過一般 `peforth_run_forth` 呼叫操作 word 會被拒絕，必須改走 `computer_operate` tool。
6. 使用者在 REPL 手動呼叫操作 word 時，也會取得該次操作專用的一次性批准；這不會形成 AI 的可重用授權。

批准提案沿用 `ai-approve` 的 `purpose` 與 `source` 欄位。範例：

```text
purpose:
Computer Use: 在 pane w1:p3 執行命令
Command: git status --short

source:
s' w1:p3' s' git status --short' herdr-screen-run
```

## 輸出保存與錯誤處理

螢幕讀取與操作結果會作為 tool result 傳回 Agents API，可能保留在遠端 session history。本機 SQLite diagnostics 不保存成功的 screen 或 operation result body。

若操作發生 timeout、連線錯誤或回應無法確認，錯誤會提醒使用者先檢查目標 pane，再決定是否重試，避免重複執行可能已成功的操作。pane 不存在、CLI 回應格式錯誤或輸出遭截斷時，會回報可辨識的結果或錯誤。

## Herdr 狀態與錯誤處理

- 控制 pane 前確認程序位於 Herdr 管理的 pane，並由 Herdr 取得真實 pane ID。
- 使用明確 pane ID；不把 UI 焦點或呼叫者環境變數當成任意目標。
- 執行前確認 pane 仍存在且身分未變。預設不改變焦點、不建立或關閉 pane。
- 對逾時、連線錯誤或結果不明確的操作，回報狀態並先讀取 pane 確認；不得盲目重送。
- 遵循 peforth 專用的本機 Herdr 執行路徑，不以通用 shell tool 取代整合入口。
- 輸出設行數與位元組上限；錯誤時採取失敗封閉，不操作其他 pane。

## 隱私與安全邊界

終端輸出可能包含密碼、token 或個人資料。`computer_read_screen` 的回應及操作結果會作為 tool result 傳回 Agents API，因此可能保留在遠端 session history；本機 SQLite diagnostics 不保存成功讀取或操作結果的正文。只讀取工作所需的 pane 與行數。唯讀操作不需核准；任何輸入、按鍵或命令都必須逐次核准，核准後不得追加、修改參數或變更目標。

## 分階段實作

### Phase 1：契約與批准邊界（已完成）

- 定義 Herdr CLI 呼叫、operation request 與 result 格式。
- 完成 `computer_use` 批准 kind，並阻止一般 Forth 執行和 Trust 狀態繞過。

### Phase 2：唯讀能力（已完成）

- 加入 current-pane、read、tail Forth words 與固定的唯讀 tool bridge。
- 加入 pane 身分檢查、行數及輸出上限、截斷資訊和錯誤回報。

### Phase 3：逐次批准操作（已完成）

- 加入 run、send-text、send-keys words 與 `computer_operate` tool。
- 批准綁定 pane 與完整操作內容，並限制授權只能使用一次。

### Phase 4：驗證與推出（自動化測試完成；live 手動驗收待完成）

- 268 個 unittest 通過，其中包含 10 個 Computer Use approval 測試。
- 推出前仍需在 live Herdr 環境手動驗收 pane 更換、timeout／連線錯誤與避免重複送出等情境。
- 手動驗收完成後，再評估是否擴充操作種類或輸出能力。

## 完成條件

- AI 能按需讀取正確 pane 的有限行數，並清楚辨識截斷狀態。
- AI 對 pane 的每次操作都先顯示目標與完整參數，並取得該次明確批准。
- 使用者可在 Forth REPL 試用及組合相關 words。
- 一般執行入口與 Trust 狀態不能繞過操作批准。
- 錯誤與逾時可辨識；結果未確認時會先提示檢查 pane，避免盲目重試。
