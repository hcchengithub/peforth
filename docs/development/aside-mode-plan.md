# `aside` 模式開發計畫書（`--aside` / `with-aside`）

## 1. 背景與設計目的

本設計旨在解決兩個實際使用場景的共同痛點：**「需要借用現有對話上下文來問答，但絕不能污染原 session，也不要產生新的持久化 session 垃圾」**。

1. **Batch 批次自動化重複使用母版 Session**
   - 先預備好一個包含完整背景知識、規則與範例的 `local_<id>` 作為「唯讀母版（template）」。
   - 在 batch 腳本中重複執行：
     ```bash
     peforth -id <session_id> --aside -c "<prompt>"
     ```
   - 每次執行都能帶著母版的上下文回答問題，但結束後**不會**將新 turn 寫回 `<session_id>`，也**不會**在 `ai-sessions` 清單中產生新的 `local_*` 垃圾。

2. **日常對話中的「岔開話題（Aside）」**
   - 在對話進行到一半時，突然想順便問一個跟當下上下文有關（或無關）的旁支問題，但不希望這個岔題與 AI 回覆混進主對話脈絡。
   - 在 Forth 模式或 `/forth` 下使用前綴詞：
     ```forth
     with-aside ai: 這段錯誤訊息的英文怎麼翻比較自然？
     ```
   - 問完後繼續主對話，主線上下文完全不受干擾。

---

## 2. `Subagent` vs. `Aside` 核心差異

| 面向 | `subagent:` / `(subagent)` | `aside`（`--aside` / `with-aside`） |
| :--- | :--- | :--- |
| **初始上下文** | **空白開局**（只有 System Prompt + 本次 Prompt，不讀 `ai_messages`） | **唯讀借用**當前（或 `-id` 載入的）完整 `ai_messages` 副本 |
| **對主對話記憶體的影響** | 不修改 `vm.host["ai_messages"]`（但在工具內呼叫時結果會回傳給父層 AI） | **Immutable Copy**：`copy.deepcopy` 到區域變數執行，從頭到尾不寫入 `vm.host["ai_messages"]` |
| **對原 Session DB 的影響** | 不寫入原 session | 不寫入原 session |
| **Diagnostics DB 紀錄** | `remote_session_id = "subagent_<16-hex>"` | `remote_session_id = "isolated_<16-hex>"`（`metadata_json` 記錄 `kind: "aside"` 與 `aside_from`） |
| **是否出現在 `ai-sessions`** | 否 | 否 |
| **適用場景** | 獨立委派任務（如 `herdr:`、`ai-cleanup:`） | Batch 重複套用母版、日常對話岔開話題 |

---

## 3. 技術實作設計

### 3.1 零風險記憶體隔離（不需「事後還原」）
- 若採用「先改 `vm.host["ai_messages"]`、結束後再還原」的作法，一旦中途發生網路錯誤、Exception 或 Ctrl+C 中斷，記憶體就可能殘留污染。
- 因此 `aside` 模式採用 **Immutable Copy**：
  - 在 `ai_turn_stateless`（`chatlkk_cli` 為 `_chat_turn_loop`）中，當 `aside=True` 時，使用 `copy.deepcopy(vm.host.get("ai_messages") or [...])` 建立區域變數 `messages`，並將本次 user prompt 加入該區域變數後送出請求。
  - 全程不寫回 `vm.host["ai_messages"]`，無論成功或失敗都零污染。

### 3.2 Diagnostics Logging 與事後清理
- 為了保留完整除錯線索（HTTP 請求、tool calls、stdout/stderr、錯誤訊息），`aside` 照常寫入 `ai-diagnostics.sqlite3`。
- `remote_session_id` 使用 `isolated_<16-hex>`，並在 `turns.metadata_json` 標記：
  ```json
  {"kind": "aside", "aside_from": "local_xxx", "model": "...", "provider": "..."}
  ```
- 好處：
  - 出錯時可透過 `ai-diagnostics-query` 查 `isolated_%` 或 `aside_from` 完整還原現場。
  - 日後資料庫瘦身時，可直接依 `remote_session_id LIKE 'isolated_%'` 精準清理，絕不誤傷 `local_%` 主對話。

### 3.3 CLI 與 Forth 介面
1. **CLI 旗標（`repl.f`）**：
   - 新增 `--aside` 旗標，可搭配 `-id <session_id> -c <prompt>`（也可單獨搭配 `-c <prompt>` 做無痕單次提問）。
   - 執行完畢不印出污染性的新 `local_*` ID；若有設定來源 `-id`，可於 stderr 輸出 `ASIDE_FROM=<sid>` 與 `DIAG_SESSION_ID=<isolated_id>` 供 batch 除錯紀錄。
2. **Forth 前綴詞（`ai.f`）**：
   - 新增 `with-aside`（`safe=True`），透過 `vm.host["ai_pending_turn_options"]["aside"] = True` 設定單輪有效（與 `with-model`、`with-reasoning` 同機制），執行後自動重置。

---

## 4. 補充檢視：可能漏掉的細節

1. **`chat>` 模式下的快捷觸發（`/aside` 或 `aside:`）**：
   - `with-aside ai: ...` 在 Forth 模式很順手，但在 `chat>` 模式下若要打 `/forth with-aside ai: ...` 略顯冗長。可考慮一併在 `repl.f` 支援 `/aside <prompt>`（或在 `ai.f` 提供 `aside:` 巨集）。
2. **`peforth` 在 Stateful（Remote `sess_...`）模式下的行為**：
   - 若使用者目前正處於 `ai_active_session_id`（Stateful 模式），執行 `with-aside ai: ...` 時**絕不能**呼叫遠端 Stateful API（否則雲端 session 會被寫入該輪對話）。應改為從本地 SQLite mirror（`sessions.sqlite3`）讀出該 remote session 的歷史訊息轉為臨時 `messages`，改走 Stateless（`/chat/completions`）完成本次 aside 問答。
3. **無 `-id` 時的 `--aside -c "..."`**：
   - 應允許 `--aside` 不帶 `-id` 使用，讓單次腳本查詢也能直接記為 `isolated_*`，避免在 `ai-sessions` 留下一堆 1-turn `local_*` 垃圾。
4. **`with-aside` 不可與 `subagent:` 混用產生誤解**：
   - `subagent:` 本身就是空白開局，若同時加上 `with-aside` 應以空白或明確報錯／忽略處理，並在文件與 help 註解中寫清楚兩者差異。
