# Project K 簡便自動安裝程式開發計畫

> **目的：** 提供 Windows PowerShell 與 Linux／WSL Ubuntu 各自的一行式安裝入口，自動取得 GitHub 上的 Project K、準備 Python 執行環境，並建立可從任意工作目錄呼叫的 `f` 命令。
>
> **範圍：** 本文件是開發行動計畫；本階段不實作安裝器，也不執行安裝。

## 背景與現況

目前 repo 的 GitHub remote 為 `https://github.com/hcchengithub/project-k.git`。一般使用者指南在 `py/docs/setup.md`，目前要求使用者自行 clone repo、建立 Python 3.10+ venv、安裝 `py/requirements.txt`，再手動建立全域啟動器並設定 PATH。

Project K 程式會以 `repl.py` 所在目錄定位 `base.f`、`auxiliary.f`、`ai.f` 等資源；`ai_bridge.py` 也將 `.env` 與 `.ai_session.json` 放在程式根目錄。因此安裝路徑必須穩定，更新時也必須保護使用者本機設定與 session 資料。

## 建議方案

在 repo 的 `py/` 下提供兩個原生安裝腳本：

- `py/install.ps1`：供 Windows PowerShell 使用。
- `py/install.sh`：供 Linux／WSL Bash 使用。

腳本從 GitHub 取得 Project K，並將程式安裝在各作業系統自己的固定位置；各自建立獨立 venv，安裝 `py/requirements.txt`，建立使用該 venv Python 的 `f` 啟動器。兩邊不可共用 venv、啟動器或安裝目錄。

建議安裝位置：

- Windows 程式：`%LOCALAPPDATA%\ProjectK\app`；venv：`%LOCALAPPDATA%\ProjectK\venv`。
- Linux／WSL 程式：`~/.local/share/project-k/app`；venv：`~/.local/share/project-k/venv`。
- Windows 啟動器：`%USERPROFILE%\.local\bin\f.cmd`。
- Linux／WSL 啟動器：`~/.local/bin/f`。

此位置安排將程式碼與 venv 分開，保留程式資源相對路徑；更新程式碼不需重建 venv，並避免 repo 目錄與使用者工作目錄耦合。由於目前 `.env` 與 `.ai_session.json` 位於 `py/`，實作前必須確認其保留策略：至少確保更新不刪除或覆寫這些未追蹤的本機檔案；若安裝器採用重新建立 app 目錄而非原地更新，則先設計並測試備份／搬移，或調整程式將使用者資料改存於 OS 的使用者資料目錄。不得默默遺失 API key 或 session index。

首次安裝入口預計為：

- PowerShell：`irm https://raw.githubusercontent.com/hcchengithub/project-k/project-k/<branch>/py/install.ps1 | iex`
- Linux／WSL：`curl -fsSL https://raw.githubusercontent.com/hcchengithub/project-k/project-k/<branch>/py/install.sh | bash`

上列 URL 中的 `<branch>` 是佔位符，不可照抄；實作前須查明 GitHub default branch，再決定使用 branch 或正式 release tag。正式文件應提供可直接複製的一行指令。管線安裝代表使用者直接執行網路取得的程式碼，文件須明確列出安裝位置、建立／修改的檔案、前置需求、更新與移除方式，並提供可先下載檢視腳本的方式。

## 行動計畫

### Task 1：確認發布與安裝政策

**目標：** 在寫腳本前，固定安裝器要跟隨的 GitHub 來源、分支與升級規則。

**檢查／決策：**

1. 查詢 `hcchengithub/project-k` 的 default branch 與公開可讀性；不假設分支名稱。
2. 決定初版由 default branch 安裝並以 fast-forward 更新，或只從發布的 tag 安裝。若使用 branch，文件說明這會取得該分支當下版本；若使用 tag，定義版本更新方式。
3. 確認 repo 根目錄與 `py/` 的檔案佈局及安裝腳本 raw URL。
4. 定義最低版本：Python 3.10+、Git、Linux 的 venv 支援；Windows 的 Python Launcher `py` 或可辨識的 Python 3.10+。

**驗收：** 安裝 URL、安裝來源、更新策略、需求版本和錯誤訊息內容都有明確決定。

### Task 2：定義安裝目錄、使用者資料與覆蓋保護

**目標：** 確保首次安裝、重複安裝和更新不破壞本機資料。

**檔案：**
- 規劃文件：`py/docs/簡便自動安裝程式開發計畫.md`
- 可能調整：`py/ai_bridge.py`、`py/docs/setup.md`

**工作：**

1. 確認 `py/.env`、`py/.ai_session.json`、使用者自訂 skill 路徑的讀寫位置及生命週期。
2. 選擇安全更新方式：在安裝目錄內 Git fast-forward 更新，遇到非預期本機修改即停止並保留現場；不可直接刪除後重 clone。
3. 明訂 app、venv、launcher、PATH 設定各自的位置，以及解除安裝時哪些使用者資料預設保留。
4. 失敗時保留既有可用安裝；首次安裝失敗則清除本次建立的部分檔案，但不可清除安裝目錄以外的資料。

**驗收：** 更新、失敗復原及解除安裝均有明確資料保留規則，特別涵蓋 `.env` 與 `.ai_session.json`。

### Task 3：實作 Linux／WSL Bash 安裝器

**目標：** 以 `py/install.sh` 自動完成 Linux／WSL 安裝與更新。

**檔案：**
- 建立：`py/install.sh`
- 測試：`py/tests/installers/` 下的 shell 測試或可重現的測試腳本

**行為要求：**

