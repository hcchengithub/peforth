# peforth v2

**peforth v2 is an AI-first, Python-hosted Forth environment.** Its primary interface is the `f` command, backed by a shared Forth kernel and an AI-assisted REPL.

> **Breaking change:** v2 is a major rewrite and does not retain peforth v1 debugger, Jupyter integrations, `peforth.ok()`, or other v1 APIs. If you need the frozen v1.33 behavior, install the v1.33 release instead.

## Development install (Windows and Ubuntu/WSL)

The checkout is the editable source tree. Windows and WSL have separate checkouts and Python environments; install separately in each environment where you want `f`.

### Ubuntu / WSL

```bash
git clone --branch v2-migration-orphan-bootstrap https://github.com/hcchengithub/peforth.git ~/.peforth
cd ~/.peforth
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Add `~/.peforth/.venv/bin` to `PATH` if it is not already available. From any directory, run:

```bash
f
```

### Windows PowerShell

```powershell
git clone --branch v2-migration-orphan-bootstrap https://github.com/hcchengithub/peforth.git "$HOME\.peforth"
Set-Location "$HOME\.peforth"
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e .
```

Add `$HOME\.peforth\.venv\Scripts` to the user `PATH`, then open a new terminal and run `f` from any directory.

## Configuration

Put `OPENAI_API_KEY` in `~/.peforth/.env` (Windows: `$HOME\.peforth\.env`) or in the process environment. Never commit the `.env` file. Optional settings include:

```dotenv
OPENAI_API_KEY=
PEFORTH_AI_MODEL=gpt-6-astra
PEFORTH_WSL_DISTRO=Ubuntu
```

AI sessions and local configuration live under `~/.peforth`, separate from the packaged Forth resources. The `docs/`, `skills/`, and `plugins/` directories are part of the editable checkout and are not automatically installed into other AI CLIs' global directories.

## Updating and contributing

Inspect `git status` before updating. Keep local work on a personal branch; commit locally as needed. To push contributions, use a fork or another remote where you have write access. The bootstrap/install flow must not reset, overwrite a dirty checkout, commit, or push automatically.

See `docs/` for user and developer documentation. The v2 migration plan is in `docs/v2-migration-plan.md`.
