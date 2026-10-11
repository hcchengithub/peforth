# peforth v2 遷移與安裝計畫

> **目的：** 在 `peforth` repository 建立一條與 peforth v1 無共同 Git 歷史的 `v2-migration` orphan branch，從 Project K `v2-migration` 的 Python Edition 建立 peforth v2。v2 幾乎重新開始，以共用 Forth Kernel、AI-first REPL 和可安裝的 `f` 命令為核心，不承接 v1.33 的舊產品功能。
>
> **安裝方向：** 將 v2 做成 Python CLI package，優先以 `pipx` 安裝，也支援在使用者指定的 Python venv 中以 `pip` 安裝。Windows PowerShell 與 Ubuntu／WSL 各自在自己的 Python 環境安裝；初期不另寫兩份自訂安裝器，除非實測發現套件安裝方式無法滿足需求。
>
> **狀態：** 本文件是待審閱計畫。尚未重建 orphan branch、搬移程式、刪除舊 branch、發布套件或執行安裝。

## 1. 已確認的方向

### v1 與 v2 的界線

- peforth v1.33 已封存；需要 v1 的使用者仍可安裝既有 v1.33。
- v2 的工作樹不保留 v1 的程式、文件、產品結構或相容性負擔。v1 的歷史已由現有 tag/branch 保存，v2 不承接那段 Git 歷史。
- v2 使用 orphan branch；v2 初始 commit 不以 v1 commit 為祖先。保留 v1 tag 不等於把 v1 檔案或歷史帶進 v2 的 commit lineage。
- v2 以 Project K 的共用 `projectk.py` Kernel 為基礎，沿用其共用 Kernel 的設計精神；面向使用者的產品和命令名稱是 peforth v2 / `f`。
- v2 不遷移 v1 debugger、Jupyter magic/kernel、`peforth.ok()` 舊 API 或其他舊產品功能。想使用這些舊功能的使用者可安裝 v1.33。

### Repository 與來源

- 目標 repository：`https://github.com/hcchengithub/peforth.git`
- 目標工作 branch 名稱：`v2-migration`。目前本機同名 branch 是從 v1.33 commit 建立的普通 branch；遷移前須安全換成 orphan branch。
- 程式來源：`https://github.com/hcchengithub/project-k.git` 的 `v2-migration` branch，主要內容在 `py/`。
- 搬移時記錄實際採用的 Project K commit SHA。只搬核准的檔案快照，不合併兩個 repository 的 Git 歷史。
- Project K 工作樹曾有未提交的 `log.txt` 修改；預設不搬，除非使用者另行明確指定。

## 2. v2 檔案範圍

### 從舊 peforth v2 branch 工作樹移除

建立乾淨的 orphan tree 時，不帶入舊 peforth 的下列產品檔案／目錄：

- `/build`
- `/notebook`
- `/peforth`
- `/peforth.egg-info`
- `/playground`
- `.gitattributes`
- `.gitignore`
- `LICENSE`
- `README.md`
- `README.rst`
- `setup.bat`
- `setup.py`

這些是舊版工作樹內容的移除，不代表 v2 不需要相應的新檔案：

- 建立新的 `.gitignore`，忽略 Python cache、venv、build/dist/egg-info、`.env`、API key、session/user state 等。
- 建立新的 README/安裝與使用文件，清楚介紹 peforth v2 的 AI-first `f` 命令。
- 以 `pyproject.toml` 和選定 build backend 建立新 package metadata，取代舊 `setup.py`。
- 新增 v2 的 LICENSE；授權文字及 attribution 須先由使用者確認，不能未確認就沿用或發布。
- 不搬入舊 notebook/playground；若日後確有 v2 教學內容需要，再另行建立。

### 從 Project K `py/` 選擇性搬入

**預計納入核心：**

- `projectk.py`：共用 Forth Kernel，保留此核心模組及其設計精神。
- `repl.py`、`ai_bridge.py`、`ai_tools.py`。
- `base.f`、`auxiliary.f`、`ai.f` 等 runtime 所需 Forth 資源。
- `requirements.txt` 中確認需要的 runtime dependency，以及可移植到 v2 的測試。

**逐項判斷後才納入：**

- `docs/`：只挑選核心語意、AI、使用方式等有助於 v2 的文件；改寫產品名稱、路徑和連結。歷史對話、暫停紀錄、舊計畫書和不適用文件不作為一般使用者文件直接複製。
- `skills/`、`plugins/`：確認是開發輔助、可選整合還是 runtime 功能；不預設它們必須隨 package 安裝。
- `verify_projectk.py`：保留並調整共用 Kernel 的有效測試。
- PDF、對話記錄或其他大型附件：不自動帶入，先判斷是否有 v2 使用價值。

**明確排除：**

- `.env`、`.ai_session.json`、任何 API key/token/secret。
- `__pycache__`、暫存檔、測試產物、build/cache/egg-info。
- Project K 未提交的 `log.txt` 修改及任何未核准的工作樹變更。

