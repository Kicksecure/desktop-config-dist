#!/usr/bin/python3 -su

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

# pylint: disable=too-many-lines

"""
livecheck.py - Monitors the system and reports whether it is persistent,
live, or semi-persistent.
"""

import signal
import sys
import select
import subprocess
import re
import functools

from pathlib import Path
from typing import Tuple, Pattern, TextIO, NoReturn
from types import FrameType

from PyQt5.QtCore import (
    Qt,
    QObject,
    QThread,
    QFileSystemWatcher,
    pyqtSignal,
    pyqtSlot,
    QTimer,
)
from PyQt5.QtGui import (
    QIcon,
    QCursor,
)
from PyQt5.QtWidgets import (
    QSystemTrayIcon,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QDialog,
    QMenu,
    QAction,
)

from term_colors.term_colors import TermColors

colors = TermColors()

installer_monitor_dir: Path = Path("/var/lib/desktop-config-dist/livecheck")
installer_monitor_file: Path = Path(
    "/var/lib/desktop-config-dist/livecheck/install-running"
)

icon_base_path: str = "/usr/share/icons/gnome-colors-common/32x32/"
loading_icon: str = "status/user-extended-away.png"
iso_live_mode_icon: str = "devices/media-optical.png"
live_mode_icon: str = "status/user-available.png"
read_only_mode_icon: str = "apps/computerjanitor.png"
semi_persistent_safe_mode_icon: str = "status/dialog-warning.png"
## These next two icons probably should be the other way around, but we've
## used dialog-error to represent "danger" for long enough I don't think we
## should change it.
##
## user-offline.png could also be used possibly? It doesn't look as "scary"
## though.
semi_persistent_danger_mode_icon: str = "status/dialog-error.png"
error_icon: str = "status/software-update-urgent.png"
installing_distribution_icon: str = "apps/system-installer.png"
persistent_mode_icon: str = "status/dialog-information.png"
exit_icon: str = "actions/application-exit.png"

kicksecure_wiki_homepage: str = "https://www.kicksecure.com"
text_header_gui: str = "<u><b>Live Check Result:</b></u>"
text_header_cli: str = (
    f"{colors.under}{colors.bold}Live Check Result:{colors.reset}"
)

## No need for a loading_text_gui variant for CLI
loading_text_gui: str = f"""{text_header_gui}<br/>
<br/>
Livecheck is still loading information about the system's persistence \
state."""

iso_live_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (ISO Live)<br/>
<b>Persistent Mode Active:</b> No
<ul>
  <li>No changes will be made to disk.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">\
{kicksecure_wiki_homepage}/wiki/Live_Mode</a>
<br/><u>This message can be safely ignored if only using this ISO to install \
to the hard drive.</u><br/>"""

iso_live_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}Live Mode Active: Yes{colors.reset} (ISO Live)
{colors.bold}Persistent Mode Active:{colors.reset} No

* No changes will be made to disk.
* For more information, see the following link:

{kicksecure_wiki_homepage}/wiki/Live_Mode

{colors.under}\
This message can be safely ignored if only using this ISO to install to the
hard drive.{colors.reset}"""

iso_semi_persistent_safe_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (ISO Live semi-persistent)<br/>
<b>Persistent Mode Active:</b> <b>Yes</b> (removable media is mounted)
<ul>
  <li>Changes to the system will be lost after a reboot. Changes to \
removable media may be preserved.</li>
  <li>The following removable media directories have a writable filesystem \
mounted to them:
    <ul>
      XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">\
{kicksecure_wiki_homepage}/wiki/Live_Mode</a>
<br/><u>This message can be safely ignored if only using this ISO to install \
to the hard drive.</u><br/>"""

iso_semi_persistent_safe_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}Live Mode Active: Yes{colors.reset} \
(ISO Live semi-persistent)
{colors.bold}\
Persistent Mode Active: Yes{colors.reset} (removable media is mounted)

* Changes to the system will be lost after a reboot. Changes to removable
  media may be preserved.
* The following removable media directories have a writable filesystem mounted
  to them:
XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
* For more information, see the following link:

{kicksecure_wiki_homepage}/wiki/Live_Mode

{colors.under}\
This message can be safely ignored if only using this ISO to install to the
hard drive.{colors.reset}"""

iso_semi_persistent_danger_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (ISO Live semi-persistent)<br/>
<b>Persistent Mode Active:</b> <b>Yes</b> (writable filesystems are mounted)
<ul>
  <li>Changes to the system should be lost after a reboot, but this is not \
guaranteed.</li>
  <li>The following removable media directories have a writable filesystem \
mounted to them:
    <ul>
      XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>The following directories have an unexpected writable filesystem \
mounted to them:
    <ul>
      XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>You should unmount all of the above listed directories to ensure \
