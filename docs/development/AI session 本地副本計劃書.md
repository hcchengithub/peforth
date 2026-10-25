# peforth AI session 本地副本計劃書

作者： peforth LBB2 WSL Active AI session: (untitled) [sess_078cfd7e70c0121e006adb2f5b2e708192b8db2288b836d87d]

**狀態：** 討論草案；目前只記錄設計，不代表已開始實作。

**目標：**

建立遠端 AI sessions 的本地可搜尋副本，讓使用者能列出、描述、回顧和再次參考曾經的對話。同步由獨立命令明確觸發，避免啟動或正常結束 REPL 時意外下載大量歷史資料。

**範圍：**

本計畫涵蓋本地儲存、description、遠端差異檢查、同步流程，以及將 `.ai_session.json` 的現有標題遷移到新儲存。診斷 logging 維持原用途，不把 session archive 寫進 diagnostics database。

---

## 一、現況與設計依據

1. 遠端 session 索引提供 session ID、建立時間、最後活動時間、狀態和模型等資訊。舊 session 之後仍可能增加對話，所以「REPL 正常結束時存一次」不能作為唯一同步時機。
2. 現有 `ai-context` 取得指定 session 最近幾輪對話，會依 API 分頁；它不是完整 archive 的專用同步介面。
3. `.ai_session.json` 目前保存 session ID 與 title，適合遷移為每個 session 的本地 description，不應在同步時被遠端資料覆蓋。
4. `~/.peforth/ai-diagnostics.sqlite3` 的資料模型是 runtimes、AI turns、timeline events 和診斷用 contents。檢查當下有 137 個 turns、21 個 remote session IDs，而遠端索引有 38 個 sessions，內容並非完整 session archive。
5. diagnostics logger 是多 runtime 共用的 SQLite writer，採 WAL，且寫入期限短。長時間的 archive 同步不應和診斷記錄競爭同一個資料庫。

---

## 二、儲存位置與責任

使用獨立 SQLite 檔案，保留 `sessions/` 子目錄：

```text
<runtime-config-root>/sessions/sessions.sqlite3
```

WSL 預設位置為 `~/.peforth/sessions/sessions.sqlite3`；實際路徑應由 runtime config root（`ai_bridge._runtime_config_path()`）推導，避免硬編碼使用者家目錄。Windows 和 WSL 各自使用其 runtime config root。

SQLite 是 sessions 的主要本地副本。Session ID 是資料庫主鍵，不再是一個 session 一個檔案。必要時可以另行設計匯出功能，但匯出檔不作為同步的權威來源。

Diagnostics DB 保持獨立；session 對話內容、description 和同步狀態都不寫入 diagnostics tables。

---

## 三、資料模型草案

最少需要兩類資料：

- **Session metadata：** `session_id`、`description`、description 來源、遠端 `created_at`、遠端 `last_active_at`、`synced_at`、archive 是否完整，以及必要的同步狀態。
- **Session items：** session 內按遠端順序保存的 API items；保留原始 JSON，以免遺失 assistant 回覆、工具互動或其他 item 類型。

概念上可分成 `sessions` 與 `session_items` 兩張表。實際主鍵、cursor 和去重方式需先確認 API item ID 的穩定性；若 item ID 可穩定識別，按 ID 合併。若無法確認，第一版對有變更的 session 重新取得完整快照，再以單一 session 為單位替換。

SQLite schema 需有自己的版本遷移機制，與 diagnostics DB 的 schema version 分開。

---

## 四、Description 規則

新 session 的初始 description 格式：

```text
YYYY-MM-DD HH:mm:ss | 第一則使用者訊息的第一句（最多 80 個字）
```

- 時間使用建立 session 時的 runtime 當地時間；內部仍保存遠端原始時間，方便排序與轉換。
- 80 個字按 Unicode 字元截取，不按 UTF-8 位元組截取。
- 建立時尚無使用者訊息，就先只保存時間；收到第一則訊息後補上第一句。
- 後續同步不重建 description。若使用者手動修改，修改後的內容一直優先保留。

遷移與初始化的優先順序：

1. 新 sessions DB 已有 description：保留。
2. 否則 `.ai_session.json` 有舊 title：將 title 搬成 description。
3. 兩者都沒有：才用遠端建立時間和第一則使用者訊息生成 description。

遠端對話只用來填補空 description，不覆蓋任何既有本地 description 或遷移來的 title。

---

## 五、檢查與同步流程

