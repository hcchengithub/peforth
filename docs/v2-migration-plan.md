# peforth v2 遷移與安裝計畫

> **目標：** 在 peforth repository 的 `v2-migration-orphan-bootstrap` orphan branch 上，以 Project K `v2-migration` branch 的 Python Edition 建立 peforth v2。v2 是以共用 Forth Kernel、AI-first REPL 和自帶 AI 的 `f` 命令為核心的大幅重整；不承接 v1.33 的舊功能或 Git 歷史。
>
> **安裝與開發原則：** Windows 與 Ubuntu／WSL 各自在使用者家目錄維護可寫的 peforth source checkout：Windows `%USERPROFILE%\.peforth`，Ubuntu／WSL `~/.peforth`。`docs/`、`skills/`、`plugins/` 跟著 source 一起放在 checkout 中。安裝後的 `f` 必須執行這份 checkout 的程式，讓使用者可在該目錄自行修改、測試及 commit。
>
> **狀態：** 本計畫已依 `hc:` 審閱意見修訂，待再次審閱。尚未搬移 Project K 程式、建立安裝流程或對 GitHub 遠端發布。

## 1. 已定案的產品與歷史方向

- peforth v1.33 已封存；需要舊功能的使用者仍可安裝 v1.33。
- v2 不保留 v1 程式、文件、產品目錄或相容性負擔；v2 的 Git history 也不承接 v1 commit。舊版 tag/branch 留在 repository，供取得舊版使用，不代表 v2 有 v1 ancestry。
- v2 已在本機建立為 orphan history。目前接受的工作 branch 名稱是 `v2-migration-orphan-bootstrap`，不必為了命名而改名。其首個 planning commit 為 `0cc00f8`，只含計畫文件；原本從 v1 建立的本機 `v2-migration` branch 已刪除。尚未 push 遠端。
- Project K 的 `projectk.py` 是共用 Forth Kernel；搬入 v2 後仍保留其共用 Kernel 的原意和模組角色，不做盲目全域改名。
- v2 著重 AI-first 的 `f` command，不搬遷 v1 debugger、Jupyter magic/kernel、`peforth.ok()` 或其他舊功能。這是重大不相容變更，必須在 README、安裝入口和 release notes 明確通知使用者。
- distribution/產品名稱為 `peforth`，主要命令為 `f`。Project K 的使用者可見產品名稱、設定與文件路徑應改為 peforth v2；保留必要的核心技術名稱、來源 attribution 和 API protocol 名稱。
- 目標 repo：`https://github.com/hcchengithub/peforth.git`。Project K 來源 repo：`https://github.com/hcchengithub/project-k.git`，branch `v2-migration`。搬移只取經確認的來源檔案快照，不合併兩個 repo 的 Git history。
- Project K 工作樹曾有未提交 `log.txt` 修改；預設排除該修改及其他未提交/未追蹤狀態，只搬已提交內容，除非使用者另行指定。

## 2. 舊 peforth 與 Project K 檔案處理

### 不從舊 v1 工作樹帶入的內容

v2 orphan tree 不沿用舊 peforth 的程式和產品佈局，包括：

- `build/`、`notebook/`、舊 `peforth/`、`peforth.egg-info/`、`playground/`
- 舊 `.gitattributes`、`.gitignore`、`README.md`、`README.rst`、`setup.bat`、`setup.py`

v2 仍需新建對應的必要專案檔案：新的 `.gitignore`、README、`pyproject.toml` 等。舊 notebook 和 playground 不納入；日後如需要 v2 範例，再按新產品需求建立。

LICENSE 以已同意的 MIT 授權為基礎，使用舊 peforth LICENSE 的簡潔形式稍作整理，更新為適用於 v2 的 copyright/attribution；核對 Project K LICENSE 的原文與 attribution 後再定稿。不可在未確認授權文字前發布。

### 從 Project K `py/` 搬入的內容

**核心程式與執行期資源：**

- `projectk.py`：共用 Forth Kernel。
- `repl.py`、`ai_bridge.py`、`ai_tools.py`。
- `base.f`、`auxiliary.f`、`ai.f` 及 REPL 實際載入的其他 Forth source。
- `requirements.txt` 中確認需要的 runtime dependencies。
- `verify_projectk.py` 中可移植的 Kernel/REPL 測試。

