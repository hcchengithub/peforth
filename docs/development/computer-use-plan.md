# Computer Use：設計與實作計畫

狀態：草案  
日期：2026-10-27

## 目標

讓 AI 能在 peforth 工作流程中讀取並操作使用者指定的 Herdr 終端 pane。讀取用於理解輸出、錯誤和工作脈絡；會改變 pane 狀態的輸入、按鍵和命令則必須由使用者逐次批准。所有可重用能力以 Forth words 實作，方便在 VM 中維護、組合與實驗。

第一階段只涵蓋 Herdr 管理的終端 pane。不做桌面截圖、滑鼠控制、其他視窗辨識或背景監看。

## 架構

```text
AI
 ├─ computer_read_screen tool（免批准）
 │    └─ 固定呼叫唯讀 Forth words
 └─ computer_operate tool（每次操作需批准）
      └─ 核准後呼叫指定操作 Forth word
           └─ Herdr pane API / CLI
```

- **Forth 層**提供可組合的能力；Forth 組合流程留在 AI 功能區，需要 Python 或 Herdr 整合時使用可見的 `code` words。
- **Tool 層**把有限能力提供給 AI，固定呼叫指定 Forth words 和明確參數，不接受任意 Forth source。
- **批准層**在任何改變 pane 狀態的 AI 操作執行前核准，並綁定目標 pane、操作種類和完整參數。

## Forth words 草案

唯讀：

- `herdr-current-pane ( -- pane-id )`：從 Herdr 呼叫端脈絡解析 pane ID，不猜測或沿用過期 ID。
- `herdr-screen-read ( -- snapshot )`：讀取目前 pane 的可見終端文字。
- `herdr-screen-tail ( line-count -- snapshot )`：讀取最近指定行數，限制最大值並回報截斷狀態。

操作：

- `herdr-screen-send-text ( text -- result )`：輸入文字，不自行送 Enter。
- `herdr-screen-send-keys ( keys -- result )`：送出經驗證的具名按鍵。
- `herdr-screen-run ( command -- result )`：把明確命令送到指定 shell pane 並提交；只可由批准後的 AI 操作路徑呼叫。

snapshot 至少含 pane ID、讀取來源、取得時間、文字、行數和截斷狀態。操作結果含 pane ID、操作種類及成功或錯誤狀態。

## Tool 和批准規則

1. `computer_read_screen` 只接受讀取來源與行數等參數，只呼叫唯讀 words，免批准；不能接受命令、按鍵或任意路徑。
2. `computer_operate` 只接受有限操作種類與明確參數。批准畫面顯示目標 pane、完整文字或命令、按鍵序列和是否包含 Enter。
3. 每次批准只授權畫面上展示的那次操作。目標或參數改變、pane 狀態過期時，重新核准。
4. 免批准讀取 tool 不得間接呼叫操作 words。操作 tool 不提供 Trust this task 或 Runtime Trust。
5. 通用 `peforth_run_forth`、Task Trust 和 Runtime Trust 不能繞過電腦操作批准。操作 word 必須驗證 AI 操作的逐次授權，或使用 VM 批准層簽發、綁定操作參數的一次性授權。
6. 使用者在 REPL 手動執行 Forth，與 AI 發起操作分開處理；不能把手動執行當成 AI 授權。

## Herdr 狀態與錯誤處理

- 控制 pane 前確認程序位於 Herdr 管理的 pane，並由 Herdr 取得真實 pane ID。
- 使用明確 pane ID；不把 UI 焦點或呼叫者環境變數當成任意目標。
- 執行前確認 pane 仍存在且身分未變。預設不改變焦點、不建立或關閉 pane。
- 對逾時、連線錯誤或結果不明確的操作，回報狀態並先讀取 pane 確認；不得盲目重送。
- 遵循 peforth 專用的本機 Herdr 執行路徑，不以通用 shell tool 取代整合入口。
- 輸出設行數與位元組上限；錯誤時採取失敗封閉，不改操作其他 pane。

## 隱私與安全邊界

終端文字可能含密碼、token 或個人資料。只在工作需要時讀取，限定 pane 與行數，避免不必要的持久紀錄。免批准能力維持唯讀；任何輸入、按鍵或命令都屬操作，必須先核准。批准後不得追加、改寫或換目標。不能由一般讀取入口、背景工作或廣泛信任模式旁路操作批准。

## 分階段實作

### Phase 1：契約與批准邊界

- 確認 Herdr 讀取、輸入及回應格式，定義 snapshot、operation request、批准收據和 result。
- 找出 AI tool 註冊位置與 VM 中批准、Task Trust、Runtime Trust 的傳遞方式。
- 設計通用 Forth 執行路徑下的防繞過機制，先完成威脅與失敗情境審查。

### Phase 2：唯讀能力

- 加入 current-pane、read、tail Forth words 和固定的唯讀 tool bridge。
- 加入 pane 身分檢查、行數上限、截斷資訊和清楚的錯誤回報。
- 確認讀取入口不能造成任何 pane 狀態變化。

### Phase 3：逐次批准操作

- 加入 send-text、send-keys、run words 和有限參數的操作 tool。
- 批准畫面綁定 pane 與完整操作內容；批准拒絕、取消或逾時時不得送出。
- 驗證通用 Forth 執行與廣泛 Trust 狀態不能繞過逐次批准。

### Phase 4：驗證與推出

- 驗證核准的目標與參數和實際送出內容完全一致。
- 驗證 pane 更換、重複提交、連線錯誤和逾時不會造成錯誤目標操作。
- 先在本機 Herdr pane 使用並記錄限制，再評估是否擴充能力。

## 完成條件

- AI 可按需免批准讀取正確 pane 的有限行數。
- 任何 AI pane 操作都先展示目標與完整效果，並取得該次明確批准。
- 使用者可在 Forth REPL 直接試用和組合相關 words。
- 通用執行入口和 Trust 狀態都不能旁路操作批准。
- 錯誤與逾時可辨識，不會默默操作其他目標。
