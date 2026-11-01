# peforth AI Session 本地副本規格書 (SPEC)

作者： Antigravity Conversation ID： f4b68893-4920-4729-88a4-cb853de528b5

**狀態：** 規格定案（已根據實體資料驗證並大幅簡化）

**核心設計哲學：**

真正的 Sessions 是由遠端 OpenAI（Agents API）管理的，遠端才是唯一權威來源（Single Source of Truth）。因此，**本地 SQLite 資料庫的定位是遠端的「唯讀鏡像快取（Read-Only Mirror）」**。
既然是唯讀鏡像，同步流程應保持極簡與自動化——只需比對時間戳記、將有更新的內容抓回本地即可，不需要繁瑣的二階段預覽或互動確認選單。

---

## 一、背景與設計決策

1. **獨立於 Diagnostics DB：** `~/.peforth/ai-diagnostics.sqlite3` 是多 runtime 共用的短交易診斷紀錄，並非完整的對話歸檔。Session 本地副本使用獨立的 SQLite 檔案，避免寫入競爭與職責混淆。
2. **直接廢棄 `.ai_session.json`（無需遷移）：** 經實際檢查現有 `.ai_session.json`，裡面的 `title` 欄位全部為空字串 `""`，沒有任何歷史資料需要保留。新機制直接停用並移除 `.ai_session.json` 的讀寫邏輯即可，完全不必編寫遷移程式。
3. **支援隨時增量同步：** 舊 session 日後仍可能繼續對話，只要比對遠端 `last_active_at` 有更新，即同步最新 items。

---

## 二、儲存位置

使用獨立的 SQLite 資料庫檔案：

```text
<runtime-config-root>/sessions/sessions.sqlite3
```

- 實際路徑由 `ai_bridge._runtime_config_path()` 推導（例如 `~/.peforth/sessions/sessions.sqlite3`），Windows 與 WSL 各自使用其 runtime config root。
- 資料庫具備獨立的 `schema_version` 管理。

---

## 三、資料模型 (Schema)

經實體樣本（`ai-session-full-20261101-220954.json`）驗證，遠端回傳的每筆 item 均帶有唯一且格式規範的 `id`（`msg_*`、`rs_*`、`exec_*`、`fco_*`），且帶有 `turn_id`，但 item 本身不含個別時間戳記。

資料庫分為兩張表：

### 1. `sessions` 表（Session Metadata）

| 欄位 | 類型 | 說明 |
| :--- | :--- | :--- |
| `session_id` | TEXT PRIMARY KEY | 遠端 session ID（如 `sess_...`） |
| `description` | TEXT | 本地顯示摘要（自動生成或使用者自訂） |
| `created_at` | TEXT / INTEGER | 遠端建立時間 |
| `last_active_at` | TEXT / INTEGER | 遠端最後活動時間（用於判斷是否需同步） |
| `synced_at` | TEXT / INTEGER | 本地最後一次完成 items 同步的時間 |
| `status` | TEXT | 遠端狀態（如 `completed`, `active` 等） |
| `model` | TEXT | 使用的模型名稱 |
| `remote_deleted` | INTEGER | 遠端是否已不存在（預設 `0`；遠端刪除時標為 `1`，不自動刪本地資料） |

### 2. `session_items` 表（對話與操作明細）

| 欄位 | 類型 | 說明 |
| :--- | :--- | :--- |
| `id` | TEXT PRIMARY KEY | 遠端 item 唯一 ID（`msg_*`, `rs_*`, `exec_*`, `fco_*`） |
| `session_id` | TEXT | 所屬 `session_id`（建立索引） |
| `seq` | INTEGER | 在該 session 內的陣列順序（從 0 開始，查詢時 `ORDER BY seq ASC`） |
| `turn_id` | TEXT | 所屬對話輪次 ID（`turn_*`） |
| `type` | TEXT | `message` / `reasoning` / `function_call` / `function_call_output` |
| `role` | TEXT | `user` / `assistant`（非 message 類型為 NULL） |
| `raw_json` | TEXT | 該 item 的完整原始 JSON 字串 |

---

## 四、Description 生成規則

每個 session 的初始 `description` 格式為：

```text
YYYY-MM-DD HH:mm:ss | 第一則使用者訊息的第一句（最多 80 個字）
```

