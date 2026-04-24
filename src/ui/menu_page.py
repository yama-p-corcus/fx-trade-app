from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class MenuPage(QWidget):
    open_calendar = pyqtSignal()
    open_dashboard = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(16)

        title = QLabel("FX Trade Journal")
        title.setProperty("role", "title")
        subtitle = QLabel("シンプルに日々のトレードを記録するための MVP")
        subtitle.setProperty("role", "subtitle")

        calendar_button = QPushButton("日別トレード登録")
        dashboard_button = QPushButton("エントリー結果")

        calendar_button.clicked.connect(self.open_calendar.emit)
        dashboard_button.clicked.connect(self.open_dashboard.emit)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(12)
        card_layout.addWidget(calendar_button)
        card_layout.addWidget(dashboard_button)

        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
