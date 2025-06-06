#!/bin/bash

## Copyright (C) 2018 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## Copyright (C) 2018 Algernon <33966997+Algernon-01@users.noreply.github.com>
## See the file COPYING for copying conditions.

set -o errexit
set -o nounset
set -o errtrace
set -o pipefail

## This script has been replaced by
## /usr/lib/python3/dist-packages/livecheck/livecheck.py. The following
## message exists to help users remove the now-unnecessary Generic Monitor
## widget from the panel.

output="$(cat <<EOF
<img>/usr/share/icons/gnome-colors-common/32x32/status/dialog-warning.png</img>
<tool><b>Please remove this widget.</b> Livecheck is no longer an XFCE panel widget, it is now its own application. Click for more details.</tool>
<click>/usr/libexec/msgcollector/generic_gui_messagenfo 'Livecheck' '<u><b>Please remove this widget.</b></u><br/><br/>
Livecheck is now an application, rather than an XFCE panel widget. You can find it in the system tray.<br/><br/>
To remove this widget:
<ul>
<li>Right-click on the XFCE panel.</li>
<li>Hover over "Panel", and click "Panel Preferences...".</li>
<li>Click the "Items" tab.</li>
<li>Scroll to the bottom of the list of widgets, and click on the "Generic Monitor" widget at the bottom.</li>
<li>Click "Remove".</li>
<li>In the pop-up that appears, click "Remove" again.</li>
</ul>
''' ok</click>
EOF
)"

printf '%s\n' "${output}"