changes made will not persist through a reboot.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">\
{kicksecure_wiki_homepage}/wiki/Live_Mode</a>
<br/><u>This message can be safely ignored if only using this ISO to install \
to the hard drive.</u><br/>"""

iso_semi_persistent_danger_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}Live Mode Active: Yes{colors.reset} (ISO Live semi-persistent)
{colors.bold}Persistent Mode Active: Yes{colors.reset} \
(writable filesystems are mounted)

* Changes to the system should be lost after a reboot, but this is
  not guaranteed.
* The following removable media directories have a writable filesystem mounted
  to them:
XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
* The following directories have an unexpected writable filesystem mounted
  to them:
XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX
* You should unmount all of the above listed directories to ensure changes
  made will not persist through a reboot.
* For more information, see the following link:

{kicksecure_wiki_homepage}/wiki/Live_Mode

{colors.under}\
This message can be safely ignored if only using this ISO to install to the
hard drive.{colors.reset}"""

live_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (grub-live)<br/>
<b>Persistent Mode Active:</b> No
<ul>
  <li>No changes will be made to disk.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">\
{kicksecure_wiki_homepage}/wiki/Live_Mode</a>"""

live_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}Live Mode Active: Yes{colors.reset} (grub-live)
{colors.bold}Persistent Mode Active:{colors.reset} No

* No changes will be made to disk.
* For more information, see the following link:

{kicksecure_wiki_homepage}/wiki/Live_Mode"""

read_only_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (grub-live read-only)<br/>
<b>Persistent Mode Active:</b> No
<ul>
  <li>No changes will be made to disk.</li>
  <li>All storage media available to the OS is set read-only by hardware or \
drivers.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">\
{kicksecure_wiki_homepage}/wiki/Live_Mode</a>"""

read_only_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}Live Mode Active: Yes{colors.reset} (grub-live read-only)
{colors.bold}Persistent Mode Active:{colors.reset} No

* No changes will be made to disk.
* All storage media available to the OS is set read-only by hardware
  or drivers.
* For more information, see the following link:

{kicksecure_wiki_homepage}/wiki/Live_Mode"""

semi_persistent_safe_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (grub-live semi-persistent)<br/>
<b>Persistent Mode Active:</b> <b>Yes</b> (removable media is mounted)
<ul>
  <li>Changes to the system will be lost after a reboot. Changes to \
removable media may be preserved.</li>
  <li>The following removable media directories have a writable filesystem \
mounted to them:
    <ul>
      XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">\
{kicksecure_wiki_homepage}/wiki/Live_Mode</a>"""

semi_persistent_safe_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}Live Mode Active: Yes{colors.reset} (grub-live semi-persistent)
{colors.bold}Persistent Mode Active: Yes{colors.reset} \
(removable media is mounted)

* Changes to the system will be lost after a reboot. Changes to removable
  media may be preserved.
* The following removable media directories have a writable filesystem mounted
  to them:
XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
* For more information, see the following link:

{kicksecure_wiki_homepage}/wiki/Live_Mode"""

semi_persistent_danger_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (grub-live semi-persistent)<br/>
<b>Persistent Mode Active:</b> <b>Yes</b> (writable filesystems are mounted)
<ul>
  <li>Changes to the system should be lost after a reboot, but this is not \
guaranteed.</li>
  <li>The following removable media directories have a writable filesystem \
mounted to them:
    <ul>
      XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>The following directories have an unexpected writable filesystem \
mounted to them:
    <ul>
      XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>You should unmount all of the above listed directories to ensure \
changes made will not persist through a reboot.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">\
{kicksecure_wiki_homepage}/wiki/Live_Mode</a>"""

semi_persistent_danger_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}Live Mode Active: Yes{colors.reset} (grub-live semi-persistent)
{colors.bold}Persistent Mode Active: Yes{colors.reset} \
(writable filesystems are mounted)

* Changes to the system should be lost after a reboot, but this is
  not guaranteed.
* The following removable media directories have a writable filesystem mounted
  to them:
XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
* The following directories have an unexpected writable filesystem mounted
  to them:
XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX
* You should unmount all of the above listed directories to ensure changes
  made will not persist through a reboot.
* For more information, see the following link:

{kicksecure_wiki_homepage}/wiki/Live_Mode"""

installing_distribution_text_gui: str = f"""{text_header_gui}<br/>
<br/>
The system installer is currently installing this operating system."""

installing_distribution_text_cli: str = f"""{text_header_cli}

The system installer is currently installing this operating system."""

persistent_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b>Live Mode Active:</b> No<br/>
<b>Persistent Mode Active:</b> <b>Yes</b>
<ul>
  <li>All changes to the disk will be preserved after a reboot.</li>
  <li>If you prefer a temporary session where changes are not saved, \
consider switching to live mode.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Persistent_Mode">\
{kicksecure_wiki_homepage}/wiki/Persistent_Mode</a>"""

persistent_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}Live Mode Active:{colors.reset} No
{colors.bold}Persistent Mode Active: Yes{colors.reset}

* All changes to the disk will be preserved after a reboot.
* If you prefer a temporary session where changes are not saved, consider
  switching to live mode.
