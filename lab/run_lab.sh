#!/bin/bash

prj_dir=$(git rev-parse --show-toplevel)
lab_dir="$prj_dir/lab"

set -eu

for i in "$lab_dir"/test[0-9]*; do 
  echo -e "\n\n\n\nRun $i"
  python $i || { echo "TEST FAILED on $i"; exit 1 ; }
  echo "Tests are ok on: $i"
done

echo
echo
echo "All tests passed"