### `ai-sessions`：列出本地狀態並預覽差異

1. 先列出本地資料庫已有的 sessions 和 descriptions。
2. 取得遠端 session 索引的輕量 metadata。
3. 依 session ID 對照本地與遠端，分類為：
   - 本地沒有：新 session。
   - 本地有，遠端 `last_active_at` 較新：可能需要更新。
   - 本地有，遠端索引找不到：遠端已不存在；保留本地資料並提示，不自動刪除。
   - 時間沒有變化：目前不需下載內容。
4. 顯示候選數量與 description，讓使用者知道同步可能涉及哪些 sessions。

### `ai-sync-sessions`：取得完整內容

1. 顯示候選清單並詢問是否同步；允許同步全部、選取項目或取消。
2. 只對使用者選中的新 session 或變更 session 讀取完整 item pages。
3. 網路下載期間不持有 SQLite 寫入交易。單一 session 的所有頁面成功取得後，再以短交易提交該 session 的 items 與同步 metadata。
4. 只有內容完整提交成功後才更新本地 `last_active_at`／`synced_at`。失敗時保留舊副本，供下次重試。
5. 以遠端 `last_active_at` 作為便宜的變更提示；同步前需檢查時間精度及分頁 cursor 行為。若時間相同但 API 可提供穩定 item ID，使用最新 item ID 作補充判斷；若無法可靠增量下載，對候選 session 重新抓取完整快照。

不在一般 REPL 關閉時自動同步所有 sessions。舊 session 可能日後續用，明確的同步命令才是更新本地副本的可靠入口。

---

## 六、遷移並退役 `.ai_session.json`

1. 讀取舊檔的 session ID/title，將 title 以「只補空值」方式寫入 sessions DB。
2. 若該 session 尚未下載對話，建立標示為未完整的 metadata row，避免舊 title 遺失。
3. 遷移需可重複執行：中斷後重跑不覆蓋現有 description，也不重複建立 session items。
4. 驗證所有舊 title 都已存在於 DB 後，程式停止讀寫 `.ai_session.json`，並在遷移成功後退役該檔。
5. 若任何項目遷移失敗，保留舊檔並提供可診斷錯誤；不以部分成功冒充完成。

---

## 七、程式分層與錯誤處理

- 使用者命令與 Forth 流程放在 `ai.f`，以 colon definitions 組合命令。
- SQLite 持久化使用不註冊 Forth words、也不承擔應用流程的 Python helper；遠端 HTTP 分頁沿用目前的 AI bridge／HTTP 邊界。
- 同步命令只在使用者確認後下載對話；preview 階段只取遠端索引 metadata。
- 取消、網路錯誤或資料解析錯誤不刪除本地 archive，也不把不完整資料標成已同步。
- 本地 cleanup 是獨立且明確的操作，不跟遠端同步或遠端刪除綁在一起。

---

## 八、實施階段與驗收條件

### 階段 1：確認遠端 item API

確認完整分頁方式、排序、cursor、item ID 穩定性及建立時間欄位。完成後凍結第一版 schema 和同步策略。

### 階段 2：新增本地資料庫

建立獨立的 `sessions/sessions.sqlite3`、schema version、metadata 與 item 儲存 helper；不改動 diagnostics DB。

### 階段 3：建立差異預覽與同步命令

實作本地列表、遠端 metadata 對照、候選確認、分頁下載、每 session 原子提交和失敗重試。

### 階段 4：description 與舊檔遷移

實作當地時間和第一句生成規則；將 `.ai_session.json` title 遷移到空 description，驗證後退役舊檔。

**完成條件：**

- 未變更的 sessions 不下載完整內容；新增與遠端時間變新的 sessions 會列為候選。
- 取消或同步失敗不會破壞先前完整的本地副本。
- description 的時間、第一句與 80 字上限正確，既有 description 不被同步覆蓋。
- 舊 title 可遷移且遷移可安全重跑；驗證成功後不再依賴 `.ai_session.json`。
- diagnostics DB 的 schema 和用途不變，session archive 寫入獨立 DB。

---

## 九、尚待討論

1. 遠端 item 的穩定 ID 與 cursor 語意，決定增量合併或完整替換。
2. `ai-sessions` 的差異預覽是否直接詢問同步，或完全由 `ai-sync-sessions` 負責確認。
3. 是否需要匯出單一 session 為 JSON，供備份或攜帶使用。
4. Description 的第一句分界標點規則，以及當地時區變更後是否維持建立當下的文字。
