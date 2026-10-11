# Project K 安裝與啟動

本指南適用於一般使用者。請在已 clone 的 Project K repo 根目錄執行對應作業系統的步驟。Linux/WSL 和 Windows 各自需要一個 Python 3.10+ venv；兩者不能共用。REPL 依賴會從 py/requirements.txt 安裝。

每個系統只需一個全域 hook：
- Linux/WSL：~/.local/bin/f
- Windows：%USERPROFILE%\.local\bin\f.cmd

Windows 的 PowerShell 和 CMD 共用 f.cmd。hook 會直接呼叫 venv 裡的 Python，不必先 activate。

## Linux / WSL

在 repo 根目錄執行：

~~~bash
PROJECT_ROOT="$(pwd)"
VENV="$HOME/.venvs/project-k"

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -r "$PROJECT_ROOT/py/requirements.txt"

mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/f" <<EOF
#!/usr/bin/env bash
exec "$VENV/bin/python" "$PROJECT_ROOT/py/repl.py" "\$@"
EOF
chmod +x "$HOME/.local/bin/f"
~~~

確保 ~/.local/bin 在 PATH 中。若尚未加入，將下列一行放入 ~/.profile：

~~~bash
export PATH="$HOME/.local/bin:$PATH"
~~~

開啟新的終端機後即可在任何目錄輸入 f。

## Windows PowerShell / CMD

在 repo 根目錄開啟 PowerShell，執行：

~~~powershell
$Project = (Get-Location).Path
$Venv = Join-Path $env:USERPROFILE '.venvs\project-k'
py -3 -m venv $Venv

$Python = Join-Path $Venv 'Scripts\python.exe'
& $Python -m pip install -r (Join-Path $Project 'py\requirements.txt')

$Bin = Join-Path $env:USERPROFILE '.local\bin'
New-Item -ItemType Directory -Force $Bin | Out-Null
$Repl = Join-Path $Project 'py\repl.py'
$Launcher = Join-Path $Bin 'f.cmd'

@"
@echo off
"$Python" "$Repl" %*
exit /b %ERRORLEVEL%
"@ | Set-Content -Encoding ascii $Launcher

$UserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$PathEntries = @($UserPath -split ';' | Where-Object { $_ })
if ($PathEntries -notcontains $Bin) {
    [Environment]::SetEnvironmentVariable(
        'Path',
        (($PathEntries + $Bin) -join ';'),
        'User'
    )
}
~~~

關閉並重新開啟 PowerShell 或 CMD，之後便可在任何目錄輸入 f。這個 Windows venv 同時供兩種 shell 使用。

## 啟動與環境資訊

在任意工作目錄輸入：

~~~text
f
~~~

REPL 啟動後，可輸入 `system_info stringify . ` 查看目前 Python、venv、shell 與 Project K source_path。
