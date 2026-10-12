# peforth v2 遷移計畫

## 目標與決策

以 Project K Python Edition 為程式碼基礎建立 AI-first 的 peforth v2，以共用 Forth Kernel 和 `f` 命令為核心。v2 不承接 peforth v1 的舊功能或 Git 歷史；v1.33 仍可獨立安裝。v2 有重大不相容變更，README、安裝入口和 release notes 必須明確通知使用者。

Windows 與 Ubuntu／WSL 各自維護可寫的 source checkout：Windows `%USERPROFILE%\\.peforth`、Ubuntu／WSL `~/.peforth`。`f` 必須執行 checkout 中的程式；`docs/`、`skills/`、`plugins/` 隨 source 一起放在 checkout，供開發者使用。

- 工作 repo/branch：`hcchengithub/peforth`，`v2-migration-orphan-bootstrap`（orphan history）。
- 固定來源：`hcchengithub/project-k` 的 `v2-migration` branch，commit `372eb63e314659607e6b434daf949bc310b8d38e`；只取該 commit 的已提交內容，不合併 Git history，不帶入來源 repo 未提交的 `log.txt` 修改。
- `peforth/projectk.py` 保留共用 Forth Kernel 的實作角色；不另造第二份 kernel。
- 納入來源 `py/docs/`、`py/skills/`、`py/plugins/` 的核准內容並重新佈局至 repo 根目錄；不自動部署到其他 AI CLI 的全域目錄。
- 排除 secrets、`.env`、session/user state、cache、暫存檔與 build artifacts。
- 以 MIT 授權發布，並在 LICENSE 整理必要 attribution。
- 使用者以開發者為主，初期不採 pipx。Windows 與 Ubuntu/WSL 各自在 `%USERPROFILE%\\.peforth` / `~/.peforth` 維護 checkout，使用 `uv` 建立本地 venv 並以 `uv pip install -e` 連結 source 並提供 `f`。Windows 與 WSL 不共用 checkout 或 venv；WSL checkout 應放在 Linux filesystem，不要從 `/mnt/c/...` 的 Windows checkout 執行 Linux 安裝。
- 使用者可在 checkout 建立個人 branch/commit；需推送時使用個人 fork/remote。安裝流程不自動 commit、reset、覆蓋 dirty source 或 push。

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

1. Windows PowerShell 與 Ubuntu／WSL 分別建立 checkout；先安裝 `uv`，再使用 `uv venv` 與 `uv pip install -e` 連結 checkout。
2. 驗證安裝產生的 entry-point wrapper；Windows 與 WSL 不共用 checkout 或 venv。
3. WSL checkout 放在 Linux filesystem，不從 `/mnt/c/...` 的 Windows checkout 執行 Linux 安裝。
4. 文件說明更新、修改、測試、commit、個人 branch/fork 與解除安裝。

### 4. 驗證狀態（2026-10-12）

- [x] WSL/Linux editable install 與 repo 外 `f --help` / Forth smoke test 通過。
- [x] sdist 與 wheel 成功建置；wheel 含 package runtime Forth resources。
- [x] `uv` editable install instructions 與 package runtime resources 文件已整理。
- [x] `.env`、session index、`.venv`、dist 等路徑由 Git ignore 保護。
- [ ] Windows Python editable install 與 repo 外端到端驗證：尚未完成。
- [ ] Windows/WSL 各自使用 `uv` 的乾淨環境首次安裝、PATH 操作及解除安裝驗收尚未完成。

## 執行核准與發布限制

已核准本機 source 盤點、遷移、package/CLI 與文件修訂。使用者已自行 commit/push；後續仍不得自行 commit 或 push。未核准 GitHub default branch 修改、tag/release 或 PyPI upload。
