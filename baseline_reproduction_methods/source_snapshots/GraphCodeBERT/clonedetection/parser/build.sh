#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' 'Parser source snapshots are not fetched through VCS in this release artifact.'
printf '%s\n' 'Use the packaged parser snapshots or upstream source archives when rebuilding.'
python build.py