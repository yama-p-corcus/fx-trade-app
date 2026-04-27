from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QDate, QTime, Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from src.models.trade import Trade
from src.ui.timeframe_analysis_block import TimeframeAnalysisBlock


class TradeFormDialog(QDialog):
    TIMEFRAME_CONFIG = (
        ("m15", "15分足 (M15)"),
        ("h1", "1時間足 (H1)"),
        ("h4", "4時間足 (H4)"),
        ("d1", "日足 (D1)"),
    )

    def __init__(
        self,
        parent=None,
        trade: Trade | None = None,
        default_date: str | None = None,
        last_currency_pair: str = "",
        validate_callback=None,
    ) -> None:
        super().__init__(parent)
        self.trade = trade
        self.validate_callback = validate_callback
        self.last_currency_pair = last_currency_pair
        self.field_errors: dict[str, QLabel] = {}
        self.timeframe_blocks: dict[str, TimeframeAnalysisBlock] = {}
        self.setWindowTitle("トレード編集" if trade else "トレード新規登録")
        self.setMinimumSize(1080, 820)
        self.resize(1120, 860)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.container = QWidget()
        self.container.setMinimumWidth(1000)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(14)
        self.scroll_area.setWidget(self.container)

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
        self.currency_pair_error = self._create_error_label()

        basic_layout.addRow("日付", self.date_edit)
        basic_layout.addRow("時間", self.time_edit)
        basic_layout.addRow("通貨ペア", self.currency_pair_edit)
        basic_layout.addRow("", self.currency_pair_error)

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

        self.order_price_spin = self._create_double_spinbox(decimals=3, maximum=99999999.999, minimum=0.001)
        self.order_price_spin.setSingleStep(0.001)
        self.settlement_price_spin = self._create_double_spinbox(decimals=3, maximum=99999999.999, minimum=0.001)
        self.settlement_price_spin.setSingleStep(0.001)
        self.lot_spin = self._create_double_spinbox(decimals=2, maximum=999999.99, minimum=0.01)
        self.lot_spin.setSingleStep(0.01)
        self.pips_spin = self._create_double_spinbox(decimals=1, maximum=999999.9, minimum=-999999.9)
        self.pips_spin.setSingleStep(0.1)
        self.trade_type_group = QButtonGroup(self)
        self.buy_button = self._create_toggle_button("買い", "buy")
        self.sell_button = self._create_toggle_button("売り", "sell")
        self.trade_type_group.addButton(self.buy_button)
        self.trade_type_group.addButton(self.sell_button)
        self.buy_button.setChecked(True)
        self._sync_trade_type_buttons()
        trade_type_layout = QHBoxLayout()
        trade_type_layout.setContentsMargins(0, 0, 0, 0)
        trade_type_layout.setSpacing(8)
        trade_type_layout.addWidget(self.buy_button)
        trade_type_layout.addWidget(self.sell_button)
        trade_type_layout.addStretch()
        self.profit_spin = QSpinBox()
        self.profit_spin.setRange(-999999999, 999999999)
        self.profit_spin.setSingleStep(1000)
        self.profit_spin.setGroupSeparatorShown(True)

        self.order_price_error = self._create_error_label()
        self.settlement_price_error = self._create_error_label()
        self.lot_error = self._create_error_label()
        self.pips_error = self._create_error_label()
        self.trade_type_error = self._create_error_label()
        self.profit_error = self._create_error_label()

        self.entry_memo_edit = QTextEdit()
        self.entry_memo_edit.setPlaceholderText("エントリーメモ")
        self.exit_memo_edit = QTextEdit()
        self.exit_memo_edit.setPlaceholderText("決済メモ")

        fields = [
            ("注文価格", self.order_price_spin),
            ("決済価格", self.settlement_price_spin),
            ("ロット数", self.lot_spin),
            ("pips", self.pips_spin),
            ("売買区分", trade_type_layout),
            ("損益（円）", self.profit_spin),
        ]
        field_error_widgets = [
            self.order_price_error,
            self.settlement_price_error,
            self.lot_error,
            self.pips_error,
            self.trade_type_error,
            self.profit_error,
        ]

        for index, (label_text, widget) in enumerate(fields):
            row = index // 2
            column = (index % 2) * 2
            grid.addWidget(QLabel(label_text), row, column)
            if isinstance(widget, QHBoxLayout):
                grid.addLayout(widget, row, column + 1)
            else:
                grid.addWidget(widget, row, column + 1)
            grid.addWidget(field_error_widgets[index], row + 3, column + 1)

        result_layout.addLayout(grid)

        analysis_card = QFrame()
        analysis_card.setObjectName("card")
        analysis_layout = QVBoxLayout(analysis_card)
        analysis_layout.setContentsMargins(18, 18, 18, 18)
        analysis_layout.setSpacing(14)

        analysis_title = QLabel("時間足分析")
        analysis_title.setProperty("role", "subtitle")

        analysis_grid = QGridLayout()
        analysis_grid.setHorizontalSpacing(14)
        analysis_grid.setVerticalSpacing(14)
        analysis_grid.setContentsMargins(0, 0, 0, 0)

        analysis_layout.addWidget(analysis_title)
        analysis_layout.addLayout(analysis_grid)

        entry_memo_card = QFrame()
        entry_memo_card.setObjectName("card")
        entry_memo_layout = QVBoxLayout(entry_memo_card)
        entry_memo_layout.setContentsMargins(18, 18, 18, 18)
        entry_memo_layout.setSpacing(10)
        entry_memo_title = QLabel("エントリーメモ")
        entry_memo_title.setProperty("role", "subtitle")
        self.entry_memo_edit.setFixedHeight(120)
        entry_memo_layout.addWidget(entry_memo_title)
        entry_memo_layout.addWidget(self.entry_memo_edit)

        exit_memo_card = QFrame()
        exit_memo_card.setObjectName("card")
        exit_memo_layout = QVBoxLayout(exit_memo_card)
        exit_memo_layout.setContentsMargins(18, 18, 18, 18)
        exit_memo_layout.setSpacing(10)
        exit_memo_title = QLabel("決済メモ")
        exit_memo_title.setProperty("role", "subtitle")
        self.exit_memo_edit.setFixedHeight(120)
        exit_memo_layout.addWidget(exit_memo_title)
        exit_memo_layout.addWidget(self.exit_memo_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._validate_before_accept)
        self.button_box.rejected.connect(self.reject)
        button_card = QFrame()
        button_card.setObjectName("card")
        button_layout = QVBoxLayout(button_card)
        button_layout.setContentsMargins(18, 18, 18, 18)
        button_layout.addWidget(self.button_box)

        container_layout.addWidget(basic_card)
        container_layout.addWidget(result_card)
        for index, (timeframe_key, timeframe_title) in enumerate(self.TIMEFRAME_CONFIG):
            block = self._create_timeframe_block(timeframe_title, timeframe_key)
            self.timeframe_blocks[timeframe_key] = block
            row = index // 2
            column = index % 2
            analysis_grid.addWidget(block, row, column)
        container_layout.addWidget(analysis_card)
        container_layout.addWidget(entry_memo_card)
        container_layout.addWidget(exit_memo_card)
        container_layout.addWidget(button_card)

        root_layout.addWidget(self.scroll_area)

        self.field_errors = {
            "currency_pair": self.currency_pair_error,
            "order_price": self.order_price_error,
            "settlement_price": self.settlement_price_error,
            "lot": self.lot_error,
            "pips": self.pips_error,
            "trade_type": self.trade_type_error,
            "profit": self.profit_error,
        }

        self._set_defaults(trade=trade, default_date=default_date)

    def _set_defaults(self, trade: Trade | None, default_date: str | None) -> None:
        self.time_edit.setTime(QTime.currentTime())
        self.date_edit.setDate(QDate.currentDate())

        if default_date:
            self.date_edit.setDate(QDate.fromString(default_date, "yyyy-MM-dd"))

        if self.last_currency_pair:
            self.currency_pair_edit.setText(self.last_currency_pair)

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
        self._set_trade_type(trade.trade_type)
        self._apply_timeframe_defaults(trade)

    def get_payload(self) -> dict[str, Any]:
        payload = {
            "trade_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "trade_time": self.time_edit.time().toString("HH:mm"),
            "currency_pair": self.currency_pair_edit.text().strip(),
            "order_price": self.order_price_spin.value(),
            "settlement_price": self.settlement_price_spin.value(),
            "lot": self.lot_spin.value(),
            "pips": self.pips_spin.value(),
            "trade_type": self.current_trade_type(),
            "profit": self.profit_spin.value(),
            "entry_memo": self.entry_memo_edit.toPlainText().strip(),
            "exit_memo": self.exit_memo_edit.toPlainText().strip(),
            "image_path": self.trade.image_path if self.trade else "",
            "image_source_path": "",
        }
        for timeframe_key, block in self.timeframe_blocks.items():
            block_values = block.values()
            payload[f"{timeframe_key}_image_path"] = getattr(self.trade, f"{timeframe_key}_image_path", "") if self.trade else ""
            payload[f"{timeframe_key}_image_source_path"] = block_values["image_source_path"]
            payload[f"{timeframe_key}_comment"] = block_values["comment"]
        return payload

    def _validate_before_accept(self) -> None:
        self.clear_errors()
        payload = self.get_payload()
        if not payload["currency_pair"]:
            self.show_field_error("currency_pair", "通貨ペアは必須です。")
            return
        if not payload["trade_type"]:
            self.show_field_error("trade_type", "売買区分を選択してください。")
            return
        try:
            if self.validate_callback:
                self.validate_callback(payload)
        except ValueError as exc:
            self.show_validation_error(str(exc))
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

    @staticmethod
    def _create_error_label() -> QLabel:
        label = QLabel("")
        label.setProperty("role", "error")
        label.setVisible(False)
        label.setWordWrap(True)
        return label

    def _create_toggle_button(self, text: str, value: str) -> QPushButton:
        button = QPushButton(text)
        button.setProperty("variant", "toggle")
        button.setProperty("checked", "false")
        button.setCheckable(True)
        button.clicked.connect(lambda checked, current=value: self._handle_trade_type_selected(current, checked))
        return button

    def _handle_trade_type_selected(self, trade_type: str, checked: bool) -> None:
        if not checked:
            self._set_trade_type(trade_type)
            return
        self._set_trade_type(trade_type)

    def _set_trade_type(self, trade_type: str) -> None:
        self.buy_button.setChecked(trade_type == "buy")
        self.sell_button.setChecked(trade_type == "sell")
        self._sync_trade_type_buttons()

    def _sync_trade_type_buttons(self) -> None:
        for button in (self.buy_button, self.sell_button):
            button.setProperty("checked", "true" if button.isChecked() else "false")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def current_trade_type(self) -> str:
        if self.buy_button.isChecked():
            return "buy"
        if self.sell_button.isChecked():
            return "sell"
        return ""

    def clear_errors(self) -> None:
        for label in self.field_errors.values():
            label.clear()
            label.setVisible(False)

    def show_field_error(self, field_name: str, message: str) -> None:
        label = self.field_errors.get(field_name)
        if label is None:
            return
        label.setText(message)
        label.setVisible(True)

    def show_validation_error(self, message: str) -> None:
        field_name = self._field_from_message(message)
        self.show_field_error(field_name, message)

    @staticmethod
    def _field_from_message(message: str) -> str:
        if "通貨ペア" in message:
            return "currency_pair"
        if "注文価格" in message:
            return "order_price"
        if "決済価格" in message:
            return "settlement_price"
        if "ロット数" in message:
            return "lot"
        if "売買区分" in message:
            return "trade_type"
        if "損益" in message:
            return "profit"
        if "pips" in message or "数値項目" in message:
            return "pips"
        return "currency_pair"

    def _create_timeframe_block(self, title: str, timeframe_key: str) -> TimeframeAnalysisBlock:
        return TimeframeAnalysisBlock(
            title=title,
            placeholder=f"{title} の分析メモを入力",
        )

    def _apply_timeframe_defaults(self, trade: Trade) -> None:
        for timeframe_key, block in self.timeframe_blocks.items():
            block.set_values(
                getattr(trade, f"{timeframe_key}_image_path", ""),
                getattr(trade, f"{timeframe_key}_comment", ""),
            )
