#!/usr/bin/python3 -su

## Copyright (C) 2025 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

# pylint: disable=broad-exception-caught

"""
backlight_tool_dist.py - GUI utility for adjusting backlight brightness.
"""

import sys
import subprocess
import signal
import functools
import traceback
from typing import NoReturn
from types import FrameType
from PyQt5.QtCore import (
    Qt,
    QTimer,
)
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QGroupBox,
)


# pylint: disable=too-few-public-methods
class ErrorWindow(QDialog):
    """
    Error message window.
    """

    def __init__(self, error_text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.resize(300, 200)
        self.setWindowTitle("Backlight Tool")
        self.root_layout: QVBoxLayout = QVBoxLayout()
        self.error_label: QLabel = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse
        )
        self.error_label.setText(error_text)
        self.button_layout: QHBoxLayout = QHBoxLayout()
        self.exit_button: QPushButton = QPushButton()
        self.exit_button.setText("Exit")
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.exit_button)
        self.root_layout.addWidget(self.error_label)
        self.root_layout.addStretch()
        self.root_layout.addLayout(self.button_layout)
        self.setLayout(self.root_layout)
        self.exit_button.clicked.connect(functools.partial(self.done, 0))


# pylint: disable=too-many-instance-attributes, too-many-statements
class BacklightToolWindow(QDialog):
    """
    Core backlight_tool_dist window.
    """

    def __init__(self, bright_int: int, parent: QWidget | None = None) -> None:
        """
        BacklightToolWindow constructor.
        """

        super().__init__(parent)

        if bright_int < 1 or bright_int > 100:
            self.error_window: ErrorWindow = ErrorWindow(
                "The system reported an incorrect brightness percentage of"
                f"'{bright_int}'!<br>"
                "<br>"
                "Please report this bug!"
            )
            self.error_window.exec_()
            sys.exit(1)

        self.bright_int = bright_int

        self.setWindowFlags(Qt.Window)

        self.resize(500, 200)
        self.setWindowTitle("Backlight Tool")

        self.brightness_label: QLabel = QLabel()
        self.brightness_label.setText("Brightness")
        self.slider_group_box: QGroupBox = QGroupBox()
        self.inc_button: QPushButton = QPushButton()
        self.inc_button.setText("+")
        self.inc_button.setMaximumSize(30, 30)
        self.dec_button: QPushButton = QPushButton()
        self.dec_button.setText("-")
        self.dec_button.setMaximumSize(30, 30)
        self.brightness_slider: QSlider = QSlider()
        self.brightness_slider.setMinimum(1)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setSingleStep(1)
        self.brightness_slider.setPageStep(5)
        self.brightness_slider.setOrientation(Qt.Horizontal)
        self.brightness_slider.setValue(self.bright_int)
        self.reset_button: QPushButton = QPushButton()
        self.reset_button.setText("Reset")
        self.apply_button: QPushButton = QPushButton()
        self.apply_button.setText("Apply")
        self.exit_button: QPushButton = QPushButton()
        self.exit_button.setText("Exit")

        self.button_layout: QHBoxLayout = QHBoxLayout()
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.exit_button)
        self.slider_layout: QHBoxLayout = QHBoxLayout()
        self.slider_layout.addWidget(self.dec_button)
        self.slider_layout.addWidget(self.brightness_slider)
        self.slider_layout.addWidget(self.inc_button)
        self.slider_group_box.setLayout(self.slider_layout)
        self.main_layout: QVBoxLayout = QVBoxLayout()
        self.main_layout.addWidget(self.brightness_label)
        self.main_layout.addWidget(self.slider_group_box)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.button_layout)
        self.setLayout(self.main_layout)

        self.dec_button.clicked.connect(self.dec_brightness_slider)
        self.inc_button.clicked.connect(self.inc_brightness_slider)
        self.reset_button.clicked.connect(self.reset_brightness_slider)
        self.apply_button.clicked.connect(self.apply_brightness)
        self.exit_button.clicked.connect(functools.partial(sys.exit, 0))

    def dec_brightness_slider(self) -> None:
        """
        Moves the brightness slider down a tick.
        """

        self.brightness_slider.setValue(self.brightness_slider.value() - 1)

    def inc_brightness_slider(self) -> None:
        """
        Moves the brightness slider up a tick.
        """

        self.brightness_slider.setValue(self.brightness_slider.value() + 1)

    def reset_brightness_slider(self) -> None:
        """
        Resets the brightness slider to its last saved value.
        """

        self.brightness_slider.setValue(self.bright_int)

    def apply_brightness(self) -> None:
        """
        Saves the current brightness value and applies it to the hardware.
        """

        error_window: ErrorWindow
        try:
            set_bright_proc: subprocess.CompletedProcess[str] = subprocess.run(
                [
                    "/usr/bin/backlight-tool-dist-agent",
                    "set",
                    f"{self.brightness_slider.value()}",
                ],
                check=False,
                capture_output=True,
                encoding="utf-8",
            )
        except Exception:
            error_window = ErrorWindow(
                "The application was unable to get the current display for an "
                "unknown reason!<br>"
                "<br>"
                "Please report this bug!<br>"
                "<br>"
                "Error details:<br>"
                f"<pre>{traceback.format_exc()}</pre>"
            )
            error_window.exec_()
            sys.exit(1)

        if set_bright_proc.returncode != 0:
            error_window = ErrorWindow(
                "'/usr/bin/backlight-tool-dist-agent set "
                f"{self.brightness_slider.value()}' was unable to set the "
                "system's display brightness!<br>"
                "<br>"
                "Please report this bug!<br>"
                "<br>"
                "Output from 'backlight-tool-dist-agent':<br>"
                f"<pre>{set_bright_proc.stdout}"
                f"{set_bright_proc.stderr}</pre>"
            )
            error_window.exec_()
            sys.exit(1)

        self.bright_int = self.brightness_slider.value()