* For more information, see the following link:

{kicksecure_wiki_homepage}/wiki/Persistent_Mode"""

error_live_mode_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b><font color="red">ERROR</font></b>: The system's live state cannot be \
determined!<br/>
<br/>
Technical information: The script \
<code>/usr/libexec/helper-scripts/live-mode.sh</code> exited with code \
'XXX_EXIT_CODE_XXX'.<br/>
<br/>
<code>live-mode.sh</code> output:
<pre>
XXX_SCRIPT_OUTPUT_XXX</pre>
Please report this bug!"""

error_live_mode_text_cli: str = f"""{text_header_cli}

{colors.bold}{colors.red}ERROR{colors.reset}: The system's live state cannot \
be determined!

Technical details: The script '/usr/libexec/helper-scripts/live-mode.sh' exited
with code 'XXX_EXIT_CODE_XXX'.

'live-mode.sh' output:
XXX_SCRIPT_OUTPUT_XXX
Please report this bug!"""

error_gwfl_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b><font color="red">ERROR</font></b>: The system's live state cannot be \
determined!<br/>
<br/>
Technical information: The script \
<code>/usr/libexec/helper-scripts/get_writable_fs_lists.sh</code> exited \
with code 'XXX_EXIT_CODE_XXX'.<br/>
<br/>
<code>get_writable_fs_lists.sh</code> output:
<pre>
XXX_SCRIPT_OUTPUT_XXX</pre>
Please report this bug!"""

error_gwfl_text_cli: str = f"""{text_header_cli}

{colors.bold}{colors.red}ERROR{colors.reset}: The system's live state cannot \
be determined!

Technical details: The script
'/usr/libexec/helper-scripts/get_writable_fs_lists.sh' exited with code \
'XXX_EXIT_CODE_XXX'.

'get_writable_fs_lists.sh' output:
XXX_SCRIPT_OUTPUT_XXX
Please report this bug!"""

error_live_mode_invalid_output_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b><font color="red">ERROR</font></b>: The system's live state cannot be \
determined!<br/>
<br/>
Technical information: The script \
<code>/usr/libexec/helper-scripts/live-mode.sh</code> ran successfully, but \
its output could not be parsed.<br/>
<br/>
<code>live-mode.sh</code> output:
<pre>
XXX_SCRIPT_OUTPUT_XXX</pre>
Please report this bug!"""

error_live_mode_invalid_output_text_cli: str = f"""{text_header_cli}

{colors.bold}{colors.red}ERROR{colors.reset}: The system's live state cannot \
be determined!

Technical details: The script '/usr/libexec/helper-scripts/live-mode.sh' ran
successfully, but its output could not be parsed.

'live-mode.sh' output:
XXX_SCRIPT_OUTPUT_XXX
Please report this bug!"""

error_gwfl_invalid_output_text_gui: str = f"""{text_header_gui}<br/>
<br/>
<b><font color="red">ERROR</font></b>: The system's live state cannot be \
determined!<br/>
<br/>
Technical information: The script \
<code>/usr/libexec/helper-scripts/get_writable_fs_lists.sh</code> ran \
successfully, but its output could not be parsed.<br/>
<br/>
<code>get_writable_fs_lists.sh</code> output:
<pre>
XXX_SCRIPT_OUTPUT_XXX</pre>
Please report this bug!"""

error_gwfl_invalid_output_text_cli: str = f"""{text_header_cli}

{colors.bold}{colors.red}ERROR{colors.reset}: The system's live state cannot \
be determined!

Technical details: The script
'/usr/libexec/helper-scripts/get_writable_fs_lists.sh' ran successfully, but
its output could not be parsed.

'get_writable_fs_lists.sh' output:
XXX_SCRIPT_OUTPUT_XXX
Please report this bug!"""

loading_tooltip: str = """Livecheck is loading information about the \
system's persistence state..."""

iso_live_mode_tooltip: str = """Live Mode Active (ISO Live): No changes \
will be made to disk. Click on the icon for more information."""

iso_semi_persistent_safe_mode_tooltip: str = """Live Mode Active (ISO Live \
semi-persistent): No changes will be made to the system disk. Changes to \
removable media will persist. Click on the icon for more information."""

iso_semi_persistent_danger_mode_tooltip: str = """Live Mode Active (ISO \
Live semi-persistent): Changes to the disk may be preserved after a reboot. \
Click on the icon for more information."""

live_mode_tooltip: str = """Live Mode Active (grub-live): No changes will \
be made to disk. Click on the icon for more information."""

read_only_mode_tooltip: str = """Live Mode Active (grub-live read-only): No \
changes will be made to disk. Click on the icon for more information."""

semi_persistent_safe_mode_tooltip: str = """Live Mode Active (grub-live \
semi-persistent): No changes will be made to the system disk. Changes to \
removable media will persist. Click on the icon for more information."""

