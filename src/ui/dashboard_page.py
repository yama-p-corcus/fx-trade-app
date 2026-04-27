from __future__ import annotations

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
except ModuleNotFoundError:
    FigureCanvasQTAgg = None
    Figure = None


class DashboardPage(QWidget):
    back_requested = pyqtSignal()
    filter_changed = pyqtSignal(int, int)
    trade_requested = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self.scroll_area.setWidget(container)
        outer_layout.addWidget(self.scroll_area)

        back_button = QPushButton("メニューへ戻る")
        back_button.setProperty("variant", "secondary")
        back_button.clicked.connect(self.back_requested.emit)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        controls_layout.addStretch()

        today = QDate.currentDate()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(today.year())
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(today.month())
        refresh_button = QPushButton("表示更新")
        refresh_button.clicked.connect(self._emit_filter_changed)

        controls_layout.addWidget(QLabel("年"))
        controls_layout.addWidget(self.year_spin)
        controls_layout.addWidget(QLabel("月"))
        controls_layout.addWidget(self.month_spin)
        controls_layout.addWidget(refresh_button)
        layout.addLayout(controls_layout)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        title = QLabel("ダッシュボード")
        title.setProperty("role", "title")

        card_layout.addWidget(title)

        self.chart_title = QLabel("日別 pips")
        self.chart_title.setProperty("role", "subtitle")
        card_layout.addWidget(self.chart_title)

        self.chart_notice = QLabel("")
        self.chart_notice.setWordWrap(True)
        self.chart_notice.setProperty("role", "subtitle")

        self.figure = Figure(figsize=(8, 3.5)) if Figure else None
        self.canvas = FigureCanvasQTAgg(self.figure) if FigureCanvasQTAgg and self.figure else None
        if self.canvas:
            self.canvas.setMinimumHeight(320)
            self.canvas.setMaximumHeight(360)
            self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            card_layout.addWidget(self.canvas)
        else:
            self.chart_notice.setText("matplotlib が未インストールのため、グラフを表示できません。`pip install -r requirements.txt` を実行してください。")
            card_layout.addWidget(self.chart_notice)

        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(12)
        stats_grid.setVerticalSpacing(12)
        self.stat_labels = {
            "wins": self._create_stat_card(stats_grid, 0, 0, "勝ち数"),
            "losses": self._create_stat_card(stats_grid, 0, 1, "負け数"),
            "win_rate": self._create_stat_card(stats_grid, 0, 2, "勝率"),
            "average_profit": self._create_stat_card(stats_grid, 1, 0, "平均利益"),
            "average_loss": self._create_stat_card(stats_grid, 1, 1, "平均損失"),
        }
        card_layout.addLayout(stats_grid)

        table_header_layout = QHBoxLayout()
        self.table_title = QLabel("月次トレード一覧")
        self.table_title.setProperty("role", "subtitle")
        self.total_profit_label = QLabel("合計損益: 0")
        self.total_profit_label.setProperty("role", "subtitle")
        table_header_layout.addWidget(self.table_title)
        table_header_layout.addStretch()
        table_header_layout.addWidget(self.total_profit_label)
        card_layout.addLayout(table_header_layout)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["日付", "時間", "通貨", "売買", "pips", "損益"])
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(self._emit_trade_requested)
        self.table.setAlternatingRowColors(True)
        self.table.setMouseTracking(True)
        self.table.viewport().setMouseTracking(True)
        self.table.setShowGrid(True)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setMinimumHeight(320)
        self.table.setMaximumHeight(420)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)
        card_layout.addWidget(self.table)
        layout.addWidget(card)

        self._draw_chart([])
        self._populate_table([])

    def set_dashboard_data(self, payload: dict) -> None:
        chart_items = payload.get("chart_items", [])
        self.chart_title.setText(f"{payload['year']}年{payload['month']}月 日別 pips")
        self._draw_chart(chart_items)

        stats = payload.get("stats", {})
        self.stat_labels["wins"].setText(f"{stats.get('wins', 0):,}")
        self.stat_labels["losses"].setText(f"{stats.get('losses', 0):,}")
        self.stat_labels["win_rate"].setText(f"{stats.get('win_rate', 0.0):.1f}%")
        self.stat_labels["average_profit"].setText(f"{stats.get('average_profit', 0.0):,.1f}")
        self.stat_labels["average_loss"].setText(f"{stats.get('average_loss', 0.0):,.1f}")
        total_profit = int(payload.get("total_profit", 0))
        self.total_profit_label.setText(f"合計損益: {total_profit:,}")
        self.total_profit_label.setStyleSheet(f"color: {'#1565c0' if total_profit >= 0 else '#c62828'};")
        self._populate_table(payload.get("table_rows", []))

    def selected_year_month(self) -> tuple[int, int]:
        return self.year_spin.value(), self.month_spin.value()

    def _emit_filter_changed(self) -> None:
        self.filter_changed.emit(self.year_spin.value(), self.month_spin.value())

    def _draw_chart(self, chart_items: list[dict]) -> None:
        if not self.figure or not self.canvas:
            return
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.axhline(0, color="#9bb5a2", linewidth=1)

        if chart_items:
            labels = [item["label"] for item in chart_items]
            values = [item["value"] for item in chart_items]
            colors = [item["color"] for item in chart_items]
            ax.bar(labels, values, color=colors, width=0.6)
        else:
            ax.text(0.5, 0.5, "データがありません", ha="center", va="center", transform=ax.transAxes)
            ax.set_xticks([])

        ax.set_ylabel("pips")
        ax.set_facecolor("#ffffff")
        self.figure.patch.set_facecolor("#ffffff")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#cddfcf")
        ax.spines["bottom"].set_color("#cddfcf")
        ax.tick_params(colors="#365244")
        self.figure.tight_layout()
        self.canvas.draw()

    def _populate_table(self, rows: list[dict]) -> None:
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            values = [
                row_data["date"],
                row_data["time"],
                row_data["currency_pair"],
                row_data["trade_type"],
                f"{row_data['pips']:,.1f}",
                f"{row_data['profit']:,}",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {4, 5}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if column == 4 and row_data["pips"] < 0:
                    item.setForeground(QColor("#c62828"))
                if column == 5:
                    if row_data["profit"] < 0:
                        item.setForeground(QColor("#c62828"))
                    else:
                        item.setForeground(QColor("#1565c0"))
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, row_data["id"])
                self.table.setItem(row_index, column, item)

        self.table.resizeRowsToContents()
        self.table.setSortingEnabled(True)
        if rows:
            self.table.selectRow(0)

    def _emit_trade_requested(self, item: QTableWidgetItem) -> None:
        trade_id = self.table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        if trade_id is not None:
            self.trade_requested.emit(int(trade_id))

    @staticmethod
    def _create_stat_card(grid: QGridLayout, row: int, column: int, title: str) -> QLabel:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        label = QLabel(title)
        label.setProperty("role", "subtitle")
        value = QLabel("0")
        value.setProperty("role", "title")
        value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(label)
        layout.addWidget(value)
        grid.addWidget(card, row, column)
        return value