`projectk.py` 可以從 Project K repo 的已確認 commit 手動 copy 到 peforth v2 source tree；這是直接、可審查的搬移方式，本計畫不要求額外寫自動同步工具。搬移時記錄來源 commit SHA 和檔案來源，避免日後不清楚差異從何而來。

**整體納入 source checkout：**

- `docs/` 整個目錄都搬入 peforth v2；內容可供使用者和開發者共同參考。之後再修正產品名稱、repo 路徑、安裝說明與文件索引；保留具歷史/開發價值的文件，不預設只留 user guide。
- `skills/` 和 `plugins/` 是自我開發流程的重要 components，隨 source 一起放在 `~/.peforth` checkout。首階段不自動把它們複製到 Codex、OpenCode 或其他 AI CLI 的全域目錄；如需註冊或連結，再作為獨立且可測試的功能設計。

**排除：**

- `.env`、`.ai_session.json`、API key、token、secret 和其他個人狀態。
- `__pycache__/`、暫存檔、build/cache/egg-info、測試產物。
- Project K 未提交的 `log.txt` 修改及任何未核准的工作樹變更。

若 Git-tracked `docs/` 中含 PDF、對話紀錄、暫停紀錄或舊計畫，依「整個 docs 搬入」先保留在 source tree，再以目錄/索引標示其用途；不得把秘密或個人 runtime state 混入文件。

## 3. Source、安裝環境與 Git 工作方式

### 可寫的 `~/.peforth` source

- Ubuntu／WSL checkout：`~/.peforth`。
- Windows checkout：`$HOME\.peforth`，即 `%USERPROFILE%\.peforth`。
- 兩邊各有獨立 checkout、Python 環境、`f` command 和使用者設定；不共用 Windows/WSL venv 或狀態。
- `f` 必須執行 checkout 中的程式；修改 `~/.peforth` source 後，`f` 應直接反映修改，不需手動複製程式。
- `docs/`、`skills/`、`plugins/` 跟著 source checkout；此決定是 source-tree 內容規則，不代表安裝器會把它們部署到其他 AI CLI 的目錄。

### 初期開發者安裝模型（不採 pipx）

目前主要使用者是開發者，且 peforth v2 還在初期，因此本階段不採用 pipx。目標仍是讓安裝簡單，並讓 `f` 直接執行使用者可修改的 `~/.peforth` source。

1. Windows PowerShell 和 Ubuntu/WSL Bash 各提供原生 bootstrap；clone 固定的 Project K/peforth v2 source 到各自的 `~/.peforth`。已存在目錄時先檢查 remote、branch 和 dirty state，不覆蓋使用者修改。
2. 在 `~/.peforth` 下建立各平台自己的 Python venv，安裝專案依賴並以 editable install 安裝 checkout，使 `f` 直接載入可寫 source。
3. 以使用者可呼叫的 `f` launcher/hook 指向該 venv 的 Python 和 checkout entry point；Linux 與 Windows 分別處理執行檔、PATH 和參數轉送。
4. 若實際 package entry point 可由 venv 正確提供 `f` 並滿足 PATH 需求，優先使用它；否則用簡單、可檢查的薄 launcher。兩平台的實作以實測結果為準。
5. 提供開發者使用的更新、修改、測試和 Git commit 指引；source 保持在 `~/.peforth`，不複製到 site-packages，也不由安裝器自動 commit/push。
6. 穩定安裝文件日後再固定至已測試的 v2 release tag；開發初期可指定明確 branch/commit，避免不知情地追蹤移動中的來源。

此方案不依賴 pipx。可先用 `venv + pip install -e` 實現隔離環境和 source-linked 命令；是否需要自訂 bootstrap/launcher，由 Windows 與 Ubuntu/WSL 的實測結果決定。

### 使用者設定與 commit

