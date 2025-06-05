#!/usr/bin/python3 -u

# Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
# See the file COPYING for copying conditions.

"""
livecheck.py - Monitors the system and reports whether it is persistent,
  live, or semi-persistent.
"""
import sys
import select
import subprocess
import re

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QSystemTrayIcon,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QDialog,
)

icon_base_path = "/usr/share/icons/gnome-colors-common/32x32/status/"

loading_icon = "user-extended-away.png"
## media-optical.png isn't in the status directory, and doing this some other
## way would be a pain, so...
iso_live_mode_icon = "../devices/media-optical.png"
live_mode_icon = "user-available.png"
semi_persistent_safe_mode_icon = "dialog-warning.png"
semi_persistent_danger_mode_icon = "dialog-error.png"
persistent_mode_icon = "dialog-information.png"

kicksecure_wiki_homepage = "https://www.kicksecure.com"
text_header = "<u><b>Live Check Result:</b></u>"

loading_text = f"""{text_header}<br/>
<br/>
Livecheck is still loading information about the system's persistence state."""

iso_live_mode_text = f"""{text_header}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (ISO Live)<br/>
<b>Persistent Mode Active:</b> No
<ul>
  <li>No changes will be made to disk.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">{kicksecure_wiki_homepage}/wiki/Live_Mode</a>
<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"""

iso_semi_persistent_safe_mode_text = f"""{text_header}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (ISO Live semi-persistent)<br/>
<b>Persistent Mode Active:</b> <b>Yes</b> (removable media is mounted)
<ul>
  <li>Changes to the system will be lost after a reboot. Changes to removable media may be preserved.</li>
  <li>The following removable media directories have a writable filesystem mounted to them:
    <ul>
      XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">{kicksecure_wiki_homepage}/wiki/Live_Mode</a>
<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"""

iso_semi_persistent_danger_mode_text = f"""{text_header}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (ISO Live semi-persistent)<br/>
<b>Persistent Mode Active:</b> <b>Yes</b> (writable filesystems are mounted)
<ul>
  <li>Changes to the system should be lost after a reboot, but this is not guaranteed.</li>
  <li>The following removable media directories have a writable filesystem mounted to them:
    <ul>
      XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>The following directories have an unexpected writable filesystem mounted to them:
    <ul>
      XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>You should unmount all of the above listed directories to ensure changes made will not persist through a reboot.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">{kicksecure_wiki_homepage}/wiki/Live_Mode</a>
<br/><u>This message can be safely ignored if only using this ISO to install to the hard drive.</u><br/>"""

live_mode_text = f"""{text_header}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (grub-live)<br/>
<b>Persistent Mode Active:</b> No
<ul>
  <li>No changes will be made to disk.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">{kicksecure_wiki_homepage}/wiki/Live_Mode</a>"""

semi_persistent_safe_mode_text = f"""{text_header}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (grub-live semi-persistent)<br/>
<b>Persistent Mode Active:</b> <b>Yes</b> (removable media is mounted)
<ul>
  <li>Changes to the system will be lost after a reboot. Changes to removable media may be preserved.</li>
  <li>The following removable media directories have a writable filesystem mounted to them:
    <ul>
      XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">{kicksecure_wiki_homepage}/wiki/Live_Mode</a>"""

semi_persistent_danger_mode_text = f"""{text_header}<br/>
<br/>
<b>Live Mode Active:</b> <b>Yes</b> (grub-live semi-persistent)<br/>
<b>Persistent Mode Active:</b> <b>Yes</b> (writable filesystems are mounted)
<ul>
  <li>Changes to the system should be lost after a reboot, but this is not guaranteed.</li>
  <li>The following removable media directories have a writable filesystem mounted to them:
    <ul>
      XXX_SAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>The following directories have an unexpected writable filesystem mounted to them:
    <ul>
      XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX
    </ul>
  </li>
  <li>You should unmount all of the above listed directories to ensure changes made will not persist through a reboot.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Live_Mode">{kicksecure_wiki_homepage}/wiki/Live_Mode</a>"""

persistent_mode_text = f"""{text_header}<br/>
<br/>
<b>Live Mode Active:</b> No<br/>
<b>Persistent Mode Active:</b> <b>Yes</b>
<ul>
  <li>All changes to the disk will be preserved after a reboot.</li>
  <li>If you prefer a temporary session where changes are not saved, consider switching to live mode.</li>
  <li>For more information, see the following link:</li>
</ul>
<a href="{kicksecure_wiki_homepage}/wiki/Persistent_Mode">{kicksecure_wiki_homepage}/wiki/Persistent_Mode</a>"""

