#!/bin/bash

## Copyright (C) 2018 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## Copyright (C) 2018 Algernon <33966997+Algernon-01@users.noreply.github.com>
## See the file COPYING for copying conditions.

set -o errexit
set -o nounset
set -o errtrace
set -o pipefail

MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$MYDIR"

mkdir --parents ~/livechecktest

safe-rm ~/livechecktest/*

run_test_case() {
   ./livecheck.sh "$@"
}

## Case 1: Booted in grub-live mode, with read-write devices
run_test_case "test" "boot=live" "1\n1\n0\n0" > ~/livechecktest/grub-live_read-write.txt

## Case 2: Booted in ISO Live mode, with read-write devices
run_test_case "test" "root=live" "1\n1\n0\n0" > ~/livechecktest/iso-live_read-write.txt

## Case 3: Booted in persistent mode (not live), with read-write devices
run_test_case "test" "" "1\n1\n0\n0" > ~/livechecktest/persistent_read-write.txt

## Case 4: Booted in grub-live mode, with read-only devices
run_test_case "test" "boot=live" "1\n1\n1\n1" > ~/livechecktest/grub-live_read-only.txt

## Case 5: Booted in ISO Live mode, with read-only devices
run_test_case "test" "root=live" "1\n1\n1\n1" > ~/livechecktest/iso-live_read-only.txt

## Case 6: Booted in persistent mode (not live), with read-only devices
run_test_case "test" "" "1\n1\n1\n1" > ~/livechecktest/persistent_read-only.txt
