#!/bin/bash

set -euo pipefail

cd examples

python example_104.py --debug true &&
  python example_105.py --debug true &&
  python example_106.py --debug true &&
  python example_107.py --debug true &&
  python example_108.py --debug true

echo "All tests OK"