semi_persistent_danger_mode_tooltip: str = """Live Mode Active (grub-live \
semi-persistent): Changes to the disk may be preserved after a reboot. Click \
on the icon for more information."""

installing_distribution_tooltip: str = """The system installer is currently \
installing this operating system."""

persistent_mode_tooltip: str = """Persistent Mode Active: All changes to \
the disk will be preserved after a reboot. Click on the icon for more \
information."""

error_live_state_tooltip: str = """ERROR: The system's live state cannot be \
determined. Click on the icon for more information."""


class LiveTextWindow(QDialog):
    """
    Popup window that appears when the Livecheck system tray icon is clicked.
    Describes the system's "live" state to the user.
    """

    def __init__(self, text_str: str, parent: QDialog | None = None) -> None:
        """
        Init function.
        """

        super().__init__(parent)
        self.text_str: str = text_str
        self.main_layout: QVBoxLayout = QVBoxLayout(self)
        self.text: QLabel = QLabel(self)
        self.button_row: QHBoxLayout = QHBoxLayout()
        self.ok_button: QPushButton = QPushButton(self)

        self.ok_button.clicked.connect(self.done)

        self.setupUi()

    # pylint: disable=invalid-name
    def setupUi(self) -> None:
        """
        Configures the UI elements of the window.
        """

        self.setWindowTitle("Livecheck")
        self.ok_button.setText("OK")
        self.text.setOpenExternalLinks(True)
        self.text.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse
        )
        self.text.setText(self.text_str)
        self.button_row.addStretch()
        self.button_row.addWidget(self.ok_button)
        self.main_layout.addWidget(self.text)
        self.main_layout.addSpacing(10)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.button_row)
        self.resize(self.minimumWidth(), self.minimumHeight())


