#!/bin/bash

## Copyright (C) 2018 - 2023 ENCRYPTED SUPPORT LP <adrelanos@whonix.org>
## Copyright (C) 2018 Algernon <33966997+Algernon-01@users.noreply.github.com>
## See the file COPYING for copying conditions.

set -e
set -o errexit
set -o nounset
set -o errtrace
set -o pipefail

MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$MYDIR"

run_test_case() {
   ./livecheck.sh "$@"
}

## Case 1: Booted in grub-live mode, with read-write devices
run_test_case "boot=live" "1\n1\n0\n0"

## Case 2: Booted in ISO Live mode, with read-write devices
run_test_case "root=live" "1\n1\n0\n0"

## Case 3: Booted in persistent mode (not live), with read-write devices
run_test_case "" "1\n1\n0\n0"

## Case 4: Booted in grub-live mode, with read-only devices
run_test_case "boot=live" "1\n1\n1\n1"

## Case 5: Booted in ISO Live mode, with read-only devices
run_test_case "root=live" "1\n1\n1\n1"

## Case 6: Booted in persistent mode (not live), with read-only devices
run_test_case "" "1\n1\n1\n1"
