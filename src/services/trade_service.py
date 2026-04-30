from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from PyQt6.QtGui import QImage

from src.models.trade import Trade
from src.repositories.trade_repository import TradeRepository


class TradeService:
    TIMEFRAMES = ("m15", "h1", "h4", "d1")

    def __init__(self, db_path: Path, images_dir: Path) -> None:
        self.repository = TradeRepository(db_path)
        self.images_dir = images_dir

    def get_daily_profit_summary(self, year: int, month: int) -> dict[str, int]:
        return self.repository.fetch_daily_profit_summary(year, month)

    def get_trades_by_date(self, trade_date: str) -> list[Trade]:
        return self.repository.fetch_by_date(trade_date)

    def get_trade(self, trade_id: int) -> Trade | None:
        return self.repository.fetch_by_id(trade_id)

    def get_dashboard_data(self, year: int, month: int) -> dict[str, Any]:
        trades = self.repository.fetch_by_month(year, month)
        return self._build_dashboard_payload(
            trades=trades,
            period="month",
            year=year,
            month=month,
            title=f"{year}年{month}月 日別 pips",
        )

    def get_weekly_dashboard_data(self, selected_date: str) -> dict[str, Any]:
        target_date = date.fromisoformat(selected_date)
        start_date = target_date.fromordinal(target_date.toordinal() - target_date.weekday())
        end_date = start_date.fromordinal(start_date.toordinal() + 6)
        trades = self.repository.fetch_by_date_range(start_date.isoformat(), end_date.isoformat())
        return self._build_dashboard_payload(
            trades=trades,
            period="week",
            year=target_date.year,
            week=target_date.isocalendar().week,
            title=f"{start_date:%Y-%m-%d} ～ {end_date:%Y-%m-%d}",
            selected_date=selected_date,
        )

    def _build_dashboard_payload(
        self,
        trades: list[Trade],
        period: str,
        year: int,
        title: str,
        month: int | None = None,
        week: int | None = None,
        selected_date: str | None = None,
    ) -> dict[str, Any]:
        daily_pips: dict[str, float] = {}
        daily_profit: dict[str, int] = {}
        wins = 0
        losses = 0
        total_profit = 0
        total_loss_abs = 0
        table_rows: list[dict[str, Any]] = []

        for trade in trades:
            daily_pips.setdefault(trade.trade_date, 0.0)
            daily_pips[trade.trade_date] += trade.pips
            daily_profit.setdefault(trade.trade_date, 0)
            daily_profit[trade.trade_date] += trade.profit

            if trade.profit >= 0:
                wins += 1
                total_profit += trade.profit
            else:
                losses += 1
                total_loss_abs += abs(trade.profit)

            table_rows.append(
                {
                    "id": trade.id,
                    "date": trade.trade_date,
                    "time": trade.trade_time,
                    "currency_pair": trade.currency_pair,
                    "trade_type": "買い" if trade.trade_type == "buy" else "売り",
                    "pips": trade.pips,
                    "profit": trade.profit,
                }
            )

        total_count = wins + losses
        win_rate = round((wins / total_count) * 100, 1) if total_count else 0.0
        average_profit = round(total_profit / wins, 1) if wins else 0.0
        average_loss = round(total_loss_abs / losses, 1) if losses else 0.0

        chart_items_pips = [
            {
                "label": trade_date[-2:] if period == "month" else trade_date[5:],
                "value": round(value, 1),
                "color": "#64b5f6" if value >= 0 else "#ef9a9a",
            }
            for trade_date, value in sorted(daily_pips.items())
        ]
        chart_items_profit = [
            {
                "label": trade_date[-2:] if period == "month" else trade_date[5:],
                "value": value,
                "color": "#64b5f6" if value >= 0 else "#ef9a9a",
            }
            for trade_date, value in sorted(daily_profit.items())
        ]

        payload = {
            "period": period,
            "year": year,
            "title": title,
            "chart_items_pips": chart_items_pips,
            "chart_items_profit": chart_items_profit,
            "stats": {
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "average_profit": average_profit,
                "average_loss": average_loss,
            },
            "table_rows": table_rows,
            "total_profit": sum(trade.profit for trade in trades),
        }
        if month is not None:
            payload["month"] = month
        if week is not None:
            payload["week"] = week
        if selected_date is not None:
            payload["selected_date"] = selected_date
        return payload

    def create_trade(self, payload: dict[str, Any]) -> int:
        trade = self._validate_and_build(payload)
        trade_id = self.repository.insert(trade)
        image_path = self._persist_trade_image(trade_id, payload.get("image_source_path"))
        if image_path:
            self.repository.update_image_path(trade_id, image_path)
        self.repository.update_analysis_image_paths(
            trade_id,
            self._persist_timeframe_images(trade_id, payload, trade),
        )
        return trade_id

    def update_trade(self, trade_id: int, payload: dict[str, Any]) -> None:
        trade = self._validate_and_build(payload, trade_id=trade_id)
        self.repository.update(trade)
        image_path = self._persist_trade_image(trade_id, payload.get("image_source_path"))
        if image_path:
            self.repository.update_image_path(trade_id, image_path)
        self.repository.update_analysis_image_paths(
            trade_id,
            self._persist_timeframe_images(trade_id, payload, trade),
        )

    def delete_trade(self, trade_id: int) -> None:
        self.repository.delete(trade_id)

    def validate_trade_payload(self, payload: dict[str, Any]) -> None:
        self._validate_and_build(payload)

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
            image_path=str(payload.get("image_path", "")).strip(),
            m15_image_path=str(payload.get("m15_image_path", "")).strip(),
            h1_image_path=str(payload.get("h1_image_path", "")).strip(),
            h4_image_path=str(payload.get("h4_image_path", "")).strip(),
            d1_image_path=str(payload.get("d1_image_path", "")).strip(),
            m15_comment=str(payload.get("m15_comment", "")).strip(),
            h1_comment=str(payload.get("h1_comment", "")).strip(),
            h4_comment=str(payload.get("h4_comment", "")).strip(),
            d1_comment=str(payload.get("d1_comment", "")).strip(),
        )

    def _persist_trade_image(self, trade_id: int, source_path: Any) -> str:
        if not source_path:
            return ""

        source = Path(str(source_path))
        if not source.exists():
            return ""

        target_dir = self.images_dir / str(trade_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / "chart.png"
        if source.resolve() == target_path.resolve():
            return str(target_path)

        image = QImage(str(source))
        if image.isNull():
            return ""
        image.save(str(target_path), "PNG")
        return str(target_path)

    def _persist_timeframe_images(
        self,
        trade_id: int,
        payload: dict[str, Any],
        trade: Trade,
    ) -> dict[str, str]:
        image_paths = {
            "m15": trade.m15_image_path,
            "h1": trade.h1_image_path,
            "h4": trade.h4_image_path,
            "d1": trade.d1_image_path,
        }
        target_dir = self.images_dir / str(trade_id)
        target_dir.mkdir(parents=True, exist_ok=True)

        for timeframe in self.TIMEFRAMES:
            source_path = payload.get(f"{timeframe}_image_source_path")
            if not source_path:
                continue
            saved_path = self._save_png_image(
                source_path=source_path,
                target_path=target_dir / f"{timeframe}.png",
            )
            if saved_path:
                image_paths[timeframe] = saved_path
        return image_paths

    @staticmethod
    def _save_png_image(source_path: Any, target_path: Path) -> str:
        source = Path(str(source_path))
        if not source.exists():
            return ""
        if source.resolve() == target_path.resolve():
            return str(target_path)

        image = QImage(str(source))
        if image.isNull():
            return ""
        image.save(str(target_path), "PNG")
        return str(target_path)
