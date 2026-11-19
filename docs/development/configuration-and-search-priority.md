# Shared Runtime Configuration and Search Priority

This guide describes configuration behavior shared by the ChatLKK CLI and peforth runtimes. Their lookup algorithms are currently the same; a small set of product-specific environment-variable names and per-user directory names differ. The mapping below is the only product-specific part. The remaining sections describe the common behavior using neutral names.

The priority order is explicitly implemented in source code. It is not an automatic convention supplied by Python, `load_dotenv`, or YAML. Treat the order as a behavioral contract: when changing implementation, update tests and both repository copies of this guide.

## Product-specific names

| Setting | ChatLKK CLI | peforth |
|---|---|---|
| Per-user config directory | `~/.chatlkk` | `~/.peforth` |
| Config directory environment variable | `CHATLKK_CONFIG_DIR` | `PEFORTH_CONFIG_DIR` |
| Diagnostic logging mode | `CHATLKK_AI_LOG_MODE` | `PEFORTH_AI_LOG_MODE` |
| Source checkout metadata path | `CHATLKK_SOURCE_PATH` | `PEFORTH_SOURCE_PATH` |
| Skills directory | `CHATLKK_SKILLS_DIR` | `PEFORTH_SKILLS_DIR` |
| Additional skills-name behavior | None | `PEFORTH_AI_SKILLS_DIR` appears in the system configuration snapshot as a fallback display value, but does not select the active skills directory; `get_skills_dir()` reads `PEFORTH_SKILLS_DIR`. |
| PowerShell override | `CHATLKK_PWSH_PATH` | `PEFORTH_PWSH_PATH` |
| WSL distro override | `CHATLKK_WSL_DISTRO` | `PEFORTH_WSL_DISTRO` |
| Snapshot-only AI model name | `CHATLKK_AI_MODEL` | `PEFORTH_AI_MODEL` |

The config-directory variable changes the base directory for local SQLite data. It does **not** relocate `.env` or `providers.yaml` search. Both runtimes use the same relative lookup structure described below, with their own per-user directory as the final candidate.

## 1. Separate configuration mechanisms

- `.env` lookup is implemented by `load_dotenv()`.
- Provider configuration lookup is implemented by `get_providers_yaml_path()` and `load_providers_config()`.
- Runtime database location is controlled by the product-specific config-directory variable above.
- Skills location is controlled by the product-specific skills-directory variable above.

These mechanisms have independent search rules. Do not infer one file's lookup order from another's.

## 2. `.env` lookup priority

With no explicit argument, `load_dotenv()` checks these candidates in order and loads the **first existing file only**:

1. `<current working directory>/.env`
2. `<directory containing ai.py>/.env`
3. `<parent directory of the directory containing ai.py>/.env`
4. `<user home>/<product-specific directory>/.env` — see the mapping above (`.chatlkk` or `.peforth`).

It stops at the first existing file; later `.env` files are not merged to fill missing keys. Values are loaded with `os.environ.setdefault()`, so variables already set in the process environment are not overwritten.

If code calls `load_dotenv(env_path=...)`, the default search is bypassed and only that explicit path is considered. A missing explicit file does not trigger the default search.

**Source of priority:** `ai.py`, function `load_dotenv(env_path=None)`. The function explicitly constructs the ordered candidate list, selects the first existing candidate, then parses that file. The ordering is therefore repository-defined, not a library default.

## 3. `providers.yaml` lookup priority

`get_providers_yaml_path(vm)` checks these candidates in order and returns the **first existing file**:

1. `<current working directory>/providers.yaml`
2. `<current working directory>/providers.yml` (alternate extension at this priority)
3. `<VM __file__dir__>/providers.yaml` (when the VM runtime directory is available)
4. `<directory containing ai.py>/providers.yaml`
5. `<user home>/<product-specific directory>/providers.yaml` — see the mapping above.

Only the working-directory candidates include `.yml`; other locations use `providers.yaml`. The selected file is not merged with later files. If it is malformed or invalid, loading reports the error instead of continuing to another candidate.

**Source of priority:** `ai.py`, `get_providers_yaml_path(vm)` defines the ordered candidates and first-existing-file rule. `load_providers_config(vm)` calls `load_dotenv()` and then selects/parses the provider file. `format_missing_providers_yaml_message(vm)` separately looks for an example template to mention in its error message; that is help text, not active configuration lookup.

The code establishes the precedence: current working directory, VM/runtime directory, source/package directory, then the per-user directory. It does not contain a separate rationale comment for why each candidate was chosen.

