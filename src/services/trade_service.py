from __future__ import annotations

from pathlib import Path
from typing import Any

from src.models.trade import Trade
from src.repositories.trade_repository import TradeRepository


class TradeService:
    def __init__(self, db_path: Path, images_dir: Path) -> None:
        self.repository = TradeRepository(db_path)
        self.images_dir = images_dir

    def get_daily_profit_summary(self, year: int, month: int) -> dict[str, int]:
        return self.repository.fetch_daily_profit_summary(year, month)

    def get_trades_by_date(self, trade_date: str) -> list[Trade]:
        return self.repository.fetch_by_date(trade_date)

    def get_trade(self, trade_id: int) -> Trade | None:
        return self.repository.fetch_by_id(trade_id)

    def create_trade(self, payload: dict[str, Any]) -> int:
        trade = self._validate_and_build(payload)
        return self.repository.insert(trade)

    def update_trade(self, trade_id: int, payload: dict[str, Any]) -> None:
        trade = self._validate_and_build(payload, trade_id=trade_id)
        self.repository.update(trade)

    def delete_trade(self, trade_id: int) -> None:
        self.repository.delete(trade_id)

    def _validate_and_build(self, payload: dict[str, Any], trade_id: int | None = None) -> Trade:
        trade_date = str(payload["trade_date"]).strip()
        trade_time = str(payload["trade_time"]).strip()
        currency_pair = str(payload["currency_pair"]).strip().upper()
        trade_type = str(payload["trade_type"]).strip()
        entry_memo = str(payload.get("entry_memo", "")).strip()
        exit_memo = str(payload.get("exit_memo", "")).strip()

        if not trade_date:
            raise ValueError("日付は必須です。")
        if not trade_time:
            raise ValueError("時間は必須です。")
        if not currency_pair:
            raise ValueError("通貨ペアは必須です。")
        if trade_type not in {"buy", "sell"}:
            raise ValueError("売買区分は buy または sell を選択してください。")

        try:
            order_price = float(payload["order_price"])
            settlement_price = float(payload["settlement_price"])
            lot = float(payload["lot"])
            pips = float(payload["pips"])
            profit = int(payload["profit"])
        except (TypeError, ValueError) as exc:
            raise ValueError("数値項目を正しく入力してください。") from exc

        if order_price <= 0:
            raise ValueError("注文価格は 0 より大きい値を入力してください。")
        if settlement_price <= 0:
            raise ValueError("決済価格は 0 より大きい値を入力してください。")
        if lot <= 0:
            raise ValueError("ロット数は 0 より大きい値を入力してください。")

        return Trade(
            id=trade_id,
            trade_date=trade_date,
            trade_time=trade_time,
            currency_pair=currency_pair,
            order_price=order_price,
            settlement_price=settlement_price,
            lot=lot,
            pips=pips,
            trade_type=trade_type,
            profit=profit,
            entry_memo=entry_memo,
            exit_memo=exit_memo,
        )
