# peforth AI Diagnostic Logging 說明書

## 概述

peforth 已提供 AI Diagnostic Logging：將 AI transport、HTTP、SSE streaming、AI turn、工具呼叫、approval 與 Forth execution 的診斷事件及相關內容記錄在 SQLite database，供問題追蹤、除錯與研究使用。這不是待實作的計劃，而是現有功能的使用與資料解讀說明。

**重點：詳細的 AI 活動紀錄是給 AI 分析的資料。** SQLite 保存的內容、關聯 ID 與事件時序十分豐富，直接由人手動查詢不容易；建議將 [AI diagnostics log inspector skill](../skills/ai-diagnostics-log-inspector/SKILL.md) 交給 Agentic AI，讓它協助定位 runtime、turn、還原對話與工具執行過程，進行 debug 或研究。此 skill 已可供其他 Agentic AI 依照指引使用，不限 peforth 內建 AI。

## 1. Database 與執行環境

每個 peforth application process 是一個 **runtime**，具有獨立的 `runtime_id`；每次 AI 對話請求是獨立的 **turn**，具有 `turn_id`。遠端 Agents API session ID 與本機 runtime ID 不同，不能互相取代。

Windows 和 WSL 各有自己的 SQLite database，同一環境的多個 runtime 共用該環境的資料庫，不共用 Windows/WSL live database。

預設位置：

```text
Windows: %USERPROFILE%\.peforth\ai-diagnostics.sqlite3
WSL:     ~/.peforth/ai-diagnostics.sqlite3
```

可用環境變數 `PEFORTH_CONFIG_DIR` 指定設定目錄；資料庫檔名為 `ai-diagnostics.sqlite3`。

SQLite 以 `contents` 保存完整文字、以 `turns` 保存每次 AI turn、以 `timeline` 保存事件時序，並以 `runtimes` 識別執行程序。相同類型且相同內容的文字可透過 hash 去重，但不同 turn 仍保留各自的 occurrence 與時間線。完整內容包括 prompt、instructions、AI output、tool arguments/results 與相關 Forth 執行資料；實際可取得的細節依事件與 logging mode 而異。

## 2. 即時查看：peforth_logging_monitor.py

[peforth_logging_monitor.py](../tools/peforth_logging_monitor.py) 是**唯讀**的終端機即時監視器：輪詢 SQLite `timeline`，以時間、四碼 runtime 簡稱、emoji 和事件摘要顯示活動，連續相同的事件會合併顯示次數。它適合快速觀察 AI request、SSE、工具呼叫、approval 和 Forth execution 的動態，不是完整內容檢索工具。

從 repository 根目錄執行：

```bash
python tools/peforth_logging_monitor.py --help
python tools/peforth_logging_monitor.py
python tools/peforth_logging_monitor.py --interval 1
python tools/peforth_logging_monitor.py --database /path/to/ai-diagnostics.sqlite3
python tools/peforth_logging_monitor.py --runtime-map
```

參數：

| 參數 | 說明 |
| --- | --- |
| `-h, --help` | 顯示完整 CLI 說明 |
| `-d, --database PATH` | 指定要監看的 SQLite database；預設使用上述設定目錄 |
| `-i, --interval SECONDS` | 輪詢間隔，預設 `0.5` 秒，必須大於 0 |
| `--runtime-map` | 列出四碼 runtime 簡稱與完整 UUID，然後結束 |

監視器啟動時會讀取目前資料庫的既有事件，再持續顯示新事件；按 **Ctrl-C** 結束。資料庫必須存在且可讀取。它使用 read-only SQLite connection，不修改 logging 資料。

## 3. 讓 Agentic AI 分析：ai-diagnostics-log-inspector

專案提供 [`skills/ai-diagnostics-log-inspector/`](../skills/ai-diagnostics-log-inspector/)；核心指引在 [SKILL.md](../skills/ai-diagnostics-log-inspector/SKILL.md)。讓支援讀取 skill 與執行本機命令的 Agentic AI 先閱讀該 skill，再告訴它要檢查的 Windows 或 WSL database、runtime 或問題現象。