# pylint: disable=too-many-instance-attributes
class TrayUi(QObject):
    """
    The system tray icon of Livecheck. Displays an icon summarizing the
    system's "live" state at a glance. If the icon is clicked, pops up a
    LiveTextWindow with more detailed information.
    """

    def __init__(self) -> None:
        """
        Init function.
        """

        super().__init__()
        self.prev_live_state: str = "loading"
        self.active_text: str = loading_text_gui

        self.tray_icon: QSystemTrayIcon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(icon_base_path + loading_icon))
        self.tray_icon.setToolTip(loading_tooltip)
        self.tray_icon.activated.connect(self.handle_systray_click)
        tray_menu: QMenu = QMenu()
        quit_action: QAction = QAction(
            QIcon(icon_base_path + exit_icon),
            "&Exit",
            self,
        )
        quit_action.triggered.connect(sys.exit)
        tray_menu.addAction(quit_action)
        tray_menu.addSeparator()
        livecheck_text_action: QAction = QAction(
            "Livecheck",
            self,
        )
        livecheck_text_action.setEnabled(False)
        tray_menu.addAction(livecheck_text_action)
        self.is_window_open: bool = False
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        ## These strings are used to store the last received mount data from
        ## the MountChecker thread. This is primarily so that if something
        ## other than the MountChecker thread has to override the live status
        ## data (i.e. the QFileSystemWatcher that checks for an "install in
        ## progress" flag file from Calamares), we can restore the correct
        ## mount information once the overriding condition is cleared.
        self.live_mode_str: str = ""
        ## live_check_str_one is either the safe FS list, or the error output
        ## of the live-mode.sh or get_writable_fs_lists.sh script.
        self.live_check_str_one: str = ""
        ## live_check_str_two is either the unsafe FS list, or the exit code
        ## of the live-mode.sh or get_writable_fs_lists.sh script.
        self.live_check_str_two: str = ""

        self.os_install_active: bool = False
        self.os_install_checker: QFileSystemWatcher = QFileSystemWatcher(
            [str(installer_monitor_dir)]
        )
        self.os_install_checker.directoryChanged.connect(
            self.install_monitor_dir_changed
        )

        self.mount_checker: MountChecker = MountChecker()
        self.monitor_thread: QThread = QThread()

        self.mount_checker.mountStateChanged.connect(self.update_mount_state)
        self.mount_checker.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.mount_checker.monitor)
        self.monitor_thread.start()
        print("INFO: Livecheck started.", file=sys.stderr)

    def handle_systray_click(
        self,
        reason: QSystemTrayIcon.ActivationReason,
    ) -> None:
        """
        Pops up either a context menu or a LiveTextWindow when the systray
        icon is right- or left-clicked, respectively.
        """

        if reason == QSystemTrayIcon.ActivationReason.Context:
            self.show_context_menu()
        else:
            self.show_live_mode_text_window()

    def show_context_menu(self) -> None:
        """
        Displays the context menu.
        """

        context_menu: QMenu | None = self.tray_icon.contextMenu()
        assert context_menu is not None
        context_menu.popup(QCursor.pos())

    def record_window_closed(self) -> None:
        """
        Event handler, marks the LiveTextWindow as closed when the user closes
        it (this is used to prevent multiple LiveTextWindows being open at
        once).
        """

        self.is_window_open = False

    def show_live_mode_text_window(self) -> None:
        """
        Pops up a LiveTextWindow if it isn't open already.
        """

        if not self.is_window_open:
            ltw: LiveTextWindow = LiveTextWindow(self.active_text)
            ltw.finished.connect(functools.partial(self.record_window_closed))
            ltw.open()
            self.is_window_open = True

    @staticmethod
    def show_notification(live_mode_str: str, is_first_popup: bool) -> None:
        """
        Shows a passive notification when the system's live state changes.
        Uses notify-send, as using Qt's notification functions sometimes
        resulted in theme issues.
        """

        ## TODO: Should we have more user-friendly identifiers for the live
        ## states? Maybe "Installing distribution" would be nicer than
        ## "installing-distribution", for instance?
        if is_first_popup:
            subprocess.run(
                [
                    "/usr/bin/notify-send",
                    "livecheck",
                    f"The system's live state is '{live_mode_str}'.",
                ],
                check=False,
            )
        else:
            subprocess.run(
                [
                    "/usr/bin/notify-send",
                    "livecheck",
                    "The system's live state has changed. Current state: "
                    + f"'{live_mode_str}'.",
                ],
                check=False,
            )

    def install_monitor_dir_changed(self) -> None:
        """
        Event handler, called when the installer monitor directory changes.
        This directory has a flag file dropped into it when OS installation
        starts; this triggers Livecheck to inform the user that an OS is being
        installed rather than warning about unsafe directories being mounted.
        """

        if installer_monitor_file.is_file():
            print(
                "INFO: Installer monitor file "
                f"('{str(installer_monitor_file)}') was written by an "
                "external process.",
                file=sys.stderr,
            )
            self.os_install_active = True
            self.update_mount_state("installing-distribution", "", "")
        else:
            print(
                "INFO: Installer monitor file "
                f"('{str(installer_monitor_file)}') was deleted by an "
                "external process.",
                file=sys.stderr,
            )
            self.os_install_active = False
            self.update_mount_state(
                self.live_mode_str,
                self.live_check_str_one,
                self.live_check_str_two,
            )

    # pylint: disable=too-many-statements
    @pyqtSlot(str, str, str)
    def update_mount_state(
        self,
        live_mode_str: str,
        live_check_str_one: str,
        live_check_str_two: str,
    ) -> None:
        """
        Event handler, called whenever filesystem mounts change. Updates the
        system's "live" state from Livecheck's perspective.
        """

        print("INFO: Mount state updated.", file=sys.stderr)
        print(f"INFO: live_mode_str: '{live_mode_str}'", file=sys.stderr)
        print(
            f"INFO: live_check_str_one: '{live_check_str_one}'",
            file=sys.stderr,
        )
        print(
            f"INFO: live_check_str_two: '{live_check_str_two}'",
            file=sys.stderr,
        )

        ## Clean up an unsightly historical artifact from live-mode.sh
        if live_mode_str == "false":
            live_mode_str = "persistent"

        if live_mode_str != "installing-distribution":
            self.live_mode_str = live_mode_str
            self.live_check_str_one = live_check_str_one
            self.live_check_str_two = live_check_str_two

            if self.os_install_active:
                return

        match live_mode_str:
            case "iso-live":
                self.active_text = iso_live_mode_text_gui
                self.tray_icon.setToolTip(iso_live_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + iso_live_mode_icon)
                )
            case "iso-live-semi-persistent":
                self.active_text = (
                    iso_semi_persistent_safe_mode_text_gui.replace(
                        "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                        live_check_str_one,
                    )
                )
                self.tray_icon.setToolTip(iso_semi_persistent_safe_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + semi_persistent_safe_mode_icon)
                )
            case "iso-live-semi-persistent-unsafe":
                self.active_text = (
                    iso_semi_persistent_danger_mode_text_gui.replace(
                        "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                        live_check_str_one,
                    ).replace(
                        "XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX",
                        live_check_str_two,
                    )
                )
                self.tray_icon.setToolTip(
                    iso_semi_persistent_danger_mode_tooltip
                )
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + semi_persistent_danger_mode_icon)
                )
            case "grub-live":
                self.active_text = live_mode_text_gui
                self.tray_icon.setToolTip(live_mode_tooltip)
                self.tray_icon.setIcon(QIcon(icon_base_path + live_mode_icon))
            case "grub-live-read-only":
                self.active_text = read_only_mode_text_gui
                self.tray_icon.setToolTip(read_only_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + read_only_mode_icon)
                )
            case "grub-live-semi-persistent":
                self.active_text = semi_persistent_safe_mode_text_gui.replace(
                    "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_one,
                )
                self.tray_icon.setToolTip(semi_persistent_safe_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + semi_persistent_safe_mode_icon)
                )
            case "grub-live-semi-persistent-unsafe":
                self.active_text = semi_persistent_danger_mode_text_gui.replace(
                    "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_one,
                ).replace(
                    "XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_two,
                )
                self.tray_icon.setToolTip(semi_persistent_danger_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + semi_persistent_danger_mode_icon)
                )
            case "installing-distribution":
                self.active_text = installing_distribution_text_gui
                self.tray_icon.setToolTip(installing_distribution_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + installing_distribution_icon)
                )
            case "persistent":
                self.active_text = persistent_mode_text_gui
                self.tray_icon.setToolTip(persistent_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + persistent_mode_icon)
                )
            case "error-live-mode":
                self.active_text = error_live_mode_text_gui.replace(
                    "XXX_SCRIPT_OUTPUT_XXX",
                    live_check_str_one,
                ).replace(
                    "XXX_EXIT_CODE_XXX",
                    live_check_str_two,
                )
                self.tray_icon.setToolTip(error_live_state_tooltip)
                self.tray_icon.setIcon(QIcon(icon_base_path + error_icon))
            case "error-get-writable-fs-lists":
                self.active_text = error_gwfl_text_gui.replace(
                    "XXX_SCRIPT_OUTPUT_XXX",
                    live_check_str_one,
                ).replace(
                    "XXX_EXIT_CODE_XXX",
                    live_check_str_two,
                )
                self.tray_icon.setToolTip(error_live_state_tooltip)
                self.tray_icon.setIcon(QIcon(icon_base_path + error_icon))
            case "error-live-mode-invalid-output":
                self.active_text = (
                    error_live_mode_invalid_output_text_gui.replace(
                        "XXX_SCRIPT_OUTPUT_XXX",
                        live_check_str_one,
                    )
                )
                self.tray_icon.setToolTip(error_live_state_tooltip)
                self.tray_icon.setIcon(QIcon(icon_base_path + error_icon))
            case "error-get-writable-fs-lists-invalid-output":
                self.active_text = error_gwfl_invalid_output_text_gui.replace(
                    "XXX_SCRIPT_OUTPUT_XXX",
                    live_check_str_one,
                )
                self.tray_icon.setToolTip(error_live_state_tooltip)
                self.tray_icon.setIcon(QIcon(icon_base_path + error_icon))

        if self.prev_live_state != "loading":
            if live_mode_str not in ("iso-live", "grub-live", "persistent"):
                self.show_notification(live_mode_str, False)
            elif self.prev_live_state not in (
                "iso-live",
                "grub-live",
                "persistent",
            ):
                self.show_notification(live_mode_str, False)
        elif live_mode_str != "persistent":
            self.show_notification(live_mode_str, True)

        self.prev_live_state = live_mode_str


