# peforth v2 安裝與開發環境

> v2 是重大不相容改寫，不支援 v1 debugger、Jupyter 整合或舊 API。本文是開發 checkout 的安裝方式，不是已發布的一鍵安裝器。

## 目前可用性

GitHub 上的 `v2-migration-orphan-bootstrap` 目前仍只有遷移計畫，尚無 Python package、`pyproject.toml` 或 `peforth/`。因此遠端 clone 後執行 `pip install -e .` 會失敗。請先取得已含完整 v2 source 的可寫 checkout；不要用尚未更新的遠端分支安裝。

Windows 與 WSL 是不同作業環境，必須各自使用 checkout、Python venv 與 `f` 命令，不共用 Windows/WSL venv，也不要以 WSL 執行的 `f` 代表 Windows 安裝已完成。

## Ubuntu / WSL

進入本機可寫的 peforth checkout：

```bash
cd /path/to/your/writable/peforth-checkout
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

將 `<checkout>/.venv/bin` 加入 WSL 的 `PATH`（或啟用 `.venv`），在 checkout 外執行 `f --help` 與 `f -e 10 20 + . cr`。預期第二個命令輸出 `30`。

## Windows PowerShell

請在 Windows 本機有寫入權的 checkout 執行，而非透過 WSL 操作：

```powershell
Set-Location 'C:\path\to\your\writable\peforth-checkout'
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e .
```

將 `<checkout>\.venv\Scripts` 加入使用者 `PATH`，開啟新的 PowerShell，在 checkout 外執行 `f --help` 與 `f -e 10 20 + . cr`。預期第二個命令輸出 `30`。若沒有 `py` launcher，請安裝支援 Python 3.10+ 的 Windows Python，再重試。若要改 Windows 使用者 PATH，請先確認該項目尚未存在，避免重複新增。

## 設定和使用者資料

AI API key 可放在 `~/.peforth/.env`（Windows：`$HOME\.peforth\.env`）或程序環境變數。不要將 `.env` 提交到 Git。可選設定：

```dotenv
OPENAI_API_KEY=
PEFORTH_AI_MODEL=gpt-6-astra
PEFORTH_AI_SKILLS_DIR=skills
PEFORTH_WSL_DISTRO=Ubuntu
```

session index 和本機 `.env` 位於 `PEFORTH_CONFIG_DIR` 指定目錄（預設 `~/.peforth`），不與 package resources、checkout 或另一作業系統共用。`docs/`、`skills/`、`plugins/` 隨 source checkout 提供，不會自動安裝到其他 AI CLI 的全域目錄。

## 更新、修改與解除安裝

更新前先看 `git status`，保留 dirty/untracked 修改；不要對有本機修改的 checkout 使用 reset、強制清理或覆寫式更新。使用者可建立個人 branch 並自行 commit；推送時需使用有寫入權的 fork/remote。本 repo 的 bootstrap 不應自動 reset、覆蓋修改、commit 或 push。

解除安裝時，先從 PATH 移除 checkout 的 venv Scripts/bin 路徑，再由使用者自行刪除 checkout 和 venv。設定目錄 `~/.peforth`（包含 `.env` 和 session index）是獨立使用者資料；除非使用者明確想刪除，否則保留。
