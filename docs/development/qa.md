> headless 什麼意思？ (01:33 2026/11/05)

  在計算機領域中，「Headless（無頭模式）」 是一個很經典的術語：
  ### 1. 字面來源
  在電腦硬體術語中，螢幕顯示器與鍵盤被稱為機器的「頭（Head）」。

  - 有頭（Headed）：有接螢幕、有互動操作介面，等著人類用鍵盤輸入。
  - 無頭（Headless）：不接螢幕、沒有終端互動介面，通常在背景默默執行任務（例如機房伺服器、背景批次處理，或是無介面的自動化瀏覽器如 Headless Chrome）。

### 2. 在我們 peforth 裡的具體意義

  在 peforth v2.1.0 裡，正常啟動時（python main.py），Forth 會一路載入詞彙並進入 REPL 互動交談環境，印出 forth>
  並停下來等待您敲鍵盤輸入指令。

  但在以下情況，我們不希望它停下來等鍵盤輸入：

  1. 跑自動化測試時（如 python test_all.py 或 GitHub Actions CI）。
  2. 作為 Python 函式庫被其他程式呼叫時（例如 from peforth import VM，純粹想拿 peforth 當底層運算引擎）。

  如果沒有 headless 機制，自動化測試一執行 dictate("init.f")，程式就會卡在 repl
  迴圈裡等待鍵盤輸入，導致測試程式卡死無法結束。

### 3. 程式碼中的實作

  我們在 peforth.f 裡寫的這段：

    \ --- Launch REPL if not headless ---
    code ?repl
        if not vm.host.get("headless", False):
            yield from vm.call(vm.tick("repl"))
        end-code
    ?repl

- 平常人為使用（預設）：headless 是 False，所以會執行 repl，出現提示字元讓您互動。
- 跑單元測試時：測試程式傳入 VM({"headless": True})，?repl 就會跳過 repl 迴圈，純粹把詞彙庫載入完畢後，把控制權交回給測試腳本進行檢驗。
---# Source checkout, Windows runtime, and WSL runtime	╭─ 👋 user ────────────────────────────────────────────────────────────────────────────────────────╮	  我們有 source code 所在的 subdirectory，然後又有 runtime (Runtime 裡有完整的 source code)，而且 	  runtime 又不只一個，可能有 Windows 的、可能有 WSL 的 runtime。 這三個地方該怎麼稱呼比較好呢？	╰─────────────────────────────────────────────────────────────────────────── 2026-11-19 04:00:36 ──╯	╭─ 🪄 peforth ────────────────────────────────────────────────────────────── OpenAI │ gpt-6-luna ──╮	  我會建議把三者稱為：	  - **Source checkout**（或 **source tree**）：Git 專案原始碼所在的位置，例如 `C:\Users\hcche\Documents\GitHub\peforth`	  - **Windows runtime**：Windows 上實際執行 peforth 的環境與資料位置，例如 `C:\Users\hcche\.peforth`	  - **WSL runtime**：WSL 裡另一套獨立的執行環境與資料位置	  「**repo path**」沒有錯，也很常用，但它指的是「Git repository 的路徑」；「**source path**」則可能被理解成某個原始碼目錄或 Python 的 source path。若要在設定、文件或診斷資訊中清楚區分，我會選 **source checkout path**、**Windows runtime path**、**WSL runtime path**。	  如果要簡短命名，可以用：	  ```text	  source_checkout	  runtime_windows	  runtime_wsl	  ```	  這樣也能避免把 repo 和 runtime 混為一談。	╰─────────────────────────────────────────────────────────────────────────── 2026-11-19 04:00:40 ──╯
