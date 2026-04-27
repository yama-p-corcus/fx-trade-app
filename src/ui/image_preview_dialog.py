from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout


class ImagePreviewDialog(QDialog):
    MAX_SIZE = 800

    def __init__(self, image_path: str, parent=None) -> None:
        super().__init__(parent)
        self.image_path = image_path
        self.setWindowTitle("画像プレビュー")
        self.setModal(True)
        self.resize(self.MAX_SIZE, self.MAX_SIZE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        self._update_pixmap()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_pixmap()

    def _update_pixmap(self) -> None:
        if not self.image_path or not Path(self.image_path).exists():
            self.image_label.clear()
            self.image_label.setText("画像が見つかりません")
            return

        pixmap = QPixmap(self.image_path)
        if pixmap.isNull():
            self.image_label.clear()
            self.image_label.setText("画像を読み込めませんでした")
            return

        scaled = pixmap.scaled(
            min(self.image_label.width(), self.MAX_SIZE),
            min(self.image_label.height(), self.MAX_SIZE),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)
        self.image_label.setText("")
