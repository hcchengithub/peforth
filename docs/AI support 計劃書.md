# peforth v2 AI 支援計劃書

> 狀態：已依使用者回覆定案，開始實作  
> 日期：2026-10-08  
> 適用範圍：peforth v2 Python package

## 1. 目的

在 peforth 的 Forth CLI 中加入 `ai:` 指令，讓使用者以自然語言與 AI 討論問題並請求協助。AI 能理解 peforth 的 Forth 慣例，提出操作，透過本機工具呼叫目前的 VM，並依實際結果繼續工作。資料堆疊介面使用 `(ai)`，保留 `ai` 名稱。

第一階段目標：提出需求 → AI 理解 Forth → 提出操作 → 使用者確認 → CLI 執行 → AI 根據結果繼續。

## 2. 設計原則

peforth 已將微核心、Forth 擴充字典與 Python Host 分開。AI 擴充沿用這種分工：Forth 使用者介面放在 `peforth/ai.f`，API 與工具交握由 Python Host 處理；保留 `peforth/projectk.py` 共用 kernel。

AI 以 Agents API session 保存多輪對話；AI 學習 peforth 的 Forth 規則則用 Agent Skills 表達。本機檔案、Forth VM 與操作結果只透過明確定義的工具提供。

## 3. 使用者介面草案

ai: 取用本行剩餘文字作為問題，顯示 AI 回覆。同一 CLI 對話沿用相同 session。

    ai: 說明這個系統的 stack 與 dictionary 如何運作
    ai: 幫我定義一個 square，然後驗證 12 的平方

(ai) 從 Forth data stack 取出提示，將回覆放回 stack，供其他 words 使用。  <-- hc: 你本來想用 'ai'，但是我覺得我想把 'ai' 保留下來，所以給它戴了耳機變成 (ai)

    s" 請給我一句簡短的歡迎詞" (ai) . cr   <-- hc: 我給這個命令戴了耳機

控制 words 為 ai-new（開新 session）、ai-status（查看狀態）、ai-cancel（取消目前 turn）。

## 4. Agents API、Skills 與對話保存

使用 OpenAI Agents API。由於使用者希望 AI 能按需讀取較完整的 Forth 使用規則，採用官方 Agent Skills 格式建立 peforth Forth skill，內容以 SKILL.md 描述 Forth 慣例、dictionary 查詢方式、程式執行工具及其使用限制，並可附上精選手冊參考資料。

Agents API 的 Skills 需要把 skill 提供給 agent 的執行環境。初步建議在 OpenAI-hosted session 中以 Agents Plugin ZIP 傳入內含 skill 的小型 plugin；agent 依 skill 指引呼叫本機 function tools 操作 peforth。這不會把使用者的本機 Forth VM 搬進雲端；本機 VM 操作仍由 CLI 的工具處理。須依 Agents Plugin 文件確認 session 建立欄位及工具組態。

若希望 agent 只保有 Forth 知識、完全沒有 hosted shell，則需評估 self-hosted sandbox 與 executor；這比第一版預期增加本機 executor、連線和生命週期管理。故第一版優先採 hosted skill plugin 加受限的本機 function tools，明確要求 agent 只透過 Forth tools 操作 peforth。

Agents API 會保存 session 狀態。本機 session index 位於 `~/.peforth/.ai_session.json`（可由 `PEFORTH_CONFIG_DIR` 指定）；目前每個 `f` process 的 active session selection 留在該 VM 記憶體中，不會自動恢復本機 VM 的 stack、dictionary 或檔案。session 操作與清除方式記錄於 `docs/ai.md`。

