#!/bin/sh

set -euo pipefail

main ()
{
  cd examples
  set -e

  python example_104.py --debug true &&
    python example_105.py --debug true &&
    python example_106.py --debug true &&
    python example_107.py --debug true &&
    python example_108.py --debug true
  rc=$?

  if [ "$rc" -eq 0 ]; then
    echo "All tests OK"
  else
    echo "All tests FAILED"
    return 1
  fi
}

main
