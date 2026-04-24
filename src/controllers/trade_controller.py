from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.models.trade import Trade
from src.services.trade_service import TradeService


class TradeController:
    def __init__(self, db_path: Path, images_dir: Path) -> None:
        self.service = TradeService(db_path=db_path, images_dir=images_dir)

    def get_calendar_summary(self, year: int, month: int) -> dict[str, int]:
        return self.service.get_daily_profit_summary(year=year, month=month)

    def get_trades_by_date(self, trade_date: str) -> list[Trade]:
        return self.service.get_trades_by_date(trade_date)

    def get_trade(self, trade_id: int) -> Trade | None:
        return self.service.get_trade(trade_id)

    def create_trade(self, payload: dict[str, Any]) -> int:
        return self.service.create_trade(payload)

    def update_trade(self, trade_id: int, payload: dict[str, Any]) -> None:
        self.service.update_trade(trade_id, payload)

    def delete_trade(self, trade_id: int) -> None:
        self.service.delete_trade(trade_id)

    @staticmethod
    def serialize_trade(trade: Trade) -> dict[str, Any]:
        return asdict(trade)