## 3. Package、命令與使用者資料設計

### Python package 與 `f` 命令

- distribution 名稱使用 `peforth`；新 Python import package 使用 `peforth`。
- 將共用 `projectk.py`、REPL、AI 模組和 Forth 資源收進合理的 package 佈局。`projectk.py` 代表共用 Kernel，不做無差別全域改名。
- 在 `pyproject.toml` 設定 build metadata 和 console script entry point，建立命令 `f`。實際 entry point module/function 依搬移後程式結構決定。
- 確保 `f` 從任何目前工作目錄都可啟動，Forth 資源可從安裝後的 package 位置載入，而不依賴 repo checkout 或 site-packages 可寫。
- v2 不以維持 v1 的 `import peforth` 行為或相容 API 為目標；只提供 v2 自身需要的 Python package API。

### API key、設定與 session state

Project K 目前把 `.env`、`.ai_session.json` 放在 source root；這不適合作為 pipx/site-packages 的可寫位置。遷移時：

1. 將 API key 設定、session index、使用者設定及自訂 skills/state 放到明確的使用者可寫位置，或提供穩定的環境變數覆寫方式。
2. 確認 Windows 和 Linux/WSL 各自的使用者資料路徑；不可混用不同作業系統的 Python 環境或狀態路徑。
3. 提供不含秘密的設定範例；任何真實 `.env`、session state 和 secrets 都不得進 package、wheel、sdist 或 Git。
4. 不要求 site-packages 可寫，也不覆蓋使用者資料。

### `pipx` 與 `pip`

- 一般 CLI 使用者優先推薦 `pipx`：隔離建立 Python 環境並暴露 `f` 命令。
- 進階使用者可在自己選定的 venv 用 `python -m pip install`；說明 `f` 只會裝在該環境的 Scripts/bin，需確保該目錄在 PATH。
- Windows PowerShell 和 Ubuntu/WSL 必須各自安裝一次。
- 初期可用 GitHub VCS URL 安裝測試版；正式指令必須固定到已測試的 v2 tag，不指向移動中的 branch。PyPI 發布不列為初版必要條件。
- 若 pipx 在任一支援平台無法滿足安裝需求，先用實測描述缺口，再決定是否補自訂包裝器；不要預先多維護兩份 installer。

## 4. 遷移行動計畫

### Phase 0：保存計畫並安全重建 orphan branch

**目標：** 把現有 `v2-migration` 換成真正的 orphan branch，安全保留本計畫，不帶入 v1 commit lineage。

1. 確認 peforth 目前 branch、HEAD、working tree、`v1.33-final`、remote URL，並確認 GitHub 上沒有同名遠端 `v2-migration` branch。
2. 確認 `docs/v2-migration-plan.md` 是最新完整版本；先保存其內容與校驗值，避免 branch 操作遺失未追蹤文件。
3. 建立暫用名稱的 orphan branch。將核准的遷移計畫放進 orphan tree 作為計畫文件；建立首個 v2 planning commit 後，驗證此 commit 沒有 v1 ancestor，且計畫文件內容一致。
4. 驗證新 orphan branch 與計畫文件完整後，才移除舊的本機普通 `v2-migration` branch ref，並將 orphan branch 改為 `v2-migration`。
5. 若任何檢查失敗，停止並保留舊 branch/計畫文件；不以 `-D` 或清空工作目錄強行繼續。
6. 本階段只改本機 branch/commit；不 push、不刪遠端 refs、不改 GitHub default branch。

**驗收：** 本機 `v2-migration` 有獨立的新歷史，首個 commit 不以 v1 為祖先；計畫文件存在且完整；v1 tag/branch 未更動；遠端未變。

### Phase 1：確認 Project K 來源快照和搬移 manifest

**目標：** 確定實際搬移來源與每個檔案的處理方式。

1. 檢查 Project K `v2-migration` branch 的 HEAD、已提交/未提交變更與檔案狀態，選定並記錄來源 commit SHA。
2. 預設不帶入未提交的 `log.txt`；其他未提交變更也一律排除，除非使用者逐項核准。
3. 建立 `納入／改寫後納入／排除` 檔案 manifest，套用上述核心範圍與排除規則。
4. 查明來源 LICENSE 和 peforth v2 的授權/attribution，取得使用者確認後才加入 LICENSE。

**驗收：** 有可審查的來源 SHA 與檔案 manifest；敏感資料、暫存物和未核准工作樹修改不會混入。

### Phase 2：建立全新的 peforth v2 package 骨架

**目標：** 在 orphan tree 建立乾淨、可建置的 v2 專案，不帶舊產品目錄。

1. 建立新的 `pyproject.toml`、`peforth` package、版本 metadata 與 build 設定；不沿用舊 `setup.py`。
2. 建立新的 `.gitignore`、README、安裝文件和已核准的 LICENSE。
3. 設定 Python 支援版本、runtime dependencies、distribution metadata、`f` console script entry point。
4. 加入最小 package/build smoke test。

