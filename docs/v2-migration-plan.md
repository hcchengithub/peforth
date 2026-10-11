# peforth v2 遷移計畫

## 目標與決策

以 Project K Python Edition 為程式碼基礎建立 AI-first 的 peforth v2，以共用 Forth Kernel 和 `f` 命令為核心。v2 不承接 peforth v1 的舊功能或 Git 歷史；v1.33 仍可獨立安裝。v2 有重大不相容變更，README、安裝入口和 release notes 必須明確通知使用者。

Windows 與 Ubuntu／WSL 各自維護可寫的 source checkout：Windows `%USERPROFILE%\\.peforth`、Ubuntu／WSL `~/.peforth`。`f` 必須執行 checkout 中的程式；`docs/`、`skills/`、`plugins/` 隨 source 一起放在 checkout，供開發者使用。

- 工作 repo/branch：`hcchengithub/peforth`，`v2-migration-orphan-bootstrap`（orphan history）。
- 固定來源：`hcchengithub/project-k` 的 `v2-migration` branch，commit `372eb63e314659607e6b434daf949bc310b8d38e`；只取該 commit 的已提交內容，不合併 Git history，不帶入來源 repo 未提交的 `log.txt` 修改。
- `peforth/projectk.py` 保留共用 Forth Kernel 的實作角色；不另造第二份 kernel。
- 納入來源 `py/docs/`、`py/skills/`、`py/plugins/`；不自動部署到其他 AI CLI 的全域目錄。
- 排除 secrets、`.env`、session/user state、cache、暫存檔與 build artifacts。
- 以 MIT 授權發布，並在 LICENSE 整理必要 attribution。
- 使用者以開發者為主，初期不採 pipx。Windows 與 Ubuntu/WSL 各自在 `%USERPROFILE%\\.peforth` / `~/.peforth` 維護 checkout，建立本地 venv，以 `pip install -e` 連結 source 並提供 `f`。若 entry-point wrapper 無法直接呼叫，再使用薄 launcher。
- 使用者可在 checkout 建立個人 branch/commit；需推送時使用個人 fork/remote。bootstrap 不自動 commit、reset、覆蓋 dirty source 或 push。

## 遷移步驟

### 1. 建立來源 manifest

唯讀檢查固定來源的 `py/` tracked files 和 LICENSE，列出納入與排除項目。來源工作樹未提交檔案不納入。

### 2. 搬入 source 並建立 v2 專案骨架

1. 將固定來源 commit 的已追蹤 `py/` 檔案搬至 peforth orphan tree；排除來源工作樹 dirty 的 `log.txt`、secrets、cache、build artifacts。
2. 搬入整個 `docs/`、`skills/`、`plugins/`，再修訂品牌、路徑和文件導覽。
3. 建立 v2 MIT LICENSE、`.gitignore`、README、`pyproject.toml`、新的 package 目錄和測試結構。
4. 以 `peforth.projectk` 作為共用 Kernel；納入 AI REPL、Forth runtime resources 與必要測試。
5. 將使用者可寫設定/session state 放在 `~/.peforth` 下並由 Git ignore 保護。
6. README/安裝入口明顯標示 v2 重大不相容變更。

### 3. 建立開發者安裝與 `f` 命令

1. Windows PowerShell 與 Ubuntu／WSL 分別建立 checkout 內 venv，安裝依賴並以 `pip install -e` 連結 checkout。
2. 驗證安裝產生的 entry-point wrapper；必要時建立薄 launcher，確保 `f` 指向該 checkout。
3. Bootstrap 對既有 checkout 檢查 remote、branch 和 dirty state，不覆蓋修改；僅建立/使用本機 venv 並 editable-install，不自動更新 source。
4. 文件說明更新、修改、測試、commit、個人 branch/fork 與解除安裝。

### 4. 驗證

- 執行 Kernel/REPL 測試，測試 `f`、Forth resources、repo 外工作目錄、含空白路徑、設定和 session state。
- 在 Windows PowerShell 與 Ubuntu／WSL 分別測試安裝、重跑、更新、dirty-tree 保護和解除安裝。
- 驗證 `.env`、session、secrets、cache 不會進 Git 或 build，也不會被更新覆寫。
- 測試及使用者審閱完成後，再另行確認是否 push、建立 v2 tag/release 或切換 GitHub default branch。

## 執行核准

已核准本機來源盤點、manifest、source 搬移和 v2 package/CLI 整合。不包含 push、GitHub default branch 修改、tag/release 或 PyPI upload。
