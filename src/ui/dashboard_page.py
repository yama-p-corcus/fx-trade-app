from __future__ import annotations

from matplotlib.ticker import FuncFormatter
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
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
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    FigureCanvasQTAgg = None
    Figure = None
    plt = None


class DashboardPage(QWidget):
    _matplotlib_font_configured = False

    back_requested = pyqtSignal()
    filter_changed = pyqtSignal(str, int, int, str)
    trade_requested = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.current_chart_metric = "pips"
        self.current_payload: dict = {}
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
        self.period_combo = QComboBox()
        self.period_combo.addItem("月次", "month")
        self.period_combo.addItem("週次", "week")
        self.period_combo.currentIndexChanged.connect(self._sync_period_controls)
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(today.year())
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(today.month())
        self.week_date_edit = QDateEdit()
        self.week_date_edit.setCalendarPopup(True)
        self.week_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.week_date_edit.setDate(today)
        refresh_button = QPushButton("表示更新")
        refresh_button.clicked.connect(self._emit_filter_changed)

        controls_layout.addWidget(QLabel("期間"))
        controls_layout.addWidget(self.period_combo)
        controls_layout.addWidget(QLabel("年"))
        controls_layout.addWidget(self.year_spin)
        self.month_label = QLabel("月")
        controls_layout.addWidget(self.month_label)
        controls_layout.addWidget(self.month_spin)
        self.week_label = QLabel("基準日")
        controls_layout.addWidget(self.week_label)
        controls_layout.addWidget(self.week_date_edit)
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

        chart_toggle_layout = QHBoxLayout()
        chart_toggle_layout.addStretch()
        self.chart_toggle_button = QPushButton("損益表示へ切替")
        self.chart_toggle_button.setProperty("variant", "secondary")
        self.chart_toggle_button.clicked.connect(self._toggle_chart_metric)
        chart_toggle_layout.addWidget(self.chart_toggle_button)
        card_layout.addLayout(chart_toggle_layout)

        self.chart_notice = QLabel("")
        self.chart_notice.setWordWrap(True)
        self.chart_notice.setProperty("role", "subtitle")

        self._configure_matplotlib_font()
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
        self._sync_period_controls()

    def set_dashboard_data(self, payload: dict) -> None:
        self.current_payload = payload
        self._refresh_chart()

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

    def selected_filters(self) -> tuple[str, int, int, str]:
        return (
            self.period_combo.currentData(),
            self.year_spin.value(),
            self.month_spin.value(),
            self.week_date_edit.date().toString("yyyy-MM-dd"),
        )

    def _emit_filter_changed(self) -> None:
        self.filter_changed.emit(
            self.period_combo.currentData(),
            self.year_spin.value(),
            self.month_spin.value(),
            self.week_date_edit.date().toString("yyyy-MM-dd"),
        )

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

        ax.set_ylabel("pips" if self.current_chart_metric == "pips" else "損益")
        ax.set_facecolor("#ffffff")
        self.figure.patch.set_facecolor("#ffffff")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#cddfcf")
        ax.spines["bottom"].set_color("#cddfcf")
        ax.tick_params(colors="#365244")
        if self.current_chart_metric == "profit":
            ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _pos: f"{int(value):,}"))
        self.figure.tight_layout()
        self.canvas.draw()

    def _refresh_chart(self) -> None:
        payload = self.current_payload or {}
        if self.current_chart_metric == "pips":
            self.chart_title.setText(f"{payload.get('title', '')} - 獲得 pips")
            self.chart_toggle_button.setText("損益表示へ切替")
            chart_items = payload.get("chart_items_pips", [])
        else:
            self.chart_title.setText(f"{payload.get('title', '')} - 損益")
            self.chart_toggle_button.setText("pips表示へ切替")
            chart_items = payload.get("chart_items_profit", [])
        self._draw_chart(chart_items)

    def _toggle_chart_metric(self) -> None:
        self.current_chart_metric = "profit" if self.current_chart_metric == "pips" else "pips"
        self._refresh_chart()

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

    @classmethod
    def _configure_matplotlib_font(cls) -> None:
        if cls._matplotlib_font_configured or plt is None:
            return
        plt.rcParams["font.family"] = ["Meiryo", "Yu Gothic", "MS Gothic", "sans-serif"]
        plt.rcParams["axes.unicode_minus"] = False
        cls._matplotlib_font_configured = True

    def _sync_period_controls(self) -> None:
        is_month = self.period_combo.currentData() == "month"
        self.month_label.setVisible(is_month)
        self.month_spin.setVisible(is_month)
        self.week_label.setVisible(not is_month)
        self.week_date_edit.setVisible(not is_month)

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