1. **時間格式：** 將 session 的 `created_at` 轉為建立當下的本地時區時間。生成後即作為靜態文字保存，日後若系統切換時區，維持原文字不重算。
2. **第一句提取與斷句規則：**
   - 尋找該 session 第一筆 `type == "message"` 且 `role == "user"` 的文字內容。
   - 依序尋找最早出現的斷句位置：
     1. 換行符號 `\n`
     2. 中文終止標點：`。`、`？`、`！`、`；`
     3. 英文終止標點：`?`、`!`、或**後接空白的句點** `. `（避免截斷小數點如 `3.14` 或檔名如 `ai.f`）
   - 若斷句前超過 80 個 Unicode 字元（或整段無標點且超過 80 字），則截取前 80 個 Unicode 字元並加上 `...`。
3. **保護規則：**
   - 建立時若尚無使用者訊息，先保存時間部分；待同步抓到第一則使用者訊息後再補齊。
   - 一旦 `description` 已經有完整內容（或經使用者手動修改），後續同步**絕不覆蓋**。

---

## 五、同步與操作流程

由於本地 SQLite 是遠端的唯讀鏡像，同步機制直接且單純：

### 1. 同步觸發時機與 Forth 命令

- **`ai-sessions`（主要入口）：** 使用者欲查看、列出 sessions 時觸發。執行流程為：
  1. 向遠端取得最新 session 索引 metadata。
  2. 自動執行差異同步（僅抓取本地缺失或有變更的 session items 寫入 SQLite，並自動生成/補充 description）。
  3. 從本地 SQLite 讀取並印出包含序號、標題（description）、建立時間與狀態的最新清單。
- **`ai-sync`（純同步命令）：** 獨立保留的同步指令。僅執行差異同步與資料庫更新，回報同步狀態（如更新了幾筆 session），不印出完整 sessions 清單。
- **不干擾核心流程：** REPL 啟動時秒開、REPL 退出時秒關、一般對話 `ai:` 時不額外同步，確保完全不被非必要的網路下載卡住。

### 2. 差異比對與寫入邏輯

1. 向遠端取得 session 索引列表（輕量 metadata，僅含 ID 與時間戳記）。
2. 逐一與本地 `sessions` 表比對：
   - **本地不存在**，或 **遠端 `last_active_at` 較新**（或尚未同步過 items）：向遠端拉取該 session 的所有 items。
   - **時間未變動**：直接跳過，不消耗多餘流量與時間。
   - **本地有、但遠端索引已消失**：將 `remote_deleted` 標記為 `1`，保留本地歷史資料不刪除。
3. 下載單一 session 的 items 後，以單一 SQLite 短交易寫入 `session_items`（依 `id` 做 `INSERT OR REPLACE` 並寫入 `seq`），同時更新 `sessions` 的 `last_active_at`、`synced_at` 及 `description`。若網路中途失敗，交易回滾，下次執行時自動重試。

### 3. 匯出單一 Session 為 JSON (`ai-export-session`)
- 提供匯出命令（如 `ai-export-session`），將指定 session 在 `session_items` 中的所有 `raw_json` 按 `seq ASC` 取出，組合成標準 JSON 陣列輸出至檔案（格式與 `ai-session-full-YYYYMMDD-HHMMSS.json` 完全一致），供備份或離線分析使用。

---

## 六、程式分層

- **Forth 層 (`ai.f`)：** 定義使用者互動命令（列表、同步、搜尋、匯出）。
- **Python Helper 層：** 負責 SQLite 讀寫與遠端 API 分頁抓取，不直接註冊 Forth words，保持介面乾淨。
- **清理舊包袱：** 移除程式碼中所有對 `.ai_session.json` 的讀寫依賴。

---

## 七、實作階段與驗收條件

1. **階段 1：建立本地 SQLite Helper**
   - 建立 `sessions/sessions.sqlite3`、`sessions` 與 `session_items` 表，以及 description 斷句生成函式。
2. **階段 2：實作差異同步與列表**
   - 比對遠端 `last_active_at`，自動拉取新增或變更的 session items 寫入資料庫，並移除 `.ai_session.json` 相關邏輯。
3. **階段 3：實作 JSON 匯出與本地查詢**
   - 支援從本地 DB 快速列出 sessions、搜尋對話內容，以及將單一 session 匯出為 JSON 檔。

**驗收條件：**
- 未變更的 sessions 不會重複下載 items；有新增或更新的 sessions 能正確拉取並依 `id` 合併。
- Description 符合本地時間、標點斷句與 80 Unicode 字元上限，且既有 description 不被同步覆蓋。
- 可將任一本地 session 完整匯出為標準 JSON 陣列檔案。
- 完全移除 `.ai_session.json` 依賴，且不影響既有 `ai-diagnostics.sqlite3` 運作。