loading_tooltip = f"""Livecheck is loading information about the system's persistence state..."""

iso_live_mode_tooltip = f"""Live Mode Active (ISO Live): No changes will be made to disk. Click on the icon for more information."""

iso_semi_persistent_safe_mode_tooltip = f"""Live Mode Active (ISO Live semi-persistent): No changes will be made to the system disk. Changes to removable media will persist. Click on the icon for more information."""

iso_semi_persistent_danger_mode_tooltip = f"""Live Mode Active (ISO Live semi-persistent): Changes to the disk may be preserved after a reboot. Click on the icon for more information."""

live_mode_tooltip = f"""Live Mode Active (grub-live): No changes will be made to disk. Click on the icon for more information."""

semi_persistent_safe_mode_tooltip = f"""Live Mode Active (grub-live semi-persistent): No changes will be made to the system disk. Changes to removable media will persist. Click on the icon for more information."""

semi_persistent_danger_mode_tooltip = f"""Live Mode Active (grub-live semi-persistent): Changes to the disk may be preserved after a reboot. Click on the icon for more information."""

persistent_mode_tooltip = f"""Persistent Mode Active: All changes to the disk will be preserved after a reboot. Click on the icon for more information."""

class LiveTextWindow(QDialog):
    def __init__(self, text_str, parent=None):
        super().__init__(parent)
        self.text_str = text_str
        self.layout = QVBoxLayout(self)
        self.text = QLabel(self)
        self.buttonRow = QHBoxLayout()
        self.okButton = QPushButton(self)

        self.okButton.clicked.connect(self.done)

        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Livecheck")
        self.okButton.setText("OK")
        self.text.setText(self.text_str)
        self.buttonRow.addStretch()
        self.buttonRow.addWidget(self.okButton)
        self.layout.addWidget(self.text)
        self.layout.addSpacing(10)
        self.layout.addStretch()
        self.layout.addLayout(self.buttonRow)
        self.resize(self.minimumWidth(), self.minimumHeight())

class TrayUi(QObject):
    def __init__(self):
        super().__init__()
        self.prev_live_state = "loading"
        self.active_text = loading_text

        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(icon_base_path + loading_icon))
        self.tray_icon.setToolTip(loading_tooltip)
        self.tray_icon.activated.connect(self.show_live_mode_text_window)
        self.tray_icon.show()

        self.mount_monitor = MountMonitor()
        self.monitor_thread = QThread()

        self.mount_monitor.mountStateChanged.connect(self.update_mount_state)
        self.mount_monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.mount_monitor.run)
        self.monitor_thread.start()

    def show_live_mode_text_window(self):
        ltw = LiveTextWindow(self.active_text)
        ltw.open()

    def show_notification(self, live_mode_str):
        self.tray_icon.showMessage(
            "livecheck",
            (
                "The system's live state has changed. Current state: "
                f"'{live_mode_str}'"
            ),
        )

    @pyqtSlot(str, str, str)
    def update_mount_state(
        self,
        live_mode_str,
        safe_fs_list_str,
        danger_fs_list_str,
    ):
        ## Clean up an unsightly historical artifact from live-mode.sh
        if live_mode_str == "false":
            live_mode_str = "persistent"

        match live_mode_str:
            case "iso-live":
                self.active_text = iso_live_mode_text
                self.tray_icon.setToolTip(iso_live_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + iso_live_mode_icon)
                )
            case "iso-live-semi-persistent":
                self.active_text = (
                    iso_semi_persistent_safe_mode_text.replace(
                        "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                        safe_fs_list_str,
                    )
                )
                self.tray_icon.setToolTip(
                    iso_semi_persistent_safe_mode_tooltip
                )
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + semi_persistent_safe_mode_icon)
                )
            case "iso-live-semi-persistent-unsafe":
                self.active_text = (
                    iso_semi_persistent_danger_mode_text.replace(
                        "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                        safe_fs_list_str,
                    ).replace(
                        "XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX",
                        danger_fs_list_str,
                    )
                )
                self.tray_icon.setToolTip(
                    iso_semi_persistent_danger_mode_tooltip
                )
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + semi_persistent_danger_mode_icon)
                )
            case "grub-live":
                self.active_text = live_mode_text
                self.tray_icon.setToolTip(live_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + live_mode_icon)
                )
            case "grub-live-semi-persistent":
                self.active_text = semi_persistent_safe_mode_text.replace(
                    "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                    safe_fs_list_str,
                )
                self.tray_icon.setToolTip(semi_persistent_safe_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + semi_persistent_safe_mode_icon)
                )
            case "grub-live-semi-persistent-unsafe":
                self.active_text = semi_persistent_danger_mode_text.replace(
                    "XXX_SAFE_WRITABLE_FILESYSTEMS_XXX",
                    safe_fs_list_str,
                ).replace(
                    "XXX_UNSAFE_WRITABLE_FILESYSTEMS_XXX",
                    danger_fs_list_str,
                )
                self.tray_icon.setToolTip(semi_persistent_danger_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + semi_persistent_danger_mode_icon)
                )
            case "persistent":
                self.active_text = persistent_mode_text
                self.tray_icon.setToolTip(persistent_mode_tooltip)
                self.tray_icon.setIcon(
                    QIcon(icon_base_path + persistent_mode_icon)
                )

        if self.prev_live_state != "loading":
            if live_mode_str not in ("iso-live", "grub-live", "persistent"):
                self.show_notification(live_mode_str)
            elif self.prev_live_state not in (
                "iso-live",
                "grub-live",
                "persistent",
            ):
                self.show_notification(live_mode_str)

        self.prev_live_state = live_mode_str

