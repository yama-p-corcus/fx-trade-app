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
                exit_memo,
                image_path,
                m15_image_path,
                h1_image_path,
                h4_image_path,
                d1_image_path,
                m15_comment,
                h1_comment,
                h4_comment,
                d1_comment
            FROM trades
            WHERE trade_date = ?
            ORDER BY trade_time DESC, id DESC
        """
        with get_connection(self.db_path) as connection:
            rows = connection.execute(query, (trade_date,)).fetchall()
        return [self._row_to_trade(row) for row in rows]

    def fetch_by_month(self, year: int, month: int) -> list[Trade]:
        month_key = f"{year:04d}-{month:02d}"
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
                exit_memo,
                image_path,
                m15_image_path,
                h1_image_path,
                h4_image_path,
                d1_image_path,
                m15_comment,
                h1_comment,
                h4_comment,
                d1_comment
            FROM trades
            WHERE substr(trade_date, 1, 7) = ?
            ORDER BY trade_date ASC, trade_time ASC, id ASC
        """
        with get_connection(self.db_path) as connection:
            rows = connection.execute(query, (month_key,)).fetchall()
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
                exit_memo,
                image_path,
                m15_image_path,
                h1_image_path,
                h4_image_path,
                d1_image_path,
                m15_comment,
                h1_comment,
                h4_comment,
                d1_comment
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
                exit_memo,
                image_path,
                m15_image_path,
                h1_image_path,
                h4_image_path,
                d1_image_path,
                m15_comment,
                h1_comment,
                h4_comment,
                d1_comment
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            trade.image_path,
            trade.m15_image_path,
            trade.h1_image_path,
            trade.h4_image_path,
            trade.d1_image_path,
            trade.m15_comment,
            trade.h1_comment,
            trade.h4_comment,
            trade.d1_comment,
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
                exit_memo = ?,
                image_path = ?,
                m15_image_path = ?,
                h1_image_path = ?,
                h4_image_path = ?,
                d1_image_path = ?,
                m15_comment = ?,
                h1_comment = ?,
                h4_comment = ?,
                d1_comment = ?
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
            trade.image_path,
            trade.m15_image_path,
            trade.h1_image_path,
            trade.h4_image_path,
            trade.d1_image_path,
            trade.m15_comment,
            trade.h1_comment,
            trade.h4_comment,
            trade.d1_comment,
            trade.id,
        )
        with get_connection(self.db_path) as connection:
            connection.execute(query, values)
            connection.commit()

    def update_image_path(self, trade_id: int, image_path: str) -> None:
        with get_connection(self.db_path) as connection:
            connection.execute("UPDATE trades SET image_path = ? WHERE id = ?", (image_path, trade_id))
            connection.commit()

    def update_analysis_image_paths(self, trade_id: int, image_paths: dict[str, str]) -> None:
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                UPDATE trades
                SET
                    m15_image_path = ?,
                    h1_image_path = ?,
                    h4_image_path = ?,
                    d1_image_path = ?
                WHERE id = ?
                """,
                (
                    image_paths.get("m15", ""),
                    image_paths.get("h1", ""),
                    image_paths.get("h4", ""),
                    image_paths.get("d1", ""),
                    trade_id,
                ),
            )
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
            image_path=row["image_path"] or "",
            m15_image_path=row["m15_image_path"] or "",
            h1_image_path=row["h1_image_path"] or "",
            h4_image_path=row["h4_image_path"] or "",
            d1_image_path=row["d1_image_path"] or "",
            m15_comment=row["m15_comment"] or "",
            h1_comment=row["h1_comment"] or "",
            h4_comment=row["h4_comment"] or "",
            d1_comment=row["d1_comment"] or "",
        )
