from __future__ import annotations

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QTextCharFormat
from PyQt6.QtWidgets import QCalendarWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QWidget


class TradeCalendarPage(QWidget):
    back_requested = pyqtSignal()
    date_selected = pyqtSignal(str)
    month_changed = pyqtSignal(int, int)

    def __init__(self) -> None:
        super().__init__()
        self._base_format = QTextCharFormat()
        self._base_format.setBackground(QColor("white"))
        self._base_format.setForeground(QColor("#26352c"))

        self._profit_format = QTextCharFormat(self._base_format)
        self._profit_format.setBackground(QColor("#d9efff"))

        self._loss_format = QTextCharFormat(self._base_format)
        self._loss_format.setBackground(QColor("#ffdfe0"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        back_button = QPushButton("メニューへ戻る")
        back_button.setProperty("variant", "secondary")
        back_button.clicked.connect(self.back_requested.emit)

        title = QLabel("カレンダー")
        title.setProperty("role", "title")
        subtitle = QLabel("トレードのある日は損益に応じて色分けされます。日付をクリックすると一覧が開きます。")
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self._handle_date_clicked)
        self.calendar.currentPageChanged.connect(self.month_changed.emit)

        card_layout.addWidget(self.calendar)

        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(card)

    def apply_trade_highlights(self, summary: dict[str, int]) -> None:
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()

        for day in range(1, 32):
            qdate = QDate(year, month, day)
            if qdate.isValid():
                self.calendar.setDateTextFormat(qdate, self._base_format)

        for trade_date, total_profit in summary.items():
            qdate = QDate.fromString(trade_date, "yyyy-MM-dd")
            if qdate.isValid() and qdate.year() == year and qdate.month() == month:
                text_format = self._profit_format if total_profit >= 0 else self._loss_format
                self.calendar.setDateTextFormat(qdate, text_format)

        self.calendar.updateCells()

    def visible_year_month(self) -> tuple[int, int]:
        return self.calendar.yearShown(), self.calendar.monthShown()

    def _handle_date_clicked(self, qdate: QDate) -> None:
        self.date_selected.emit(qdate.toString("yyyy-MM-dd"))
