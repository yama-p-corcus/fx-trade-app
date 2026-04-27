from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStackedWidget,
)

from src.controllers.trade_controller import TradeController
from src.ui.dashboard_page import DashboardPage
from src.ui.menu_page import MenuPage
from src.ui.styles import APP_STYLESHEET
from src.ui.trade_calendar_page import TradeCalendarPage
from src.ui.trade_form_dialog import TradeFormDialog
from src.ui.trade_list_page import TradeListPage


class MainWindow(QMainWindow):
    def __init__(self, db_path: Path, images_dir: Path) -> None:
        super().__init__()
        self.setWindowTitle("FX Trade Journal")
        self.resize(1120, 760)

        self.controller = TradeController(db_path=db_path, images_dir=images_dir)
        self.selected_date = ""
        self.last_currency_pair = ""

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.setStyleSheet(APP_STYLESHEET)

        self.menu_page = MenuPage()
        self.calendar_page = TradeCalendarPage()
        self.trade_list_page = TradeListPage()
        self.dashboard_page = DashboardPage()

        self.stack.addWidget(self.menu_page)
        self.stack.addWidget(self.calendar_page)
        self.stack.addWidget(self.trade_list_page)
        self.stack.addWidget(self.dashboard_page)

        self.menu_page.open_calendar.connect(self.show_calendar_page)
        self.menu_page.open_dashboard.connect(self.show_dashboard_page)
        self.calendar_page.back_requested.connect(self.show_menu_page)
        self.calendar_page.date_selected.connect(self.show_trade_list_for_date)
        self.calendar_page.month_changed.connect(self.refresh_calendar_highlights)
        self.trade_list_page.back_requested.connect(self.show_calendar_page)
        self.trade_list_page.add_requested.connect(self.open_create_dialog)
        self.trade_list_page.edit_requested.connect(self.open_edit_dialog)
        self.trade_list_page.delete_requested.connect(self.delete_trade)
        self.dashboard_page.back_requested.connect(self.show_menu_page)
        self.dashboard_page.filter_changed.connect(self.refresh_dashboard)
        self.dashboard_page.trade_requested.connect(self.open_edit_dialog)

        self.show_menu_page()

    def show_menu_page(self) -> None:
        self.stack.setCurrentWidget(self.menu_page)

    def show_calendar_page(self) -> None:
        self.stack.setCurrentWidget(self.calendar_page)
        year, month = self.calendar_page.visible_year_month()
        self.refresh_calendar_highlights(year, month)

    def show_dashboard_page(self) -> None:
        self.stack.setCurrentWidget(self.dashboard_page)
        year, month = self.dashboard_page.selected_year_month()
        self.refresh_dashboard(year, month)

    def show_trade_list_for_date(self, trade_date: str) -> None:
        self.selected_date = trade_date
        self.stack.setCurrentWidget(self.trade_list_page)
        self._reload_trade_list()

    def refresh_calendar_highlights(self, year: int, month: int) -> None:
        summary = self.controller.get_calendar_summary(year, month)
        self.calendar_page.apply_trade_highlights(summary)

    def open_create_dialog(self, default_date: str) -> None:
        dialog = TradeFormDialog(
            self,
            default_date=default_date,
            last_currency_pair=self.last_currency_pair,
            validate_callback=self.controller.validate_trade_payload,
        )
        if dialog.exec():
            payload = dialog.get_payload()
            self.controller.create_trade(payload)
            self.last_currency_pair = payload["currency_pair"]
            self._after_trade_changed(payload["trade_date"])

    def open_edit_dialog(self, trade_id: int) -> None:
        trade = self.controller.get_trade(trade_id)
        if not trade:
            return

        previous_date = trade.trade_date
        dialog = TradeFormDialog(
            self,
            trade=trade,
            last_currency_pair=self.last_currency_pair,
            validate_callback=self.controller.validate_trade_payload,
        )
        if dialog.exec():
            payload = dialog.get_payload()
            self.controller.update_trade(trade_id, payload)
            self.last_currency_pair = payload["currency_pair"]
            self._after_trade_changed(payload["trade_date"], previous_date=previous_date)

    def delete_trade(self, trade_id: int) -> None:
        trade = self.controller.get_trade(trade_id)
        if not trade:
            QMessageBox.warning(self, "エラー", "対象のトレードが見つかりません。")
            return

        response = QMessageBox.question(
            self,
            "削除確認",
            f"{trade.trade_date} {trade.trade_time} のトレードを削除しますか？",
        )
        if response != QMessageBox.StandardButton.Yes:
            return

        self.controller.delete_trade(trade_id)
        self._after_trade_changed(self.selected_date, previous_date=trade.trade_date)

    def _after_trade_changed(self, active_date: str, previous_date: str | None = None) -> None:
        self.selected_date = active_date
        self._reload_trade_list()

        year, month = self.calendar_page.visible_year_month()
        self.refresh_calendar_highlights(year, month)

        if previous_date and previous_date != active_date:
            self.refresh_calendar_highlights(year, month)

    def _reload_trade_list(self) -> None:
        trades = self.controller.get_trades_by_date(self.selected_date)
        self.trade_list_page.load_trades(self.selected_date, trades)

    def refresh_dashboard(self, year: int, month: int) -> None:
        payload = self.controller.get_dashboard_data(year, month)
        self.dashboard_page.set_dashboard_data(payload)
