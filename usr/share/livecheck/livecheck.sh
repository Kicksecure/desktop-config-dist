#!/bin/bash

## Copyright (C) 2018 - 2023 ENCRYPTED SUPPORT LP <adrelanos@whonix.org>
## Copyright (C) 2018 Algernon <33966997+Algernon-01@users.noreply.github.com>
## See the file COPYING for copying conditions.

set -e

## sudo /bin/lsblk
##
## NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
## sda      8:0    0  100G  1 disk
##
## 1 means read-only
## 0 means read-write

## As soon as we have at least one "0" it is concluded: not live mode.

## when using snapd:
##
## sudo /bin/lsblk
##
## NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
## loop0    7:0    0   55M  1 loop /snap/core18/1754
## loop1    7:1    0        0 loop
## loop2    7:2    0        0 loop
## loop3    7:3    0        0 loop
## loop4    7:4    0        0 loop
## loop5    7:5    0        0 loop
## loop6    7:6    0        0 loop
## loop7    7:7    0        0 loop
## sda      8:0    0  100G  0 disk
##   sda1   8:1    0  100G  0 part /
## sr0     11:0    1 1024M  0 rom

## when using snapd:
##
## sudo /bin/lsblk --noheadings --raw --output RO
##
## 1
## 1
## 0
## 0
## 0
## 0
## 0
## 0
## 0
## 0
## 0

## The following did not work with snapd:
## http://forums.whonix.org/t/wickr-me-gets-whonix-stuck-in-live-mode/9834/1
#if sudo --non-interactive /bin/lsblk --noheadings --raw --output RO | grep --invert-match "0" ; then

## Using `sudo` to run `lsblk` because `hide-hardware-info.service` makes this no longer
## readable by user `root`. Only readable by user `root`.
## https://forums.whonix.org/t/restrict-hardware-information-to-root-testers-wanted/8618/13

if test -f /usr/share/whonix/marker ; then
   homepage="https://www.whonix.org"
else
   homepage="https://www.kicksecure.com"
fi

missing_icon=""
icon_dir="/usr/share/icons/gnome-colors-common/32x32"
icon_error="${icon_dir}/status/dialog-error.png"
icon_warn="${icon_dir}/status/dialog-warning.png"
icon_info="${icon_dir}/status/dialog-information.png"
icon_apply="${icon_dir}/actions/dialog-apply.png"
test -f "${icon_error}" || missing_icon=true
test -f "${icon_warn}" || missing_icon=true
test -f "${icon_info}" || missing_icon=true
test -f "${icon_apply}" || missing_icon=true

if [ "$missing_icon" = "true" ]; then
   bug_message="

(Minor bug: Missing icons.)"
else
   bug_message=""
fi

## Check if execution of lsblk fails with a non-zero exit code such as in case of missing sudoers permissions.
if ! lsblk_output="$(sudo --non-interactive /bin/lsblk --noheadings --raw --output RO)" ; then
   ## lsblk exited a non-zero exit code.
   true "INFO: Running 'sudo --non-interactive /bin/lsblk --noheadings --raw --output RO' failed!"
   echo "<img>${icon_error}</img>"
   ## Show "Error" next to info symbol in systray.
   echo "<txt>Error</txt>"
   echo "<tool>Live Detection Test: Minor issue. Do not panic. Unable to determine if booted into live mode or persistent mode. For assistance and to report this issue, please visit: ${homepage}/wiki/Grub-live#Live_Check_Systray_Issues or click on the icon for more information.${bug_message}</tool>"
   echo "<click>x-www-browser ${homepage}/wiki/Grub-live#Live_Check_Systray_Issues</click>"
   echo "<txtclick>x-www-browser ${homepage}/wiki/Grub-live#Live_Check_Systray_Issues</txtclick>"
   exit 0
fi
## lsblk exited with exit code 0.

proc_cmdline_output=$(cat /proc/cmdline)

## Manual testing.
#proc_cmdline_output="boot=live"
#proc_cmdline_output="root=live"

if echo "${proc_cmdline_output}" | grep --no-messages --quiet 'boot=live' ; then
   live_mode_environment="grub-live"
   maybe_iso_live_message=""
elif echo "${proc_cmdline_output}" | grep --no-messages --quiet 'root=live' ; then
   live_mode_environment="ISO Live"
   maybe_iso_live_message="

This does not matter if you are only using this ISO to install to the hard drive. In that case, this message can be safely ignored."
fi

if echo "$lsblk_output" | grep --quiet "0" ; then
   true "INFO: If at least one '0' was found. Conclusion: not all read-only. Some read-write."
   if echo "${proc_cmdline_output}" | grep --no-messages --quiet 'boot=live\|root=live'; then
      true "INFO: grub-live or ISO live is enabled."
      echo "<img>${icon_warn}</img>"
      ## Show "Live" next to info symbol in systray.
      echo "<txt>Live</txt>"
      echo "<tool>Live Mode Active (${live_mode_environment}): Your system is currently running in live mode, ensuring no changes are made to the disk. For added security, consider setting your disk to read-only mode, if possible. See: ${homepage}/wiki/Live_Mode or click on the icon for more information.${maybe_iso_live_message}${bug_message}</tool>"
      echo "<click>x-www-browser ${homepage}/wiki/read-only</click>"
      echo "<txtclick>x-www-browser ${homepage}/wiki/read-only</txtclick>"
   else
      true "INFO: Live mode and/or ISO live is disabled."
      echo "<img>${icon_info}</img>"
      ## Do not show "Persistent" next to info symbol in systray.
      #echo "<txt>Persistent</txt>"
      echo "<tool>Persistent Mode Active: Your system is currently in persistent mode, and all changes to the disk will be preserved after a reboot. For using live mode, which enables temporary sessions where changes are not saved to the disk, see: ${homepage}/wiki/Live_Mode or click on the icon for more information.${bug_message}</tool>"
      echo "<click>x-www-browser ${homepage}/wiki/Live_Mode</click>"
      echo "<txtclick>x-www-browser ${homepage}/wiki/Live_Mode<txtclick>"
   fi
else
   true "INFO: No '0' is found. Therefore only '1' found. Conclusion: read-only."

   echo "<img>${icon_apply}</img>"
   ## Show "Live" next to info symbol in systray.
   echo "<txt>Live</txt>"
   echo "<tool>Live Mode Active (${live_mode_environment}): All changes to the disk will be gone after a reboot. See: ${homepage}/wiki/Live_Mode or click on the icon for more information.${bug_message}</tool>"
   echo "<click>x-www-browser ${homepage}/wiki/Live_Mode</click>"
   echo "<txtclick>x-www-browser ${homepage}/wiki/Live_Mode</txtclick>"
fi
