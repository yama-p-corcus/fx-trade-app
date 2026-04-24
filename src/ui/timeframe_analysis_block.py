from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QSizePolicy, QTextEdit, QVBoxLayout, QWidget

from src.ui.image_drop_area import ImageDropArea


class TimeframeAnalysisBlock(QFrame):
    def __init__(self, title: str, placeholder: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setProperty("role", "subtitle")

        self.image_drop_area = ImageDropArea()
        self.image_drop_area.setFixedHeight(170)

        comment_label = QLabel("コメント")
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText(placeholder)
        self.comment_edit.setFixedHeight(72)

        layout.addWidget(title_label)
        layout.addWidget(self.image_drop_area)
        layout.addWidget(comment_label)
        layout.addWidget(self.comment_edit)

    def set_values(self, image_path: str, comment: str) -> None:
        if image_path:
            self.image_drop_area.set_image_path(image_path)
        self.comment_edit.setPlainText(comment)

    def values(self) -> dict[str, str]:
        return {
            "image_source_path": self.image_drop_area.image_path(),
            "comment": self.comment_edit.toPlainText().strip(),
        }
