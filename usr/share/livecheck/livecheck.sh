#!/bin/bash

## Copyright (C) 2018 - 2023 ENCRYPTED SUPPORT LP <adrelanos@whonix.org>
## Copyright (C) 2018 Algernon <33966997+Algernon-01@users.noreply.github.com>
## See the file COPYING for copying conditions.

set -e

## The following command lists the block devices:
## sudo /bin/lsblk
##
## Example output:
## NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
## sda      8:0    0  100G  1 disk
##
## RO (Read-Only) column:
## 1 indicates read-only
## 0 indicates read-write
##
## If any "0" appears, the system is not in live mode.

## Special case when using snapd:
##
## sudo /bin/lsblk
##
## Example output:
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

## Running:
##
## sudo /bin/lsblk --noheadings --raw --output RO
##
## Example output:
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

## The following method did not work properly with snapd:
## http://forums.whonix.org/t/wickr-me-gets-whonix-stuck-in-live-mode/9834/1
#if sudo --non-interactive /bin/lsblk --noheadings --raw --output RO | grep --invert-match "0" ; then

## We use `sudo` to run `lsblk` because `hide-hardware-info.service` makes it readable only by the `root` user.
## https://forums.whonix.org/t/restrict-hardware-information-to-root-testers-wanted/8618/13

if test -f /usr/share/whonix/marker ; then
   homepage="https://www.whonix.org"
else
   homepage="https://www.kicksecure.com"
fi

missing_icon=""
icon_dir="/usr/share/icons/gnome-colors-common/32x32"

msg_cmd="/usr/libexec/msgcollector/generic_gui_message"

icon_error="${icon_dir}/status/dialog-error.png"
icon_persistent_mode="${icon_dir}/status/dialog-information.png"
icon_grub_live_without_read_only="${icon_dir}/status/user-online.png"
icon_iso="${icon_dir}/devices/media-optical.png"
icon_grub_live_with_read_only="${icon_dir}/actions/dialog-apply.png"

test -f "${icon_error}" || missing_icon=true
test -f "${icon_persistent_mode}" || missing_icon=true
test -f "${icon_grub_live_without_read_only}" || missing_icon=true
test -f "${icon_iso}" || missing_icon=true
test -f "${icon_grub_live_with_read_only}" || missing_icon=true

if [ "$missing_icon" = "true" ]; then
   bug_message="<br/><i>(Minor bug: Missing icons)</i><br/>"
else
   bug_message=""
fi

heading_line="<u><b>Live Check Result:</b></u>"

# Check if the lsblk command fails (e.g., due to insufficient sudo permissions)
if ! lsblk_output="$(sudo --non-interactive /bin/lsblk --noheadings --raw --output RO)" ; then
   # lsblk command failed with a non-zero exit code
   true "INFO: Running 'sudo --non-interactive /bin/lsblk --noheadings --raw --output RO' failed!"
   echo "<img>${icon_error}</img>"
   echo "<txt>Error</txt>"
   title="Livecheck"
   link="<a href=\"${homepage}/wiki/Grub-live#Live_Check_Systray_Issues\">${homepage}/wiki/Grub-live#Live_Check_Systray_Issues</a>"
   msg="\
${heading_line}<br/><br/>
<b>Live Detection Test:</b> Minor issue. Do not panic.<br/>
<br/>
<i>Unable to determine if booted into live mode or persistent mode.</i> For assistance and to report this issue, please visit:<br/>
${link}.<br/><br/>
${bug_message}"
   click="${msg_cmd} error '${title}' '${msg}' '' ok"
   echo "<click>${click}</click>"
   echo "<txtclick>${click}</txtclick>"
   echo "<tool><b>Live Detection Test:</b> Minor issue. Click on the icon for more information.</tool>"
   exit 0
fi
## lsblk command succeeded

proc_cmdline_output=$(cat /proc/cmdline)

## Manual testing examples:
#proc_cmdline_output="boot=live"
#proc_cmdline_output="root=live"
#lsblk_output=""

## Detect if the system was booted in live mode
if echo "${proc_cmdline_output}" | grep --no-messages --quiet 'boot=live' ; then
   live_mode_environment="grub-live"
   status_word="Live"
   maybe_iso_live_message=""
