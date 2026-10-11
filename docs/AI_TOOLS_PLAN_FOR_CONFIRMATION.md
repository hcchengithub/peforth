# Project K AI tools 實作記錄

## 目標

提供六個由 AI 查詢並使用的 Forth words：system_info、run_pwsh、run_bash、run_curl、run_http、stringify，支援 Windows PowerShell 7 與 WSL2 Ubuntu，也支援 Linux／WSL 主機。

Words 的 stack 操作、輸入檢查與主機命令組裝定義在 `ai.f`。`ai_tools.py` 只保留 Python 專屬的程序啟動、主機偵測與 HTTP 傳輸 helper，由 `ai.f` 的 `code` words 匯入呼叫。

## AI 如何使用這些 words

這些 words 不會各自註冊成 Agents API 的獨立 function schema。AI 透過現有的字典搜尋工具讀取 word 名稱、stack signature、help 與說明，再組成 Forth 程式，交由既有的 Forth 執行工具提出執行。該工具仍要求使用者明確核准。

複合 Python 值可由 Python bridge 放到 Forth stack，例如 curl 的字串參數清單或 HTTP request mapping。各 word 的 stack signature 和 help 是 AI 判斷輸入格式的依據。

## Words 與介面

### system_info

Signature: ( -- info )

首次呼叫時偵測並回傳 mapping，並把結果快取在該 word object 的 properties；快取維持於目前 VM 的生命週期。包含 OS、Python 執行檔與版本、虛擬環境是否啟用及其路徑、WSL 狀態與 distro，以及 pwsh、bash、curl 的可用狀態、路徑與版本。VM 重啟後重新偵測。

### run_pwsh

Signature: ( script-string -- result )

執行當前環境可用的 PowerShell 7（pwsh）。不自動改用 Windows PowerShell 5.1。回傳 mapping，包含 exit_code、stdout、stderr、timed_out、truncated；發生啟動錯誤或逾時時也包含 error。逾時上限 60 秒，每個輸出串流最多保留 64 KiB。

### run_bash

Signature: ( script-string -- result )

Linux／WSL 主機使用本機 Bash；Windows 主機透過 wsl.exe 在指定的 Ubuntu distro 執行 Bash。distro 可由 PROJECTK_WSL_DISTRO 指定，預設 Ubuntu。回傳格式與 run_pwsh 相同。

### run_curl

Signature: ( argument-list -- result )

argument-list 是字串清單，必須包含 URL。直接以 argv 呼叫 curl.exe 或 curl，不經 shell。回傳格式與 run_pwsh 相同。

### run_http

Signature: ( request-mapping -- response )

使用 Python 標準函式庫 urllib.request 發出 HTTP/HTTPS request，不啟動 shell 或額外 Python 程序。mapping 欄位：url（必要）、method（預設 GET）、headers（字串對字串 mapping，選填）、body（選填字串）。成功及 HTTP 錯誤狀態都回傳 status_code、headers、body、truncated；連線或輸入錯誤回傳 error。逾時上限 30 秒，最多讀取 64 KiB response body，沿用標準 TLS 憑證驗證。

## 跨平台與執行行為

- system_info 提供目前環境資訊，讓 AI 判斷 shell 與 Python venv 狀態。
- 每個 shell/curl 呼叫啟動子程序，沿用 Project K 程序的工作目錄及環境；子程序變更不會改動父 REPL 的工作目錄或環境變數。
- run_http 使用 Python 標準函式庫的網路、代理與憑證設定。
- 執行 shell、curl、HTTP request 都可能造成外部或本機副作用；AI 提出的 Forth 程式仍經使用者核准後才執行。

## 完成狀態

- [x] 在每個 Forth word object 加入 properties mapping，供 word 專屬快取使用。
- [x] 新增六個 AI-facing words，並以 help/comment 提供 stack signature 和輸入說明。
- [x] 由 Python 安裝系統、shell 與 HTTP host words；`stringify` 直接以 `auxiliary.f` 的 `code` 定義。
- [x] system_info 包含目前 Python venv 狀態與路徑，並在同一 VM 內快取。
- [x] 維持既有 AI Forth 執行核准流程。
- [x] 更新 Project K Forth AI 參考文件。
- [ ] 依需求執行測試或目標環境的實際 smoke check。

- [x] 在 `auxiliary.f` 直接定義 `stringify`，輸出縮排 JSON；字串會解析 JSON/Python literal，其他巢狀物件以 repr 表示。
