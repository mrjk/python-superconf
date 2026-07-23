# Development setup

How to run SuperConf locally and across supported Python versions.

## Status

| Area | Today | CI toolkit (in progress) |
|------|--------|---------------------------|
| Poetry + in-project `.venv/` | Works (`poetry.toml`) | Same |
| Task + `PY=poetry run` | Works (root `Taskfile.yml`) | CORE + docs Taskfile |
| mise pins (python, poetry, task, shellcheck) | Works (`mise.toml` + `.envrc`) | Same |
| `task clean` / `test_matrix` | Not yet | `scripts/clean_workspace.sh`, `run_python_matrix.sh` |
| Docs Task / MkDocs CI | Docs are markdown under `docs/` | `docs/Taskfile.yml` + `gh_page` workflow |
| GitHub Actions | `test_project.yml` (single 3.11) | Matrix + thin `setup-ci` later |

Usable now: `mise install`, `poetry install --with dev`, `task test_report`, `task test_lint` / `fix_lint`, `task test_examples`, `./scripts/release.sh --dry-run`.

Secrets: put PyPI tokens in `poetry config`, your shell env, or gitignored `.envrc.local` — never in committed `.envrc`.

## Supported Python versions

| | Version |
| --- | --- |
| **Declared in packaging** | `python = "^3.9"` (`pyproject.toml`) |
| Daily / release base | **3.11** (`mise.toml`) |
| CI matrix (planned) | **3.10–3.13** |
| Docs build (planned) | 3.10 or daily pin |

## Virtualenvs (always)

Development **always** uses a project-local virtualenv — never install into the system Python.

| Env | Path | Role |
| --- | --- | --- |
| Daily / release | **`.venv/`** | Poetry in-project env (`poetry.toml`: `virtualenvs.in-project = true`) |
| Version matrix (planned) | **`.venvs/pyX.Y/`** | Isolated envs for `task test_matrix` (does not replace `.venv`) |

Both directories are gitignored.

## Prerequisites

- [mise](https://mise.jdx.dev/) — pins **Python 3.11** (override with `PYTHON_VERSION`), **Poetry 2.1.4**, **Task 3.52.0**, and **shellcheck** (`mise.toml`)
- A shell with mise activated (`eval "$(mise activate bash)"`, or direnv + `use mise` in `.envrc`)

After cloning, trust the config once: `mise trust`.

Poetry and Task come from mise after `mise install` — you do **not** need a system-wide Poetry install.

**Secrets:** never put PyPI tokens in `.envrc` or commit them. Use `poetry config` or export `POETRY_PYPI_TOKEN_PYPI` / `POETRY_PYPI_TOKEN_TESTPYPI` in your private shell env. See [Release](release.md).

## Bootstrap (daily env)

```bash
# 1) Activate mise in this shell (skip if direnv already loaded .envrc)
eval "$(mise activate bash)"   # or: eval "$(mise activate zsh)"

# 2) Install pinned tools
mise install
mise which poetry              # should print a path under ~/.local/share/mise/...

# 3) Create/update project .venv
poetry env use "$(mise which python)"
poetry install --with dev
```

If Poetry is only available inside an existing `.venv` (bootstrap in progress):

```bash
./.venv/bin/poetry install --with dev
```

After bootstrap, run Task as usual — Python tools are invoked via `poetry run`
(see `PY` in the root Taskfile), so you do **not** need to activate `.venv`:

```bash
task test
task fix_lint
```

`poetry` itself must be on your PATH (from `mise activate` / `.envrc`), or use `./.venv/bin/poetry run task …`.

Useful subsets:

| Task | What it runs |
|------|----------------|
| `task test_report` | Pytest + coverage on `superconf` |
| `task test_pytest` | Pytest suite |
| `task test_examples` | Example scripts via `scripts/run_python_scripts.sh` |
| `task test_lint` | isort `--check-only`, black `--check`, pylint |
| `task test_lint_full` | Lint + yamllint + markdown + shellcheck |
| `task fix_lint` | isort + black (rewrite) |
| `task clean` | Planned: remove `.venv`, `.venvs`, caches, build artifacts |

## Reset environment (fresh-clone-like)

Planned once `scripts/clean_workspace.sh` lands:

```bash
task clean
```

Expected deletions (same idea as Clak):

- `.venv/`, `.venvs/`
- `dist/`, `build/`, `*.egg-info`
- `__pycache__/`, `.pytest_cache/`, coverage and similar caches
- `docs/site/`, `.cache/`

Then bootstrap again:

```bash
eval "$(mise activate bash)"   # if needed
mise install
poetry env use "$(mise which python)"
poetry install --with dev
```

## Local Python matrix

Planned: exercise 3.10–3.13 without touching daily `.venv`, using isolated envs under `.venvs/pyX.Y`.

```bash
task test_matrix                       # all matrix versions
task test_matrix_one PYTHON_VERSION=3.11
```

Override the set with `PYTHON_MATRIX` if needed:

```bash
PYTHON_MATRIX="3.11 3.12" bash ./scripts/run_python_matrix.sh
```

## CI

GitHub Actions will use an in-project `.venv` and run the same command as locally:

```bash
poetry install --with dev
poetry run task test
```

See `.github/workflows/test_project.yml` (single Python 3.11; matrix later).

## Releases

Bump/tag/publish uses the daily `.venv`. Maintainer guide: [Release](release.md).
