#!/bin/bash
# Run all python files in a specific directory.
# Uses Poetry's venv by default so project deps (pytest, package) resolve.
# Override with: PYTHON='python3.11' bash ./scripts/run_python_scripts.sh …


set -eu -o pipefail

# Default: poetry run python (matches Taskfile PY). Single binary via PYTHON=.
run_one ()
{
  if [[ -n "${PYTHON:-}" ]]; then
    "$PYTHON" "$1"
  else
    poetry run python "$1"
  fi
}

run_python_files ()
{
  local failed=0
  local list=""

  local src_dir="$1"
  local pattern="${2:-*.py}"

  # Loop over each files
  for i in "$src_dir"/$pattern; do
    echo -e "\n=========================="
    echo -e "Run $i"
    if run_one "$i" ; then
      echo "OK: Passed $i"
    else
      echo "KO: Failed $i"
      failed=$(( failed + 1))
      list="${list} $i"
    fi
  done

  # Report errors
  if [[ "$failed" -ne 0 ]]; then
    echo -e "\n=========================="
    echo "KO: FAILED $failed times: $list"
    return 1
  fi
}

run_python_files "$@"

echo -e "\n=========================="
echo "All tests passed"
