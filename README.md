# peforth v2

**peforth v2 is an AI-first, Python-hosted Forth environment.** Its primary interface is the `f` command, backed by a shared Forth kernel and an AI-assisted REPL.

> **Breaking change:** v2 is a major rewrite and does not retain peforth v1 debugger, Jupyter integrations, `peforth.ok()`, or other v1 APIs. If you need the frozen v1.33 behavior, install the v1.33 release instead.

## Current availability

peforth is developed continuously from the `v2-migration-orphan-bootstrap` branch. Clone that branch to use the current development version; this repository is not a published PyPI release.

## Installation (Windows and Ubuntu/WSL)

Install `uv` first by following the official instructions at `https://docs.astral.sh/uv/getting-started/installation/`, then verify with `uv --version`. The checkout is the editable source tree. Windows and WSL have separate checkouts and Python environments; install separately in each environment where you want `f`.

### Ubuntu / WSL

```bash
uv --version
git clone --branch v2-migration-orphan-bootstrap https://github.com/hcchengithub/peforth.git ~/.peforth
cd ~/.peforth
uv venv
uv pip install -e .
export PATH="$HOME/.peforth/.venv/bin:$PATH"
```

From any directory, run:

```bash
f
```

### Windows PowerShell

```powershell
uv --version
git clone --branch v2-migration-orphan-bootstrap https://github.com/hcchengithub/peforth.git "$HOME\.peforth"
Set-Location "$HOME\.peforth"
uv venv
uv pip install -e .
$env:PATH = "$HOME\.peforth\.venv\Scripts;$env:PATH"
```

If the package download fails with `invalid peer certificate: UnknownIssuer` on a corporate network, retry the install with native Windows TLS certificate handling:

```powershell
uv --native-tls pip install -e .
```

Do not disable TLS certificate verification. Open a new terminal if you want to use `f` from any directory. Windows and WSL require separate checkouts and `.venv` directories.

For WSL/Linux, keep the checkout in the WSL filesystem, such as `~/.peforth`; do not run the Linux install from a Windows-mounted `/mnt/c/...` checkout. For Windows, use the Windows checkout from PowerShell. Do not share a checkout or `.venv` between Windows and WSL.

## Configuration

Put `OPENAI_API_KEY` in `~/.peforth/.env` (Windows: `$HOME\.peforth\.env`) or in the process environment. Never commit the `.env` file. Optional settings include:

```dotenv
OPENAI_API_KEY=
PEFORTH_AI_MODEL=gpt-6-luna
PEFORTH_WSL_DISTRO=Ubuntu
PEFORTH_SOURCE_PATH=/path/to/peforth-repository
```

Set `PEFORTH_SOURCE_PATH` when the runtime package is separate from the local repository clone. It controls the repository path reported as `source_path` in System Info; it does not change which Python package is loaded. On Windows, `%USERPROFILE%` placeholders are expanded at runtime.

AI sessions and local configuration live under `~/.peforth`, separate from the packaged Forth resources. The `docs/`, `skills/`, and `plugins/` directories are part of the editable checkout and are not automatically installed into other AI CLIs' global directories.

## Updating and contributing

Inspect `git status` before updating. Keep local work on a personal branch; commit locally as needed. To push contributions, use a fork or another remote where you have write access. The install flow does not reset, overwrite a dirty checkout, commit, or push automatically.

See `docs/` for user and developer documentation. The v2 migration plan is in `docs/v2-migration-plan.md`.
