# peforth v2

**peforth v2 is an AI-first, Python-hosted Forth environment.** Its primary interface is the `f` command, backed by a shared Forth kernel and an AI-assisted REPL.

> **Breaking change:** v2 is a major rewrite and does not retain peforth v1 debugger, Jupyter integrations, `peforth.ok()`, or other v1 APIs. If you need the frozen v1.33 behavior, install the v1.33 release instead.

## Current availability

The v2 source is currently available only in the `v2-migration-orphan-bootstrap` branch's local checkout; the corresponding GitHub branch does not yet contain the package or CLI files. Do not use `pip install -e .` against a remote clone of that branch until those files have been pushed. The commands below install the existing local checkout, not a fresh remote clone.

## Bootstrap from a writable local checkout

These platform-specific bootstraps create/reuse only the checkout-local `.venv` and install the current source in editable mode. They validate the checkout's origin and migration branch, never fetch/checkout/reset or overwrite source, and never commit or push. They may install Python package dependencies into `.venv`; inspect the script before running it. Run them from this local repo checkout (not from a remote clone that lacks the migration files):

- WSL/Linux: `bash ./bootstrap.sh`
- Windows PowerShell: `./bootstrap.ps1`

Neither script modifies PATH. Add `.venv/bin` (WSL/Linux) or `.venv\\Scripts` (Windows) yourself if you want bare `f` in new terminals.

## Development install (Windows and Ubuntu/WSL)

The checkout is the editable source tree. Windows and WSL have separate checkouts and Python environments; install separately in each environment where you want `f`.

### Ubuntu / WSL

```bash
cd /path/to/your/writable/peforth-checkout
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Add `~/.peforth/.venv/bin` to `PATH` if it is not already available. From any directory, run:

```bash
f
```

### Windows PowerShell

```powershell
Set-Location 'C:\path\to\your\writable\peforth-checkout'
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e .
```

Add `<checkout>\.venv\Scripts` to the user `PATH`, then open a new terminal and run `f` from any directory.

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