- API key、session index、設定及自訂 runtime state 放在各自 OS 的 `~/.peforth` 之下，與應用 source 清楚分區；Windows 和 WSL 各一份。
- `.gitignore` 必須排除 `.env`、session state、secret、runtime data、venv、cache 和 build artifacts；提供不含秘密的範例設定。
- 程式不依賴 site-packages 可寫，也不把 runtime 狀態當作 source commit。
- 使用者在自己的 `~/.peforth` checkout 修改後，可建立本機 branch/commit。bootstrap 和更新流程不得自動 commit、reset、stash 或 push。
- 遠端協作建議使用個人 fork/remote 和個人 branch，再視需要向官方 repo 提交 PR；不要假設所有使用者對 `hcchengithub/peforth` 有 push 權限，也不自動推送到 upstream。README/開發指南需提供清楚的 status、branch、commit、remote 操作方式。
- 更新前檢查 dirty state；若有修改，不覆蓋、不 reset，應停止並指引使用者先 commit/備份或自行處理 rebase。

## 4. 行動計畫

### Phase 1：唯讀鎖定來源與 manifest

**目標：** 確認 Project K 的來源快照、檔案清單與 LICENSE 依據。

1. 唯讀檢查 Project K `v2-migration` 的 remote、HEAD、tracked/untracked/modified 狀態，記錄來源 commit SHA。
2. 僅搬該 commit 的已提交檔案；預設排除未提交 `log.txt` 及其他工作樹修改。
3. 列出搬入核心、整體 `docs/`、`skills/`、`plugins/`、測試、範例和排除的敏感/暫存項目。
4. 核對 Project K MIT LICENSE 和 peforth 舊 LICENSE，按已同意方向更新授權/attribution 文本。

**驗收：** 來源 SHA、檔案 manifest 和 LICENSE 文本可審查；沒有 secrets 或未核准的工作樹變更。

### Phase 2：建立全新的 peforth v2 source tree

**目標：** 在 orphan branch 建立乾淨的 v2 專案骨架，再手動搬入核准來源。

1. 保留現有 orphan branch 名稱 `v2-migration-orphan-bootstrap`；不再安排重建、改名或刪除 branch。確認其 planning commit 和已審閱的計畫內容。
2. 從 Project K 固定來源 commit 手動 copy 核准檔案到 peforth v2 tree，排除 secrets、cache、build output 和未提交修改；記錄來源 SHA。
3. 建立新的 `.gitignore`、MIT LICENSE、README、`pyproject.toml`、測試結構和文件索引；舊版 `setup.py` 不沿用。
4. 整個搬入 `docs/`、`skills/`、`plugins/`，修正必要路徑和品牌；保留它們在 source tree 的用途。
5. 定義 package/import 結構與 `f` entry point，讓開發模式從 `~/.peforth` source 載入程式及 Forth resources。
6. 把 `.env`、session index 等設定/狀態遷移到 `~/.peforth` 下明確且被 ignore 的位置。
7. 在 README、安裝文件和命令入口加入明顯的 v2 重大不相容通知，說明 v1 使用者需另行安裝 v1.33。

**驗收：** 初始 v2 tree 沒有舊 peforth package/產品目錄；共用 Kernel、核心程式、文件、skills/plugins 和授權均在預期位置；沒有私有資料；重大變更通知明確。

### Phase 3：建立 bootstrap 與 source-linked `f`

**目標：** 讓 Windows PowerShell、Ubuntu/WSL 使用者各自一行安裝，且 `f` 執行可寫 source。

1. 在 Linux/WSL 和 Windows 分別驗證以 `venv` 建立環境，並以 `pip install -e` 將 `~/.peforth` checkout editable-install 的流程。
2. 設計各平台 bootstrap：檢查 Python/Git 前置條件，clone 指定的 v2 source，建立 checkout 內 venv、安裝依賴並暴露 `f`。
3. 測試 venv 安裝產生的 entry-point wrapper 是否能直接從 PATH 使用；若不行，實作薄 launcher/hook 指向 venv Python 和 checkout entry point。
4. 對已存在 checkout 檢查 repo remote、branch 和 dirty state；有本機修改時不可覆蓋或 reset。
5. 提供更新、解除安裝、PATH、source 修改與 Git commit 指引；安裝器不自動 sudo、不刪資料、不自動 commit/push。

**驗收：** 兩平台安裝後的 `f` 都執行各自的 `~/.peforth` source；修改 source 即可生效；dirty checkout 時更新安全停止。

### Phase 4：測試與安裝安全驗證

**目標：** 驗證 Kernel/AI/REPL、文件元件、Forth 資源、source-linked install 及資料保護。

