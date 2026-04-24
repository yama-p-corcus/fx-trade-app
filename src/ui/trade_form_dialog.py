from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QDate, QTime, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
)

from src.models.trade import Trade


class TradeFormDialog(QDialog):
    def __init__(self, parent=None, trade: Trade | None = None, default_date: str | None = None) -> None:
        super().__init__(parent)
        self.trade = trade
        self.setWindowTitle("トレード編集" if trade else "トレード新規登録")
        self.resize(620, 560)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        basic_card = QFrame()
        basic_card.setObjectName("card")
        basic_layout = QFormLayout(basic_card)
        basic_layout.setContentsMargins(18, 18, 18, 18)
        basic_layout.setSpacing(12)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.currency_pair_edit = QLineEdit()
        self.currency_pair_edit.setPlaceholderText("例: USD/JPY")

        basic_layout.addRow("日付", self.date_edit)
        basic_layout.addRow("時間", self.time_edit)
        basic_layout.addRow("通貨ペア", self.currency_pair_edit)

        result_card = QFrame()
        result_card.setObjectName("card")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(18, 18, 18, 18)
        result_layout.setSpacing(12)

        section_title = QLabel("結果")
        section_title.setProperty("role", "subtitle")
        result_layout.addWidget(section_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        self.order_price_spin = self._create_double_spinbox(decimals=5, maximum=99999999.99999, minimum=0.00001)
        self.settlement_price_spin = self._create_double_spinbox(decimals=5, maximum=99999999.99999, minimum=0.00001)
        self.lot_spin = self._create_double_spinbox(decimals=2, maximum=999999.99, minimum=0.01)
        self.pips_spin = self._create_double_spinbox(decimals=1, maximum=999999.9, minimum=-999999.9)
        self.trade_type_combo = QComboBox()
        self.trade_type_combo.addItem("買い", "buy")
        self.trade_type_combo.addItem("売り", "sell")
        self.profit_spin = QSpinBox()
        self.profit_spin.setRange(-999999999, 999999999)
        self.profit_spin.setSingleStep(1000)
        self.profit_spin.setGroupSeparatorShown(True)

        self.entry_memo_edit = QTextEdit()
        self.entry_memo_edit.setPlaceholderText("エントリーメモ")
        self.exit_memo_edit = QTextEdit()
        self.exit_memo_edit.setPlaceholderText("決済メモ")

        fields = [
            ("注文価格", self.order_price_spin),
            ("決済価格", self.settlement_price_spin),
            ("ロット数", self.lot_spin),
            ("pips", self.pips_spin),
            ("売買区分", self.trade_type_combo),
            ("損益（円）", self.profit_spin),
        ]

        for index, (label_text, widget) in enumerate(fields):
            row = index // 2
            column = (index % 2) * 2
            grid.addWidget(QLabel(label_text), row, column)
            grid.addWidget(widget, row, column + 1)

        result_layout.addLayout(grid)
        result_layout.addWidget(QLabel("エントリーメモ"))
        result_layout.addWidget(self.entry_memo_edit)
        result_layout.addWidget(QLabel("決済メモ"))
        result_layout.addWidget(self.exit_memo_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._validate_before_accept)
        self.button_box.rejected.connect(self.reject)

        root_layout.addWidget(basic_card)
        root_layout.addWidget(result_card)
        root_layout.addWidget(self.button_box)

        self._set_defaults(trade=trade, default_date=default_date)

    def _set_defaults(self, trade: Trade | None, default_date: str | None) -> None:
        self.time_edit.setTime(QTime.currentTime())
        self.date_edit.setDate(QDate.currentDate())

        if default_date:
            self.date_edit.setDate(QDate.fromString(default_date, "yyyy-MM-dd"))

        if not trade:
            return

        self.date_edit.setDate(QDate.fromString(trade.trade_date, "yyyy-MM-dd"))
        self.time_edit.setTime(QTime.fromString(trade.trade_time, "HH:mm"))
        self.currency_pair_edit.setText(trade.currency_pair)
        self.order_price_spin.setValue(trade.order_price)
        self.settlement_price_spin.setValue(trade.settlement_price)
        self.lot_spin.setValue(trade.lot)
        self.pips_spin.setValue(trade.pips)
        self.profit_spin.setValue(trade.profit)
        self.entry_memo_edit.setPlainText(trade.entry_memo)
        self.exit_memo_edit.setPlainText(trade.exit_memo)

        index = self.trade_type_combo.findData(trade.trade_type)
        if index >= 0:
            self.trade_type_combo.setCurrentIndex(index)

    def get_payload(self) -> dict[str, Any]:
        return {
            "trade_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "trade_time": self.time_edit.time().toString("HH:mm"),
            "currency_pair": self.currency_pair_edit.text().strip(),
            "order_price": self.order_price_spin.value(),
            "settlement_price": self.settlement_price_spin.value(),
            "lot": self.lot_spin.value(),
            "pips": self.pips_spin.value(),
            "trade_type": self.trade_type_combo.currentData(),
            "profit": self.profit_spin.value(),
            "entry_memo": self.entry_memo_edit.toPlainText().strip(),
            "exit_memo": self.exit_memo_edit.toPlainText().strip(),
        }

    def _validate_before_accept(self) -> None:
        if not self.currency_pair_edit.text().strip():
            QMessageBox.warning(self, "入力エラー", "通貨ペアは必須です。")
            return
        self.accept()

    @staticmethod
    def _create_double_spinbox(decimals: int, maximum: float, minimum: float) -> QDoubleSpinBox:
        widget = QDoubleSpinBox()
        widget.setDecimals(decimals)
        widget.setRange(minimum, maximum)
        widget.setGroupSeparatorShown(True)
        widget.setAlignment(Qt.AlignmentFlag.AlignRight)
        return widget