**驗收：** 乾淨環境可建置骨架；安裝後 `f` 的 smoke command 可執行；新版 metadata 和文件齊全。

### Phase 3：搬入共用 Kernel、AI REPL 與 Forth 資源

**目標：** 將核准的 Project K 程式整合為 peforth v2，同時保留共用 Kernel 精神。

1. 搬入 `projectk.py`、核准的 REPL/AI 模組和 Forth runtime 資源；按 package 結構調整 import。
2. 將 Forth 資源包進 distribution，從安裝後位置可靠載入。
3. 完成 `f` entry point，驗證互動/非互動輸入、參數、stdin/stdout、退出碼及 repo 外 cwd。
4. 將使用者可見的 Project K 名稱和舊路徑改成 peforth v2；保留核心模組識別、API protocol 名稱、必要 attribution，不做盲目全域取代。
5. 將 API key、session index、自訂設定移至使用者可寫位置；不把狀態寫進 package 目錄。
6. 只納入核准的 v2 文件和測試；不帶入 peforth v1 debugger/Jupyter/舊 API。

**驗收：** source tree 和安裝後皆可啟動 `f`；共用 Kernel、AI/Forth 功能與 package resource 正常；repo 外工作目錄仍能使用。

### Phase 4：驗證 package build 和 Windows/Ubuntu 安裝

**目標：** 實證 `pipx`/`pip` 可達成使用者要的全域 `f` 體驗。

1. 建置 wheel/sdist，檢查包含必要模組與 Forth 資源，不包含 secrets、session、cache 或 build 環境產物。
2. 在乾淨 Ubuntu/WSL 環境，以 pipx 從固定測試 tag 安裝；測 `f` 在 repo 外目錄啟動、更新和解除安裝指引。
3. 在乾淨 Windows PowerShell 環境執行相同測試，檢查命令 wrapper、含空白路徑、互動輸入輸出和退出碼。
4. 在使用者指定的 venv 另測 `pip` 安裝，驗證 `f` 所在 Scripts/bin 與 PATH 說明。
5. 測試 API key 缺失時的錯誤提示，以及設定/session 資料在升級後不被覆寫。
6. 加入可重現測試與 Windows/Linux package build/install smoke CI。

**驗收：** 兩平台各自從乾淨環境完成安裝、啟動、資源載入與設定路徑測試；`pipx` 和 `pip` 的適用情境清楚。

### Phase 5：完成使用者文件與發布準備

**目標：** 將 v2 作為新的 major version 發布，讓需要 v1 的使用者仍能取得 v1.33。

1. 撰寫全新 README、AI/REPL 指南、Windows 和 Ubuntu/WSL 安裝說明、設定與解除安裝說明。
2. 安裝命令固定到已測試的 v2 tag，不指向開發 branch。
3. 初版可先使用 GitHub 固定 tag/VCS 安裝；PyPI 發布待後續另行決定，不是本次遷移的前置條件。
4. 通過測試與使用者審閱後，才確認 v2 tag/release、是否切換 GitHub default branch。這些遠端操作屆時逐項確認。
5. 驗證 v2 branch 無 v1 ancestry；v1.33 tag 仍可用，但不屬於 v2 runtime/package 的相容範圍。

**驗收：** 新手依文件可在 Windows 或 Ubuntu/WSL 安裝並使用 `f`；發布指向已測試的 commit；v1.33 仍可單獨安裝。

## 5. 需要使用者協助的決策

進入搬移程式前，只需要使用者確認以下事項：

1. **授權決定：** 是否核准 peforth v2 採用 Project K 的 MIT 授權，並在新 LICENSE 中保留正確 copyright/attribution？建議採用來源專案實際授權並明確標註，但須由專案擁有者確認。
2. **核准 Phase 0/1：** 是否同意我先在本機安全重建 orphan `v2-migration`、保存本計畫作為 orphan branch 的首個 planning commit，然後唯讀檢查 Project K 來源 SHA 和檔案 manifest？這不會 push、刪除 GitHub 遠端 branch/tag 或更改 default branch。
3. **Project K 未提交變更：** 預設排除目前已知的 `log.txt` 修改及所有其他未提交/未追蹤狀態；如需納入，請指出具體檔案和內容。否則不需使用者手動處理。

使用者目前不需要執行安裝命令、手動搬檔或提供 PyPI credentials。PyPI 是否發布可等 package 及 GitHub tag 路線驗證後再決定。

## 6. 技術參考

- Python Packaging User Guide：console script entry points — https://packaging.python.org/en/latest/specifications/entry-points/
- Python Packaging User Guide：CLI packaging — https://packaging.python.org/en/latest/guides/creating-command-line-tools/
- pip VCS installs — https://pip.pypa.io/en/stable/topics/vcs-support/
- pipx — https://pipx.pypa.io/stable/