# pylint: disable=unused-argument
def signal_handler(sig: int, frame: FrameType | None) -> None:
    """
    Handles SIGINT and SIGTERM.
    """

    print("Received SIGINT or SIGTERM, exiting.", file=sys.stderr)
    sys.exit(128 + sig)


def main() -> NoReturn:
    """
    Main function.
    """

    app = QApplication(sys.argv)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    timer: QTimer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    error_window: ErrorWindow
    try:
        current_bright_proc: subprocess.CompletedProcess[str] = subprocess.run(
            [
                "/usr/bin/backlight-tool-dist-agent",
                "get",
            ],
            check=False,
            capture_output=True,
            encoding="utf-8",
        )
    except Exception:
        error_window = ErrorWindow(
            "The application was unable to get the current display for an "
            "unknown reason!<br>"
            "<br>"
            "Please report this bug!<br>"
            "<br>"
            "Error details:<br>"
            f"<pre>{traceback.format_exc()}</pre>"
        )
        error_window.exec_()
        sys.exit(1)

    if current_bright_proc.returncode != 0:
        error_window = ErrorWindow(
            "'/usr/bin/backlight-tool-dist-agent get' was unable to get the "
            "system's current backlight value! Possible causes:<br>"
            "- The system does not support display brightness controls.<br>"
            "- Your user account is not a member of the 'sudo' or "
            "'privleap' groups.<br>"
            "<br>"
            "Output from 'backlight-tool-dist-agent':<br>"
            f"<pre>{current_bright_proc.stdout}"
            f"{current_bright_proc.stderr}</pre>"
        )
        error_window.exec_()
        sys.exit(1)

    current_bright_str: str = current_bright_proc.stdout.strip()

    try:
        current_bright_int: int = int(current_bright_str)
    except Exception:
        error_window = ErrorWindow(
            "The system reported an invalid brightness value of "
            f"'{current_bright_str}'!<br>"
            "<br>"
            "Please report this bug!"
        )
        error_window.exec_()
        sys.exit(1)

    window = BacklightToolWindow(current_bright_int)
    window.show()
    app.exec_()
    sys.exit(0)


if __name__ == "__main__":
    main()
