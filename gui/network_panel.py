from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path
from typing import Dict, List, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QCheckBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
MONITOR_DIR = ROOT_DIR / "monitor"


class NetworkPanel(QWidget):
    """PySide6 panel that manages dev-safe network restrictions."""

    def __init__(self, main_window, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._main_window = main_window
        self._python = sys.executable
        self._status_label = QLabel("Network access: enabled")
        self._note_box = QTextEdit()
        self._note_box.setReadOnly(True)
        self._note_box.setFixedHeight(90)
        self._note_box.setStyleSheet(
            "QTextEdit { background-color: #f7fafc; border: 1px solid #e2e8f0; "
            "border-radius: 8px; padding: 6px; }"
        )

        self.disable_check = QCheckBox("Disable Network Access")
        self.enforce_check = QCheckBox("Enforce (requires sudo)")
        self.enforce_check.setToolTip(
            "Requires root. GUI will display sudo command; it will not run privileged commands."
        )
        self.enforce_check.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        header = QLabel("📡 Network Restriction")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d3748;")
        layout.addWidget(header)
        layout.addWidget(self.disable_check)
        layout.addWidget(self.enforce_check)
        layout.addWidget(self._status_label)
        layout.addWidget(self._note_box)

        self.disable_check.toggled.connect(self._on_disable_toggled)
        self.enforce_check.toggled.connect(self._on_enforce_toggled)
        self._update_status()

    def is_disabled(self) -> bool:
        return self.disable_check.isChecked()

    def is_enforce_mode(self) -> bool:
        return self.is_disabled() and self.enforce_check.isChecked()

    def prepare_command(self, command: Sequence[str]) -> List[str]:
        if not self.is_disabled():
            return list(command)
        if self.is_enforce_mode():
            return list(command)
        wrapper_cmd = [self._python, "-m", "monitor.net_wrapper", "--", *command]
        return wrapper_cmd

    def apply_env_overrides(self, env: Dict[str, str]) -> None:
        existing = env.get("PYTHONPATH", "")
        root = str(ROOT_DIR)
        if existing:
            if root not in existing.split(os.pathsep):
                env["PYTHONPATH"] = os.pathsep.join([root, existing])
        else:
            env["PYTHONPATH"] = root

        if self.is_enforce_mode():
            env.setdefault("ZENCUBE_NET_MODE", "seccomp")
        elif self.is_disabled():
            env.setdefault("ZENCUBE_NET_MODE", "dev-safe")

    def show_enforce_command(self, sandbox_path: str, base_args: Sequence[str]) -> None:
        if not self.is_enforce_mode():
            return
        parts = ["sudo", sandbox_path, *base_args]
        command = shlex.join(parts)
        self._note_box.setPlainText(
            "Enforce mode requires sudo. Run the following command manually:\n\n" + command
        )

    def reset_note(self) -> None:
        if not self.is_disabled():
            self._note_box.clear()
        else:
            if not self.is_enforce_mode():
                self._note_box.setPlainText(
                    "Dev-safe mode: monitor.net_wrapper will automatically wrap the command."
                )

    def _update_status(self) -> None:
        if not self.is_disabled():
            self._status_label.setText("Network access: enabled")
            self._note_box.setPlaceholderText("Enable network restriction to view status messages.")
        elif self.is_enforce_mode():
            self._status_label.setText("Network access: disabled via seccomp (requires sudo)")
        else:
            self._status_label.setText("Network access: disabled (dev-safe)")
            if not self._note_box.toPlainText():
                self._note_box.setPlainText(
                    "Dev-safe mode: network sockets will raise PermissionError and attempts are logged."
                )

    def _on_disable_toggled(self, checked: bool) -> None:
        self.enforce_check.setEnabled(checked)
        if not checked:
            self.enforce_check.setChecked(False)
        self._update_status()
        self.reset_note()
        if hasattr(self._main_window, "log_output"):
            message = "Network restriction disabled" if not checked else "Network restriction enabled"
            self._main_window.log_output(message + "\n", "info")

    def _on_enforce_toggled(self, checked: bool) -> None:
        self._update_status()
        if checked and hasattr(self._main_window, "log_output"):
            self._main_window.log_output("Seccomp enforce mode requested. Run with sudo to activate.\n", "warning")
        if not checked:
            self.reset_note()


def attach_network_panel(main_window, layout) -> NetworkPanel:
    panel = NetworkPanel(main_window)
    layout.addWidget(panel)
    return panel
