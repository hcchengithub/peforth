[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$ExpectedRemote = 'https://github.com/hcchengithub/peforth.git'

if (-not (Test-Path -LiteralPath (Join-Path $Root 'pyproject.toml')) -or
    -not (Test-Path -LiteralPath (Join-Path $Root 'peforth\repl.py'))) {
    throw "Not a complete peforth source checkout: $Root"
}
$Git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $Git) { $Git = Get-Command git -ErrorAction SilentlyContinue }
if (-not $Git) { throw 'Git is required. Install Git for Windows and retry.' }
$Remote = (& $Git.Source -C $Root remote get-url origin 2>$null | Select-Object -First 1)
if ($LASTEXITCODE -ne 0 -or $Remote.Trim() -ne $ExpectedRemote) {
    throw "Unexpected origin remote in '$Root': '$Remote' (expected '$ExpectedRemote')."
}
$Branch = (& $Git.Source -C $Root branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $Branch -ne 'v2-migration-orphan-bootstrap') {
    throw "Refusing bootstrap on unexpected branch: '$Branch'."
}
$Porcelain = & $Git.Source -C $Root status --porcelain --untracked-files=all
if ($Porcelain) {
    Write-Warning 'Checkout has local changes; bootstrap will not alter or discard source files.'
}

$Python = $null
$PyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if ($PyLauncher) {
    & $PyLauncher.Source -3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
    if ($LASTEXITCODE -eq 0) { $Python = @{ Exe = $PyLauncher.Source; Prefix = @('-3') } }
}
if (-not $Python) {
    $PythonCmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($PythonCmd) {
        & $PythonCmd.Source -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
        if ($LASTEXITCODE -eq 0) { $Python = @{ Exe = $PythonCmd.Source; Prefix = @() } }
    }
}
if (-not $Python) { throw 'Python 3.10+ is required; install Python for Windows and retry.' }

$Venv = Join-Path $Root '.venv'
$VenvCfg = Join-Path $Venv 'pyvenv.cfg'
if ((Test-Path -LiteralPath $Venv) -and -not (Test-Path -LiteralPath $VenvCfg)) {
    throw "Refusing to reuse an existing non-venv path: $Venv"
}
$VenvPython = Join-Path $Venv 'Scripts\python.exe'
if ((Test-Path -LiteralPath $VenvCfg) -and -not (Test-Path -LiteralPath $VenvPython)) {
    throw "Existing .venv is not a usable Windows environment: $Venv"
}
if (-not (Test-Path -LiteralPath $VenvCfg)) {
    & $Python.Exe @($Python.Prefix) -m venv $Venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create venv (exit $LASTEXITCODE)." }
}
& $VenvPython -m pip install -e $Root
if ($LASTEXITCODE -ne 0) { throw "Editable install failed (exit $LASTEXITCODE)." }

Write-Host ''
Write-Host 'peforth v2 editable install is ready. Source files were not updated.'
Write-Host "Run from any directory: $Venv\Scripts\f.exe --help"
Write-Host "Smoke test: $Venv\Scripts\f.exe -e 10 20 + . cr"
Write-Host "Add '$Venv\Scripts' to your user PATH only if it is not already present."
Write-Host 'No commit, reset, checkout, or push was performed.'
