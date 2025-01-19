#!/bin/bash

prj_dir=$(git rev-parse --show-toplevel)
lab_dir="$prj_dir/lab"

set -eu

run_tests ()
{
  local failed=0
  local list=""

  for i in "$lab_dir"/test[0-9]*; do
    echo -e "\n\n\n\nRun $i"
    if python $i ; then
      echo "OK: Passed $i"
    else
      echo "KO: Failed $i"
      failed=$(( failed + 1))
      list="${list} $i"
    fi

  done

  if [[ "$failed" -ne 0 ]]; then
    echo
    echo
    echo "KO: FAILED $failed times: $list"
    return 1
  fi
}

run_tests

echo
echo
echo "All tests passed"