elif echo "${proc_cmdline_output}" | grep --no-messages --quiet 'root=live' ; then
   live_mode_environment="ISO Live"
   status_word="ISO"
   maybe_iso_live_message="<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"
fi

## Check if there are any read-write devices
if echo "$lsblk_output" | grep --quiet "0" ; then
   true "INFO: At least one '0' found. Conclusion: not all devices are read-only; some are read-write."
   if echo "${proc_cmdline_output}" | grep --no-messages --quiet 'boot=live\|root=live'; then
      true "INFO: Live mode (grub-live or ISO live) is enabled."
      if [ "$live_mode_environment" = "grub-live" ]; then
         echo "<img>${icon_grub_live_without_read_only}</img>"
         msg_type="warning"
      elif [ "$live_mode_environment" = "ISO Live" ]; then
         echo "<img>${icon_iso}</img>"
         msg_type="warning"
      else
         echo "<img>${icon_error}</img>"
         msg_type="error"
      fi
      ## Show "Live" or "ISO" next to info symbol in systray.
      echo "<txt>$status_word</txt>"
      title="Livecheck"
      link="<a href=\"${homepage}/wiki/Live_Mode\">${homepage}/wiki/Live_Mode</a>"
      msg="\
${heading_line}<br/><br/>
<b>Live Mode Active:</b> <b>Yes</b> (${live_mode_environment})<br/>
<b>Persistent Mode Active:</b> No<br/><br/>
No changes will be made to disk.
<ul>
   <li>For added security, consider <a href=\"${homepage}/wiki/Read-only\">setting your disk to read-only mode</a>.</li>
</ul>
${maybe_iso_live_message}<br/>
For more information, see: ${link}<br/><br/>
${bug_message}"
      click="${msg_cmd} ${msg_type} '${title}' '${msg}' '' ok"
      echo "<click>${click}</click>"
      echo "<txtclick>${click}</txtclick>"
      echo "<tool><b>Live Mode Active (${live_mode_environment}):</b> No changes will be made to disk. Click on the icon for more information.${maybe_iso_live_message}${bug_message}</tool>"
   else
      true "INFO: Live mode (grub-live or ISO live) is disabled."
      echo "<img>${icon_persistent_mode}</img>"
      ## Do not show "Persistent" next to info symbol in systray.
      #echo "<txt>Persistent</txt>"
      title="Livecheck"
      link="<a href=\"${homepage}/wiki/Persistent_Mode\">${homepage}/wiki/Persistent_Mode</a>"
      msg="\
${heading_line}<br/><br/>
<b>Live Mode Active:</b> No<br/>
<b>Persistent Mode Active:</b> <b>Yes</b>
<ul>
   <li>All changes to the disk will be preserved after a reboot.</li>
   <li>If you prefer a temporary session where changes are not saved, consider switching to live mode.</li>
</ul>
For more information, see: ${link}<br/><br/>
${bug_message}"
      click="${msg_cmd} info '${title}' '${msg}' '' ok"
      echo "<click>${click}</click>"
      echo "<txtclick>${click}</txtclick>"
      echo "<tool><b>Persistent Mode Active:</b> All changes to the disk will be preserved after a reboot. Click on the icon for more information.${bug_message}</tool>"
   fi
else
   true "INFO: No '0' found. Conclusion: All devices are read-only."

   echo "<img>${icon_grub_live_with_read_only}</img>"
   ## Show "read-only" next to info symbol in systray.
   echo "<txt>read-only</txt>"
   title="Livecheck"
   link="<a href=\"${homepage}/wiki/Live_Mode\">${homepage}/wiki/Live_Mode</a>"
   msg="\
${heading_line}<br/><br/>
<b>Live Mode Active:</b> <b>Yes</b> (${live_mode_environment})<br/>
<b>Persistent Mode Active:</b> No
<ul>
   <li>No changes will be made to disk.</li>
   <li>For more information, see the following link:</li>
</ul>
${link}<br/><br/>
${bug_message}"
   click="${msg_cmd} warning '${title}' '${msg}' '' ok"
   echo "<click>${click}</click>"
   echo "<txtclick>${click}</txtclick>"
   echo "<tool><b>Live Mode Active (${live_mode_environment}):</b> No changes will be made to disk. Click on the icon for more information.${bug_message}</tool>"
fi
