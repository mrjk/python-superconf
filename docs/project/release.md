# Release

Maintainer guide to bump, tag, and publish `superconf` to PyPI.

## Status

| Area | Today | Notes |
|------|--------|--------|
| `./scripts/release.sh` | Works | Commits `pyproject.toml` + `superconf/__init__.py`; branch rules enforced |
| `task publish_pypi` / `publish_pypi_test` | Works | Manual publish after push/tags |
| `poetry-bumpversion` | Install via `poetry self add` | **Not** a project dependency |
| Bumpversion file path | Needs fix | `pyproject.toml` still has placeholder `your_package/__init__.py` — change to `superconf/__init__.py` before relying on synced `__init__` version |
| Publish-on-tag GHA | Planned | Optional `publish_pypi.yml` on tags `v*` |

Usable now: `./scripts/release.sh --dry-run patch`, then real bump on the correct branch; `task publish_pypi` with a token.

## Overview

| Step | Command |
|------|---------|
| Bump + tag | `./scripts/release.sh <VERSION>` |
| Push | `git push && git push --tags` |
| Publish | `task publish_pypi` (manual today) |

Version lives in `pyproject.toml`. Install the bump plugin once with
`poetry self add poetry-bumpversion` so `poetry version` can also update
`superconf/__init__.py` (see `[tool.poetry_bumpversion]` in `pyproject.toml`).

Package directory is the filesystem path **`superconf`** (not the PyPI name alone).
Override if needed: `PKG_DIR=superconf ./scripts/release.sh patch` (once the script
reads `PKG_DIR`; current script already hardcodes `superconf/__init__.py`).

## Prerequisites

- Clean git working tree (untracked files are fine; modified/staged files are not)
- Poetry project deps on the **daily Python 3.11** env (in-project **`.venv/`** via `poetry install --with dev`)
- For stable releases: checkout `main` or `master`
- For pre-releases (`pre*`, or a version like `1.2.3a0`): any branch **except** `main`/`master` (usually `develop`)
- For publish: a PyPI API token (`poetry config` or `POETRY_PYPI_TOKEN_PYPI`)

Never commit tokens. Do not store them in `.envrc`. See [Development setup](setup.md).

Supported runtime range for users: **Python 3.9+** (see [Development setup](setup.md)).

## Bump and tag

Preview:

```bash
./scripts/release.sh --dry-run prerelease
./scripts/release.sh --dry-run patch
```

Apply:

```bash
# Pre-release on develop (e.g. 0.2.0a0 -> 0.2.0a1)
./scripts/release.sh prerelease

# Next pre-release phase (a -> b -> rc -> final)
./scripts/release.sh prerelease --next-phase

# Stable on main/master
./scripts/release.sh patch    # or: minor | major | 1.2.3
```

The script:

1. Checks branch rules and clean tree
2. Runs `poetry version …`
3. Commits with `bump: version vX.Y.Z`
4. Creates annotated tag `vX.Y.Z`

Then push:

```bash
git push && git push --tags
```

See `./scripts/release.sh --help` for all bump keywords.

## PyPI authentication

### Local / manual (current)

```bash
poetry config pypi-token.pypi <your-token>
# or:
export POETRY_PYPI_TOKEN_PYPI=<your-token>
task publish_pypi
```

If you see `HTTP 403` / access denied, the token is missing or revoked.

### TestPyPI

```bash
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi <your-testpypi-token>
task publish_pypi_test
```

## Typical flows

### Next alpha on develop

```bash
./scripts/release.sh prerelease
git push && git push --tags
task publish_pypi
```

### Stable release

```bash
git checkout main && git pull
./scripts/release.sh patch
git push && git push --tags
task publish_pypi
```