1. 使用嚴格錯誤處理；偵測 Linux／WSL、`git`、`curl`、`python3` 與 `venv` 模組，缺少需求時提供明確安裝提示，不使用 `sudo` 自動安裝系統套件。
2. 安裝到固定 Linux 使用者目錄；clone／更新時檢查既有安裝狀態，禁止以不安全的刪除重建方式更新。
3. 建立 Python 3.10+ venv，使用該 venv 的 Python／pip 安裝 `py/requirements.txt`。
4. 建立 `~/.local/bin/f`，以絕對路徑執行安裝目錄中的 `py/repl.py`，正確轉送所有命令列參數；不依賴使用者當前目錄或 venv activation。
5. 僅在必要時將 `~/.local/bin` 加入使用者登入 shell 設定；不重複追加、不覆寫整份設定檔，並提示重新開啟 shell。
6. 支援安全重跑；完成後顯示版本／來源、實際安裝位置、PATH 狀態及下一步。

**驗收：** 在乾淨 Linux／WSL 測試環境可安裝；重跑不產生重複 PATH 設定；更新不損壞本機設定；`f` 可從 repo 外的目錄啟動。

### Task 4：實作 Windows PowerShell 安裝器

**目標：** 以 `py/install.ps1` 自動完成 Windows 安裝與更新。

**檔案：**
- 建立：`py/install.ps1`
- 測試：`py/tests/installers/` 下的 PowerShell 測試或可重現的測試腳本

**行為要求：**

1. 驗證 Windows、Git 及 Python 3.10+；優先支援 `py` launcher，也辨識可用的 `python`。缺少需求時說明如何安裝，不靜默下載或執行其他安裝程式。
2. 安裝至固定 `%LOCALAPPDATA%\ProjectK` 子目錄；建立獨立 venv，安裝 `py/requirements.txt`。
3. 建立 `%USERPROFILE%\.local\bin\f.cmd`，以絕對路徑呼叫 venv Python 與 `py\repl.py`，完整保留 `%*` 參數及 Python 的退出碼。
4. 安全更新既有安裝；檢查目錄、Git 狀態及本機資料，遇到不能安全自動處理的狀況應停止並保留現場。
5. 僅在必要時更新使用者 PATH，避免大小寫／尾端分隔符差異造成重複項目；不覆寫其他 PATH 項目，提示重新開啟 PowerShell／CMD。
6. 支援安全重跑並輸出清楚的成功或失敗摘要。

**驗收：** 在 Windows PowerShell 測試環境可安裝；`f.cmd` 可從 repo 外的目錄啟動並正常轉送參數；重跑不重複修改 PATH，且不破壞 `.env`／session 資料。

### Task 5：建立可重現的跨平台安裝測試

**目標：** 驗證首次安裝、重跑、更新與錯誤復原，避免只以腳本語法檢查當作完成。

**檔案：**
- 建立：`py/tests/installers/` 測試案例及測試說明

**測試案例：**

1. Bash 語法檢查（`bash -n py/install.sh`）；可用時執行 ShellCheck。
2. PowerShell parser 語法檢查及 PSScriptAnalyzer（若專案環境可安裝）。
3. 在隔離的 Linux／WSL 使用者目錄測試首次安裝、第二次安裝、更新及網路／需求缺失錯誤。
4. 在 Windows 測試環境測試首次安裝、第二次安裝、更新及 PATH 已存在／不存在兩種情況。
5. 以含空白的測試路徑驗證啟動器 quoting 與參數轉送。
6. 確認從 repo 外目錄啟動仍載入 `base.f`、`auxiliary.f`、`ai.f`；驗證 `.env` 與 `.ai_session.json` 在更新後保留。
7. 確認更新遇到本機修改時會安全停止，不丟棄修改或資料。

**驗收：** 兩平台皆有實際執行記錄；單純 lint／parser 通過不能取代端到端安裝及啟動驗證。

### Task 6：更新一般使用者文件

**目標：** 把目前冗長手動設定改成優先推薦的一行安裝，並保留必要替代說明。

**檔案：**
- 修改：`py/docs/setup.md`
- 視 repo 文件入口需要修改：repo 根目錄使用者指南／README（若存在且有連結到舊 setup 步驟）

**工作：**

1. 開頭提供 Windows PowerShell 與 Linux／WSL Ubuntu 各自可直接複製的安裝命令。
2. 清楚提醒 Windows 與 WSL 要分別安裝、各自執行各自命令，不能共用 venv。
3. 說明安裝前置需求、路徑、PATH 更新後需重開終端機、如何更新、如何解除安裝，以及如何保留／備份使用者資料。
4. 提供先下載並檢視安裝腳本的替代步驟，並說明 `irm | iex` 與 `curl | bash` 會執行遠端程式碼。
5. 將舊版手動方式保留為疑難排解／進階安裝，不讓它與新安裝方式互相矛盾。

**驗收：** 乾淨環境使用者只依對應平台指令與提示即可完成安裝；文件命令中的 owner、repo、branch/tag 與腳本實際發布路徑一致。

## 完成條件

- GitHub 上可取得兩份原生安裝器，PowerShell 與 Bash 流程彼此獨立。
- 兩平台皆建立各自的 Python 3.10+ 環境和全域 `f` 啟動器。
- 從任意工作目錄執行 `f` 均可啟動 REPL 並找到隨附 Forth 資源。
- 安裝器可安全重跑與更新；遇到本機修改或錯誤時不破壞現有安裝及使用者資料。
- 測試涵蓋安裝、啟動、更新、PATH 及本機資料保留；`setup.md` 已改為清楚的雙平台簡易安裝指南。