例如：

> 請先閱讀 peforth 的 `skills/ai-diagnostics-log-inspector/SKILL.md`，以唯讀方式檢查指定的 AI diagnostic SQLite database，找出最近一次失敗的 AI turn，還原 prompt、agent output、tool calls、approval 與相關事件時序，並分析可能原因。請明確標示所查詢的 host、database、runtime_id 與 turn_id。

skill 指導 AI 區分**執行分析的環境**與**資料庫所在的環境**：WSL 上的 Agent 也可能要讀 Windows database，不能擅自改讀自己的預設資料庫。對仍在使用中的 Windows SQLite/WAL，優先使用 Windows-native reader，避免直接透過 WSL `/mnt/` 掛載路徑讀取造成 I/O 問題。分析時應保持唯讀，不修改、checkpoint 或刪除資料庫與 WAL 檔。

## 4. 深入查詢：ai_diagnostics.py

[tools/ai_diagnostics.py](../tools/ai_diagnostics.py) 提供進一步的唯讀診斷查詢。使用時先看 `--help`，再依 skill 的指引選擇 runtime 與 turn：

```bash
python tools/ai_diagnostics.py /path/to/ai-diagnostics.sqlite3 list-runtimes
python tools/ai_diagnostics.py /path/to/ai-diagnostics.sqlite3 runtime-timeline <runtime_id>
python tools/ai_diagnostics.py /path/to/ai-diagnostics.sqlite3 turn-timeline <turn_id>
python tools/ai_diagnostics.py /path/to/ai-diagnostics.sqlite3 show-turn <turn_id>
python tools/ai_diagnostics.py /path/to/ai-diagnostics.sqlite3 export-turn <turn_id>
```

`show-turn` 適合還原單次對話的 user prompt 與 agent output；`export-turn` 可提供更完整的事件資料，但輸出可能很大。AI 也可以追蹤 `contents` 的 content ID，分析重複 instructions、工具參數、stdout/stderr 等。注意區分**整個 database 的 content 筆數**與**某個 turn 引用的 content 筆數**，避免統計混淆。

## 5. 記錄的資訊與常見除錯方向

- **Runtime / turn：** 執行環境、process、啟停、session/turn 關聯、成功或失敗狀態。
- **HTTP / SSE：** request/response、狀態碼、串流事件、耗時、stream failure 與 timeout 的前後事件。
- **AI 對話：** prompt、instructions、完成的 output，以及失敗時已保存的 partial output（若有）。
- **工具與核准：** tool call、arguments、result、approval decision 及相關時序。
- **Forth：** 執行事件及已記錄的 source、stdout/stderr 等診斷內容。

常見分析包括：追查 SSE read timeout 前最後收到的事件；比較 `requires_action` 與後續 `in_progress` 回應；還原 AI 使用哪些工具、是否獲得 approval、工具執行結果如何；或比較多個 runtime、turn 中重複出現的 instructions。

SQLite 記錄可供深入研究，但不表示每次異常都必然有完整資料：程序被強制終止、尚未寫入的事件或 logging 自身失敗，仍可能造成最後部分紀錄缺失。診斷時應區分已保存的事實與推測。

## 6. 使用建議

**人看即時動態，用 Monitor；AI 查完整歷史，用 Skill 搭配 SQLite 查詢工具。**

Monitor 適合快速觀察「現在發生什麼」；需要回答「為什麼失敗、AI 當時說了什麼、呼叫了什麼工具、經過哪些事件」，就讓 Agentic AI 依 `ai-diagnostics-log-inspector` 分析資料庫。這也是 peforth Diagnostic Logging 的核心價值：把原本難以人工追查的 AI 活動，轉為可被 AI 系統化閱讀與研究的證據。