## 4. Runtime config directory and local databases

The product-specific config-directory variable selects the base directory for local SQLite data:

- `<config directory>/db/ai-diagnostics.sqlite3` — diagnostic log
- `<config directory>/db/sessions.sqlite3` — local session mirror

When the variable is unset or blank, the base defaults to the product-specific per-user directory in the mapping above. Legacy database locations are checked when the new `db/` location is absent. The standalone diagnostic logging monitor follows the same config-directory rule for its default database.

The main `ai.py` resolver expands `~`, `$VARIABLE`, and `%VARIABLE%`; relative configured paths are resolved relative to the process current working directory. The monitor expands home and environment variables.

**Important:** changing the config directory does not change the `.env` or `providers.yaml` candidate lists. Their final per-user candidates remain based on the fixed product-specific directory, not the custom config directory.

## 5. Environment variables common to both runtimes

A discovered `.env` file can supply these values, subject to the precedence rules above. Provider API-key variable names are selected by `api_key_env` in `providers.yaml`; keep secret values out of that YAML file.

| Variable | Effect |
|---|---|
| `OPENAI_API_KEY` | Credential when the selected provider's `api_key_env` names it. Other providers may name their own variables. |
| `OPENAI_BASE_URL` | Included in the environment snapshot; active provider endpoints are defined in `providers.yaml`, not generally overridden by this variable in the inspected source. |
| `OPENAI_MODEL` | Overrides the active Stateless profile model when set; also participates as a fallback in Stateful model selection. |
| `OPENAI_REASONING_EFFORT` | Fallback reasoning-effort setting for Stateless provider configuration/requests. |
| Provider-specific key (for example, `GEMINI_API_KEY`, `GROQ_API_KEY`) | The variable named by a provider profile's `api_key_env`; store the secret in the process environment or `.env`. |
| `LINE_CHANNEL_ACCESS_TOKEN`, `LINE_USER_ID` | Credentials used by the `line-notify` integration. The environment snapshot reports only whether these are set. |
| `LINE_API_ENDPOINT` | Optional LINE API endpoint override; otherwise the LINE push endpoint is used. |
| `LINE_NOTIFY_DISABLED` | When `1`, prepares a LINE payload but does not send it. |
| `HERDR_ENV`, `HERDR_WORKSPACE_ID`, `HERDR_TAB_ID`, `HERDR_PANE_ID` | Herdr context exposed in the environment snapshot and potentially consumed by Herdr tooling. |

The product-specific `*_AI_MODEL` names in the mapping are included in the environment snapshot but are not used as model overrides in the inspected source. Use `OPENAI_MODEL` or the provider configuration for model selection.

The runtimes also read `HOME`, `USERPROFILE`, `USERNAME`, `USER`, `SHELL`, `WSL_DISTRO_NAME`, and `COMPUTERNAME` for home, user, shell, OS, distro, or host detection/metadata. These are platform context, not product-specific application settings.

## 6. Provider file responsibilities and secrets

`providers.yaml` defines Stateful/Stateless providers, endpoints, models, profile selection, reasoning settings, and the name of the environment variable that holds a credential. The checked-in provider example advises against putting secret values in YAML. Keep keys in the process environment or `.env`.

The `.env.example` and `providers.yaml.example` files are templates, not active search candidates. Copy them to a searched location (or pass an explicit `env_path` from code for `.env`) and create a real `providers.yaml` at one of its searched locations.

**Documentation caveat:** peforth's current `.env.example` says that setting `PEFORTH_CONFIG_DIR` places `.env` under that directory. The inspected `load_dotenv()` source does not do this: its final `.env` candidate is fixed at `~/.peforth/.env`. The source behavior and this guide take precedence until the template or implementation is deliberately changed.

## 7. Source and regression tests

Primary implementation in each repository:

- `ai.py`: `_expand_env_vars()`, `_runtime_config_path()`, `_diagnostic_db_path()`, `_session_db_path()`, `load_dotenv()`, `get_providers_yaml_path()`, `load_providers_config()`, `get_skills_dir()`, and `detect_system_info()`.
- `tools/peforth_logging_monitor.py`: `default_database()` mirrors the diagnostic database config-directory rule.

Relevant regression coverage is in `test_all.py` (configuration paths, provider lookup, and monitor behavior) and `test_session_store.py` (session storage configuration).

When changing candidate order, extension support, merge behavior, or fallback behavior, update implementation, tests, and both copies of this guide together. Do not treat priority as an incidental library default.
