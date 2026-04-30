from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.trade import Trade


class TradeListPage(QWidget):
    PIPS_COLUMN = 4
    PROFIT_COLUMN = 5

    back_requested = pyqtSignal()
    add_requested = pyqtSignal(str)
    edit_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.selected_date = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        top_bar = QHBoxLayout()
        self.back_button = QPushButton("カレンダーへ戻る")
        self.back_button.setProperty("variant", "secondary")
        self.back_button.clicked.connect(self.back_requested.emit)

        self.title_label = QLabel("日別トレード一覧")
        self.title_label.setProperty("role", "title")

        top_bar.addWidget(self.back_button)
        top_bar.addStretch()
        top_bar.addWidget(self.title_label)
        top_bar.addStretch()

        action_bar = QHBoxLayout()
        self.summary_label = QLabel("")
        self.summary_label.setProperty("role", "subtitle")

        self.add_button = QPushButton("新規追加")
        self.edit_button = QPushButton("編集")
        self.edit_button.setProperty("variant", "secondary")
        self.delete_button = QPushButton("削除")
        self.delete_button.setProperty("variant", "danger")

        self.add_button.clicked.connect(lambda: self.add_requested.emit(self.selected_date))
        self.edit_button.clicked.connect(self._emit_edit)
        self.delete_button.clicked.connect(self._emit_delete)

        action_bar.addWidget(self.summary_label)
        action_bar.addStretch()
        action_bar.addWidget(self.add_button)
        action_bar.addWidget(self.edit_button)
        action_bar.addWidget(self.delete_button)

        card = QFrame()
        card.setObjectName("card")
        card.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["ID", "時間", "通貨ペア", "売買", "pips", "損益", "注文価格", "決済価格"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(self._emit_edit)
        self.table.setAlternatingRowColors(True)
        self.table.setMouseTracking(True)
        self.table.viewport().setMouseTracking(True)
        self.table.setShowGrid(True)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)

        card_layout.addWidget(self.table, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(top_bar)
        layout.addLayout(action_bar)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()

        self._set_action_enabled(False)

    def load_trades(self, selected_date: str, trades: list[Trade]) -> None:
        self.selected_date = selected_date
        self.title_label.setText(f"{selected_date} のトレード一覧")
        total_pips = sum(trade.pips for trade in trades)
        self.summary_label.setText(f"{len(trades)} 件 / 合計 pips: {self._format_decimal(total_pips, 1)}")

        self.table.clearContents()
        self.table.setRowCount(len(trades))
        for row, trade in enumerate(trades):
            values = [
                str(trade.id),
                trade.trade_time,
                trade.currency_pair,
                "買い" if trade.trade_type == "buy" else "売り",
                self._format_decimal(trade.pips, 1),
                self._format_integer(trade.profit),
                self._format_decimal(trade.order_price, 5),
                self._format_decimal(trade.settlement_price, 5),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {0, 4, 5, 6, 7}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if column == self.PIPS_COLUMN and trade.pips < 0:
                    item.setForeground(QColor("#c62828"))
                if column == self.PROFIT_COLUMN and trade.profit < 0:
                    item.setForeground(QColor("#c62828"))
                self.table.setItem(row, column, item)

        self.table.resizeRowsToContents()
        self._set_action_enabled(bool(trades))
        if trades:
            self.table.selectRow(0)

    def _set_action_enabled(self, enabled: bool) -> None:
        self.edit_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def _selected_trade_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _emit_edit(self, *_args) -> None:
        trade_id = self._selected_trade_id()
        if trade_id is not None:
            self.edit_requested.emit(trade_id)

    def _emit_delete(self) -> None:
        trade_id = self._selected_trade_id()
        if trade_id is not None:
            self.delete_requested.emit(trade_id)

    @staticmethod
    def _format_integer(value: int) -> str:
        return f"{value:,}"

    @staticmethod
    def _format_decimal(value: float, digits: int) -> str:
        return f"{value:,.{digits}f}"
