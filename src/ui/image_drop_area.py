from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class ImageDropArea(QWidget):
    image_changed = pyqtSignal(str)
    PREVIEW_WIDTH = 320
    PREVIEW_HEIGHT = 170

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._image_path = ""
        self.setAcceptDrops(True)
        self.setMinimumHeight(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.preview_label = QLabel("画像をここへドラッグ＆ドロップ")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setWordWrap(True)
        self.preview_label.setFixedSize(self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.preview_label.setStyleSheet(
            "border: 2px dashed #b8d3c0; border-radius: 12px; background: #f8fcf9; color: #567064;"
        )

        self.help_label = QLabel("対応形式: PNG / JPG / JPEG / BMP")
        self.help_label.setProperty("role", "subtitle")
        self.help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.help_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._extract_image_path(event):
            event.acceptProposedAction()
            return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        image_path = self._extract_image_path(event)
        if not image_path:
            event.ignore()
            return
        self.set_image_path(image_path)
        event.acceptProposedAction()

    def set_image_path(self, image_path: str) -> None:
        self._image_path = image_path
        self._update_preview()
        self.image_changed.emit(image_path)

    def image_path(self) -> str:
        return self._image_path

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_preview()

    def _update_preview(self) -> None:
        if not self._image_path or not Path(self._image_path).exists():
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("画像をここへドラッグ＆ドロップ")
            self.help_label.setVisible(True)
            return

        pixmap = QPixmap(self._image_path)
        if pixmap.isNull():
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("画像を読み込めませんでした")
            self.help_label.setVisible(True)
            return

        scaled = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setText("")
        self.preview_label.setPixmap(scaled)
        self.help_label.setVisible(False)

    @staticmethod
    def _extract_image_path(event) -> str:
        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            return ""

        for url in mime_data.urls():
            if not url.isLocalFile():
                continue
            local_path = Path(url.toLocalFile())
            if local_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}:
                return str(local_path)
        return ""