官方參考：[Agents API 概觀](https://developers.openai.com/api/docs/guides/agents-api/overview)、[Sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions)、[Skills](https://developers.openai.com/api/docs/guides/tools-skills)、[Agents API Plugins](https://developers.openai.com/api/docs/guides/agents-api/tools/plugins)、[Agents API hosted files](https://developers.openai.com/api/docs/guides/agents-api/environments/files)。

## 5. 本機工具與確認方式

第一版先提供兩種 function tools：

1. **查詢 Forth dictionary**：依名稱或關鍵字，取得目前 VM 的 words 說明和定義，使 AI 能看到實際可用的 Forth 擴充。
2. **執行 Forth 程式**：將 AI 提出的 Forth 送給目前 VM，回傳實際輸出或錯誤供 AI 後續判斷。

第一版每次執行 AI 提出的 Forth 程式前，都在 CLI 顯示完整程式並要求使用者確認。拒絕後回傳拒絕結果，讓 AI 可改提其他方案。獲准的程式使用 VM 既有能力，其中可能包括 Python Host Bridge，因而能讀寫檔案或執行系統工作；確認畫面要清楚呈現將執行的 Forth。

AI 的請求、function tool 呼叫與工具回覆都透過 Agents API session events 傳遞；CLI 負責工具實際執行及使用者確認。

## 6. REPL 與 Task 調度

AI 等待本機執行確認期間，使用者輸入的其他 Forth 命令先排隊，待目前 AI Task 結束後依序處理。Agents API 網路等待目前由 REPL 同步處理，尚不能在該期間接收新輸入；後續可改為非同步事件工作者以支援完整等待期間的佇列。不在第一版交錯執行 AI 工作與一般 Forth 工作，降低共享 data stack、dictionary 與 VM 的狀態混淆。

CLI 以 peforth Task continuation 配合 Agents API 事件處理長時間等待；網路工作和 VM 指令執行分開處理，所有 Forth tools 都在 REPL 主執行緒中執行。實作需定義按 Ctrl-C 或 ai-cancel 時，如何取消遠端 turn、結束目前 Task 並恢復命令佇列。

## 7. 設定與金鑰

由 Python 標準函式庫直接呼叫 Agents API，不增加 SDK 依賴。載入 repo 根目錄的 .env，並支援使用作業系統環境變數。設定項目為：

- OPENAI_API_KEY：Platform API key。
- PEFORTH_AI_MODEL：預設模型名稱；由環境變數設定，不把易變模型名稱寫死在 Forth 字典。

若使用 .env，repo 提供不含實際 key 的 .env.example，並將 .env 加入 .gitignore。環境變數中已存在的值優先，不被檔案值覆蓋。啟動 AI 功能時若沒有 key，顯示清楚的設定指引；不影響一般 Forth 使用。

已提供 API key（請勿將 key 或私人設定提交到 Git）。 

API key 僅用於本機 Host 向 OpenAI API 驗證，不放入 skill、plugin ZIP、function tool 結果或 agent 指令。Agents API session 將對話送至 OpenAI 服務；使用者需留意平台資料保存與資料區域政策。

## 8. 檔案分工草案

| 檔案 | 預計職責 |
| --- | --- |
| `peforth/ai.f` | 使用者可見的 Forth words、stack effect、session 操作、turn flow、工具交握與本機核准流程 |
| `peforth/ai_bridge.py` | 標準函式庫 HTTP/SSE、API 傳輸、session index 檔案、skill 載入及本機 Forth 輸出擷取等基礎功能 |
| `skills/peforth-forth/SKILL.md` | AI 使用 Forth、查詢字典與提交程式的技能說明 |
| `skills/peforth-forth/references/` | Forth 操作與語言說明 |
| `plugins/peforth-forth/.codex-plugin/plugin.json` | Agent Plugin 描述；隨 source 提供，不自動全域部署 |
| `peforth/repl.py` | REPL 與 f CLI |
| `docs/ai.md` | 設定、使用、權限、session 保存與故障處理 |

skill/plugin 內容應由 repo 中審閱過的 peforth 文件維護，不讓模型任意載入未檢查的 skills。

## 9. 分階段交付

### 第一階段：Forth skill 與 API 對話

建立 peforth Forth Agent Skill/plugin，採標準函式庫呼叫 Agents API，提供 ai:、(ai)、雲端 session ID 保存、模型環境變數及 .env 設定。

### 第二階段：本機 Forth 工具循環

提供 dictionary 查詢和 Forth 執行 function tools。AI 執行前每次確認；CLI 把真實輸出或錯誤回傳，使 AI 能據此續答。

### 第三階段：排隊、取消與恢復

完成 AI Task 期間的 REPL 命令排隊、取消、session 續接和錯誤恢復文件。視需求擴充更多受控的本機工具。

## 10. 驗收條件草案

- ai: 能送出問題、串流顯示回覆，並在相同 session 延續對話。
- `ai-sessions` 可刷新本機標題索引；active session 僅在目前 `f` VM 內，除非明確執行 `ai-use`，新 process 不會自動續接。
- Agents API 能發現 peforth Forth skill，並按需參考 Forth 說明。
- AI 能查詢目前 dictionary；提交的 Forth 程式每次先顯示並取得使用者確認。
- 獲准執行後，程式在本機 VM 執行，實際輸出或錯誤返回 AI。
- AI Task 進行期間的新 REPL 命令排隊，Task 結束後依序執行。
- .env 設定、環境變數優先順序、金鑰排除 Git、取消及 API 錯誤都有明確行為。
- 不安裝 OpenAI SDK；一般 Forth 在沒有 API key 時仍可使用。

## 11. 已確認的實作決定

1. 已確認使用 OpenAI Agents API 提供雲端 session；Forth 執行留在本機 VM，並經 CLI 核准流程執行。新 session 使用 `environment.type: none`，不建立 hosted sandbox。

2. 使用者設定與 session index 預設放在 `~/.peforth`（可由 `PEFORTH_CONFIG_DIR` 指定），與 source checkout 分離；模型環境變數為 `PEFORTH_AI_MODEL`。
	--> 已改採 peforth repo 根目錄套件佈局；Windows 與 WSL 使用各自 checkout。
	
3. Forth skill 根目錄可由 `PEFORTH_AI_SKILLS_DIR` 環境變數指定，預設為 checkout 的 `skills`。docs、skills、plugins 隨 source 提供，不會自動部署到其他 AI CLI 全域目錄。
	--> 已實作 `PEFORTH_AI_SKILLS_DIR`，預設值為 checkout 的 `skills`。

本文件記錄已確認的 AI 設計及目前實作狀態；v2 package/CLI 實作以 source code、`docs/ai.md` 和測試為準。
