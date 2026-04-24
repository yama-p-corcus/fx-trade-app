from __future__ import annotations

from pathlib import Path

from src.database.connection import get_connection
from src.models.trade import Trade


class TradeRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def fetch_daily_profit_summary(self, year: int, month: int) -> dict[str, int]:
        month_key = f"{year:04d}-{month:02d}"
        query = """
            SELECT trade_date, SUM(profit) AS total_profit
            FROM trades
            WHERE substr(trade_date, 1, 7) = ?
            GROUP BY trade_date
        """
        with get_connection(self.db_path) as connection:
            rows = connection.execute(query, (month_key,)).fetchall()
        return {row["trade_date"]: int(row["total_profit"]) for row in rows}

    def fetch_by_date(self, trade_date: str) -> list[Trade]:
        query = """
            SELECT
                id,
                trade_date,
                trade_time,
                currency_pair,
                order_price,
                settlement_price,
                lot,
                pips,
                trade_type,
                profit,
                entry_memo,
                exit_memo
            FROM trades
            WHERE trade_date = ?
            ORDER BY trade_time DESC, id DESC
        """
        with get_connection(self.db_path) as connection:
            rows = connection.execute(query, (trade_date,)).fetchall()
        return [self._row_to_trade(row) for row in rows]

    def fetch_by_id(self, trade_id: int) -> Trade | None:
        query = """
            SELECT
                id,
                trade_date,
                trade_time,
                currency_pair,
                order_price,
                settlement_price,
                lot,
                pips,
                trade_type,
                profit,
                entry_memo,
                exit_memo
            FROM trades
            WHERE id = ?
        """
        with get_connection(self.db_path) as connection:
            row = connection.execute(query, (trade_id,)).fetchone()
        return self._row_to_trade(row) if row else None

    def insert(self, trade: Trade) -> int:
        query = """
            INSERT INTO trades (
                trade_date,
                trade_time,
                currency_pair,
                order_price,
                settlement_price,
                lot,
                pips,
                trade_type,
                profit,
                entry_memo,
                exit_memo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            trade.trade_date,
            trade.trade_time,
            trade.currency_pair,
            trade.order_price,
            trade.settlement_price,
            trade.lot,
            trade.pips,
            trade.trade_type,
            trade.profit,
            trade.entry_memo,
            trade.exit_memo,
        )
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def update(self, trade: Trade) -> None:
        query = """
            UPDATE trades
            SET
                trade_date = ?,
                trade_time = ?,
                currency_pair = ?,
                order_price = ?,
                settlement_price = ?,
                lot = ?,
                pips = ?,
                trade_type = ?,
                profit = ?,
                entry_memo = ?,
                exit_memo = ?
            WHERE id = ?
        """
        values = (
            trade.trade_date,
            trade.trade_time,
            trade.currency_pair,
            trade.order_price,
            trade.settlement_price,
            trade.lot,
            trade.pips,
            trade.trade_type,
            trade.profit,
            trade.entry_memo,
            trade.exit_memo,
            trade.id,
        )
        with get_connection(self.db_path) as connection:
            connection.execute(query, values)
            connection.commit()

    def delete(self, trade_id: int) -> None:
        with get_connection(self.db_path) as connection:
            connection.execute("DELETE FROM trades WHERE id = ?", (trade_id,))
            connection.commit()

    @staticmethod
    def _row_to_trade(row) -> Trade:
        return Trade(
            id=int(row["id"]),
            trade_date=row["trade_date"],
            trade_time=row["trade_time"],
            currency_pair=row["currency_pair"],
            order_price=float(row["order_price"]),
            settlement_price=float(row["settlement_price"]),
            lot=float(row["lot"]),
            pips=float(row["pips"]),
            trade_type=row["trade_type"],
            profit=int(row["profit"]),
            entry_memo=row["entry_memo"] or "",
            exit_memo=row["exit_memo"] or "",
        )