class MountMonitor(QObject):
    mountStateChanged = pyqtSignal(str, str, str)

    @staticmethod
    def get_writable_fs_lists(mount_data_list):
        ## writable_fs_lists[0] is "safe" writable filesystems,
        ## writable_fs_lists[1] is dangerous ones. "Safe" writable
        ## filesystems are removable media or network filesystems mounted to
        ## /media, /mnt, or a directory under /media or /mnt. Dangerous
        ## writable filesystems are anything else writable mounted from a
        ## device or the network (i.e. nfs).
        writable_fs_lists = ([], [])
        ## Do NOT strip the string that is returned by
        ## get_writable_fs_lists.sh, as doing so may trim an important empty
        ## second line!
        writable_fs_lists_str_list = subprocess.run(
            [
                "/usr/libexec/helper-scripts/get_writable_fs_lists.sh",
            ],
            capture_output=True,
            encoding="utf-8",
        ).stdout.splitlines()

        if len(writable_fs_lists_str_list) != 2:
            return writable_fs_lists

        writable_fs_lists[0].extend(
            [x for x in writable_fs_lists_str_list[0].split(" ") if x != ""]
        )
        writable_fs_lists[1].extend(
            [x for x in writable_fs_lists_str_list[1].split(" ") if x != ""]
        )
        decode_re = re.compile(r"\\\d+")
        for wfl_idx, writable_fs_list in enumerate(writable_fs_lists):
            for wf_idx, writable_fs in enumerate(writable_fs_list):
                octal_escape_list = decode_re.findall(writable_fs)
                for octal_escape in octal_escape_list:
                    octal_str = octal_escape.strip("\\")
                    try:
                        octal_int = int(octal_str, 8)
                    except ValueError:
                        continue
                    real_char = chr(octal_int)
                    writable_fs = writable_fs.replace(octal_escape, real_char)
                    writable_fs_lists[wfl_idx][wf_idx] = writable_fs

        return writable_fs_lists

    def run(self):
        mount_file = open("/proc/self/mounts", "r", encoding="utf-8")
        mount_poll = select.poll()
        mount_poll.register(mount_file, select.POLLPRI)
        while True:
            mount_file.seek(0)
            mount_data_list = mount_file.read().splitlines()
            live_check_output = subprocess.run(
                [ "/usr/libexec/helper-scripts/live-mode.sh" ],
                capture_output=True,
                text=True,
            ).stdout.strip().splitlines()
            for line in live_check_output:
                if line.startswith(
                    "live_status_detected_live_mode_environment_machine="
                ):
                    live_mode_str = line.split("=", maxsplit=1)[1].strip(
                        "'"
                    )
                    writable_fs_lists = self.get_writable_fs_lists(
                        mount_data_list
                    )
                    safe_fs_str = ""
                    danger_fs_str = ""
                    for safe_fs in writable_fs_lists[0]:
                        safe_fs_str += f"<li>{safe_fs}</li>"
                    for danger_fs in writable_fs_lists[1]:
                        danger_fs_str += f"<li>{danger_fs}</li>"
                    if safe_fs_str == "":
                        safe_fs_str = "<li>none</li>"
                    if danger_fs_str == "":
                        danger_fs_str = "<li>none</li>"
                    self.mountStateChanged.emit(
                        live_mode_str,
                        safe_fs_str,
                        danger_fs_str,
                    )
                    break
            mount_poll.poll()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    ui = TrayUi()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
