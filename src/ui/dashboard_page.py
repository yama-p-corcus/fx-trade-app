from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    back_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        back_button = QPushButton("メニューへ戻る")
        back_button.setProperty("variant", "secondary")
        back_button.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        title = QLabel("ダッシュボード")
        title.setProperty("role", "title")
        message = QLabel("この画面は後続ステップで実装予定です。MVP ではカレンダーとトレード記録のみ対応しています。")
        message.setWordWrap(True)

        card_layout.addWidget(title)
        card_layout.addWidget(message)
        layout.addWidget(card)
