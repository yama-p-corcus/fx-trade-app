from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel


class ClickableImageLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        self.clicked.emit()