1. 執行 Project K 共用 Kernel/REPL 測試並建立 peforth v2 CLI、AI、Forth resource 測試。
2. 測 package metadata/build（若 v2 使用 wheel/sdist）及 `venv + pip install -e`；驗證安裝方式不會取代或隱藏 `~/.peforth` 的 source tree。
3. 在乾淨 Windows PowerShell 和 Ubuntu/WSL 各自執行 bootstrap、`f`、repo 外工作目錄、source 修改後重啟、更新和解除安裝測試。
4. 測含空白路徑、無 API key、有 API key、互動 stdin/stdout/退出碼，以及 Forth resource 載入。
5. 確認 docs/skills/plugins 隨 checkout 存在但不會被自動散佈至未核准的 AI CLI 目錄。
6. 確認 `.env`、session、個人設定、cache 不會進 commit/build、不被更新覆寫；驗證 dirty checkout 保護。
7. 在 README/安裝入口檢查重大不相容通知清楚可見。

**驗收：** Windows 和 Ubuntu/WSL 均有可重現的安裝及功能測試記錄；`f` 從任意 cwd 使用可寫 source；更新保護和資料隔離通過。

### Phase 5：文件審閱、發布與主線切換

**目標：** 完成 peforth v2 發布，保留 v1.33 作為可獨立安裝的舊版。

1. 建立全新 README、AI/REPL 使用指南、開發/commit 指南、Windows/Ubuntu 安裝與更新/解除安裝說明。
2. 清楚說明 `~/.peforth` 是 source checkout，`f` 執行該 checkout，`docs/skills/plugins` 也位於其中；說明如何在自己的 branch/fork commit 和同步。
3. 安裝流程 pin 到已測試的 v2 tag；初版先採 GitHub source bootstrap，PyPI 發布另行決策。
4. 測試通過並經使用者審閱後，才另行確認 push branch、建立 v2 tag/release、GitHub default branch 切換等遠端操作。
5. Release notes 和安裝入口明確通知重大不相容變更，並提供 v1.33 安裝方式。

**驗收：** Windows/Ubuntu 使用者按文件可安裝並從任意目錄執行 `f`；source 可寫、可修改、可 commit；重大變更通知清楚；v1.33 可獨立取得。

## 5. 已確認事項與後續需審閱項目

使用者已確認：

- peforth v2 採用 Project K MIT 授權方向，並更新適當 attribution；LICENSE 可沿用舊 peforth 文件的簡潔形式稍作調整。
- v2 使用 orphan history；目前接受 `v2-migration-orphan-bootstrap` 名稱，不再為改名而操作。
- 不帶入 Project K 未提交的 `log.txt` 或其他未核准工作樹狀態。
- `docs/`、`skills/`、`plugins/` 隨 source 放在 `~/.peforth`；後兩者不因此自動散佈到其他 AI CLI 的目錄。
- v2 不保留 v1 舊功能，並須讓使用者看見重大不相容通知。
- `projectk.py` 可從確認後的 Project K source commit 手動 copy，無需先造自動同步工具。

待下一輪計畫審閱時確認：

1. 本計畫是否核准進入 source manifest 與檔案搬移階段；核准範圍不包含 push、GitHub default branch 修改、release 或 PyPI upload。
2. Git 協作建議採個人 branch/commit，必要時推到有權限的個人 fork/remote；使用者可在之後決定是否指定自己的 fork。
3. 安裝環境採 checkout 內的 Python venv 與 `pip install -e`；若 entry-point wrapper 在任一平台不能直接提供可呼叫的 `f`，採平台專用薄 launcher。

使用者目前不需要手動搬檔、手動整理 `~/.peforth` 或提供 PyPI credentials。外部寫入與正式發布會另行詢問確認。

## 6. 技術參考

- Python Packaging User Guide：console script entry points — https://packaging.python.org/en/latest/specifications/entry-points/
- Python Packaging User Guide：CLI packaging — https://packaging.python.org/en/latest/guides/creating-command-line-tools/
- pip VCS installs — https://pip.pypa.io/en/stable/topics/vcs-support/
- Python `venv` / editable install (`pip install -e`) — https://pip.pypa.io/en/stable/topics/local-project-installs/