class MountChecker(QObject):
    """
    Watches for changes to the system's mount points so the "live" state can
    be tracked.
    """

    mountStateChanged = pyqtSignal(str, str, str)

    @staticmethod
    def get_writable_fs_lists() -> Tuple[int, list[str] | str, list[str] | str]:
        """
        Gets a list of writable filesystem mounts on the system, separated
        into "safe" and "unsafe" groups. "Safe" writable filesystems are
        removable media or network filesystems mounted to /media, /mnt, or a
        directory under /media or /mnt. Dangerous writable filesystems are
        anything else writable mounted from a device or the network (i.e.
        nfs).

        The first returned value is the integer '0' on success, '1' on
        failure, or '2' if the script succeeded but its output could not be
        processed. The second value is either a list of safe writable
        filesystems, or the output of the script if an error was encountered.
        The third value is either a list of unsafe writable filesystems, or
        the exit code of the script if an error was encountered.
        """

        safe_writable_fs_list: list[str] = []
        unsafe_writable_fs_list: list[str] = []
        gwfl_proc: subprocess.CompletedProcess[str] = subprocess.run(
            [
                "/usr/libexec/helper-scripts/get_writable_fs_lists.sh",
            ],
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        if gwfl_proc.returncode != 0:
            return (
                1,
                gwfl_proc.stderr + gwfl_proc.stdout,
                str(gwfl_proc.returncode),
            )
        ## Do NOT strip the string that is returned by
        ## get_writable_fs_lists.sh, as doing so may trim an important empty
        ## second line!
        writable_fs_lists_str_list: list[str] = gwfl_proc.stdout.splitlines()

        if len(writable_fs_lists_str_list) != 2:
            return (
                2,
                gwfl_proc.stderr + gwfl_proc.stdout,
                str(gwfl_proc.returncode),
            )

        safe_writable_fs_list.extend(
            [x for x in writable_fs_lists_str_list[0].split(" ") if x != ""]
        )
        unsafe_writable_fs_list.extend(
            [x for x in writable_fs_lists_str_list[1].split(" ") if x != ""]
        )
        decode_re: Pattern[str] = re.compile(r"\\\d+")
        for wfl_idx, writable_fs_list in enumerate(
            (safe_writable_fs_list, unsafe_writable_fs_list)
        ):
            for wf_idx, writable_fs in enumerate(writable_fs_list):
                octal_escape_list: list[str] = decode_re.findall(writable_fs)
                for octal_escape in octal_escape_list:
                    octal_str: str = octal_escape.strip("\\")
                    try:
                        octal_int: int = int(octal_str, 8)
                    except ValueError:
                        continue
                    real_char: str = chr(octal_int)
                    writable_fs = writable_fs.replace(octal_escape, real_char)
                if wfl_idx == 0:
                    safe_writable_fs_list[wf_idx] = writable_fs
                elif wfl_idx == 1:
                    unsafe_writable_fs_list[wf_idx] = writable_fs

        return (0, safe_writable_fs_list, unsafe_writable_fs_list)

    # pylint: disable=too-many-branches
    @staticmethod
    def get_live_state_info(in_cli_mode: bool) -> Tuple[str, str, str]:
        """
        Gets info about the system's live state. On success, returns the live
        state, a formatted list of safe writable filesystems, and a formatted
        list of unsafe writable filesystems. On failure, returns one of the
        following:

            * ("error-live-mode", output_of_live_mode,
              return_code_of_live_mode). This is returned if the live-mode.sh
              script errors out.
            * ("error-get-writable-fs-lists", output_of_get_writable_fs_lists,
              return_code_of_get_writable_fs_lists). Same as above, but for
              get-writable-fs-lists.sh.
            * ("error-live-mode-invalid-output", output_of_live_mode, "0").
              This is returned if the live-mode.sh script does not error out,
              but its output cannot be processed.
            * ("error-get-writable-fs-lists-invalid-output",
              output_of_get_writable_fs_lists,
              return_code_of_get_writable_fs_lists). Same as above, but for
              get-writable-fs-lists.sh.

        The argument (in_cli_mode) dictates whether the strings containing the
        filesystem lists are formatted using HTML or plain-text. HTML is
        suitable for GUI display, while plain text can be embedded into
        the CLI.
        """

        live_check_process: subprocess.CompletedProcess[str] = subprocess.run(
            ["/usr/libexec/helper-scripts/live-mode.sh"],
            capture_output=True,
            text=True,
            check=False,
        )
        if live_check_process.returncode != 0:
            return (
                "error-live-mode",
                live_check_process.stderr + live_check_process.stdout,
                str(live_check_process.returncode),
            )
        live_check_output: list[str] = (
            live_check_process.stdout.strip().splitlines()
        )

        for line in live_check_output:
            if line.startswith(
                "live_status_detected_live_mode_environment_machine="
            ):
                live_mode_str: str = line.split("=", maxsplit=1)[1].strip("'")
                writable_fs_list_data: Tuple[
                    int, list[str] | str, list[str] | str
                ] = MountChecker.get_writable_fs_lists()
                if writable_fs_list_data[0] == 1:
                    assert isinstance(writable_fs_list_data[1], str)
                    assert isinstance(writable_fs_list_data[2], str)
                    return (
                        "error-get-writable-fs-lists",
                        writable_fs_list_data[1],
                        writable_fs_list_data[2],
                    )
                if writable_fs_list_data[0] == 2:
                    assert isinstance(writable_fs_list_data[1], str)
                    assert isinstance(writable_fs_list_data[2], str)
                    return (
                        "error-get-writable-fs-lists-invalid-output",
                        writable_fs_list_data[1],
                        writable_fs_list_data[2],
                    )
                assert isinstance(writable_fs_list_data[1], list)
                assert isinstance(writable_fs_list_data[2], list)
                safe_fs_str: str = ""
                danger_fs_str: str = ""
                if in_cli_mode:
                    for safe_fs in writable_fs_list_data[1]:
                        safe_fs_str += f"  - {safe_fs}\n"
                    for danger_fs in writable_fs_list_data[2]:
                        danger_fs_str += f"  - {danger_fs}\n"
                    if safe_fs_str == "":
                        safe_fs_str = "  - none"
                    if danger_fs_str == "":
                        danger_fs_str = "  - none"
                    safe_fs_str = safe_fs_str.strip("\n")
                    danger_fs_str = danger_fs_str.strip("\n")
                else:
                    for safe_fs in writable_fs_list_data[1]:
                        safe_fs_str += f"<li>{safe_fs}</li>"
                    for danger_fs in writable_fs_list_data[2]:
                        danger_fs_str += f"<li>{danger_fs}</li>"
                    if safe_fs_str == "":
                        safe_fs_str = "<li>none</li>"
                    if danger_fs_str == "":
                        danger_fs_str = "<li>none</li>"
                return (live_mode_str, safe_fs_str, danger_fs_str)
        return (
            "error-live-mode-invalid-output",
            live_check_process.stderr + live_check_process.stdout,
            "0",
        )

    def monitor(self) -> None:
        """
        Monitors the system for mount changes. This function is blocking and
        does not terminate, so it must be run in a separate thread. This is
        only for use in Livecheck's GUI mode.
        """

        # pylint: disable=consider-using-with
        mount_file: TextIO = open("/proc/self/mounts", "r", encoding="utf-8")
        mount_poll: select.poll = select.poll()
        ## According to `man proc_pid_mounts`:
        ##
        ## Since Linux 2.6.15, this file [/proc/self/mounts] is pollable;
        ## after opening the file for reading, a change in this file (i.e. a
        ## filesystem mount or unmount) causes select(2) to mark the file
        ## descriptor as having an exceptional condition, and poll(s) and
        ## epoll_wait(2) mark the file as having a priority event (POLLPRI).
        mount_poll.register(mount_file, select.POLLPRI)
        while True:
            mount_file.seek(0)
            mount_file.read()
            live_state_info: Tuple[str, str, str] = self.get_live_state_info(
                in_cli_mode=False
            )
            self.mountStateChanged.emit(
                live_state_info[0],
                live_state_info[1],
                live_state_info[2],
            )
            mount_poll.poll()


# pylint: disable=unused-argument
def signal_handler(sig: int, frame: FrameType | None) -> None:
    """
    Handles signals.
    """

    print(f"INFO: Signal '{sig}' received, exiting.", file=sys.stderr)
    sys.exit(128 + sig)


def main_gui() -> NoReturn:
    """
    Launches the Livecheck GUI.
    """

    app: QApplication = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    timer: QTimer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    # pylint: disable=unused-variable
    ui: TrayUi = TrayUi()
    app.exec_()
    sys.exit(0)


def main_cli() -> NoReturn:
    """
    Gets information about the system's live state in one shot and prints it
    to stdout.
    """

    live_state_info: Tuple[str, str, str] = MountChecker.get_live_state_info(
        in_cli_mode=True
    )
    live_mode_str: str = live_state_info[0]
    ## See TrayUi constructor for a description of the contents of
    ## live_check_str_one and live_check_str_two.
    live_check_str_one: str = live_state_info[1]
    live_check_str_two: str = live_state_info[2]

    ## Clean up an unsightly historical artifact from live-mode.sh
    if live_mode_str == "false":
        live_mode_str = "persistent"

    ## Check to see if the distribution is being installed
    if installer_monitor_file.is_file():
        live_mode_str = "installing-distribution"

    match live_mode_str:
        case "iso-live":
            print(iso_live_mode_text_cli)
        case "iso-live-semi-persistent":
            print(
                iso_semi_persistent_safe_mode_text_cli.replace(
                    "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_one,
                )
            )
        case "iso-live-semi-persistent-unsafe":
            print(
                iso_semi_persistent_danger_mode_text_cli.replace(
                    "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_one,
                ).replace(
                    "XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_two,
                )
            )
        case "grub-live":
            print(live_mode_text_cli)
        case "grub-live-read-only":
            print(read_only_mode_text_cli)
        case "grub-live-semi-persistent":
            print(
                semi_persistent_safe_mode_text_cli.replace(
                    "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_one,
                )
            )
        case "grub-live-semi-persistent-unsafe":
            print(
                semi_persistent_danger_mode_text_cli.replace(
                    "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_one,
                ).replace(
                    "XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX",
                    live_check_str_two,
                )
            )
        case "installing-distribution":
            print(installing_distribution_text_cli)
        case "persistent":
            print(persistent_mode_text_cli)
        case "error-live-mode":
            print(
                error_live_mode_text_cli.replace(
                    "XXX_SCRIPT_OUTPUT_XXX",
                    live_check_str_one,
                ).replace(
                    "XXX_EXIT_CODE_XXX",
                    live_check_str_two,
                )
            )
        case "error-get-writable-fs-lists":
            print(
                error_gwfl_text_cli.replace(
                    "XXX_SCRIPT_OUTPUT_XXX",
                    live_check_str_one,
                ).replace(
                    "XXX_EXIT_CODE_XXX",
                    live_check_str_two,
                )
            )
        case "error-live-mode-invalid-output":
            print(
                error_live_mode_invalid_output_text_cli.replace(
                    "XXX_SCRIPT_OUTPUT_XXX",
                    live_check_str_one,
                )
            )
        case "error-get-writable-fs-lists-invalid-output":
            print(
                error_gwfl_invalid_output_text_cli.replace(
                    "XXX_SCRIPT_OUTPUT_XXX",
                    live_check_str_one,
                )
            )

    if live_mode_str.startswith("error-"):
        sys.exit(1)
    sys.exit(0)


def main() -> NoReturn:
    """
    Main function. Dispatches to either main_gui or main_cli.
    """

    if len(sys.argv) < 2:
        print(
            "ERROR: No argument provided, either '--gui' or '--cli' must be "
            "specified!",
            file=sys.stderr,
        )
        sys.exit(1)
    if sys.argv[1] == "--gui":
        main_gui()
    elif sys.argv[1] == "--cli":
        main_cli()
    print(
        f"ERROR: Unrecognied argument '{sys.argv[1]}', expected either "
        "'--gui' or '--cli'!",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
