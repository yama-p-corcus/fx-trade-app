from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Path) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_date TEXT NOT NULL,
                trade_time TEXT NOT NULL,
                currency_pair TEXT NOT NULL,
                order_price REAL NOT NULL,
                settlement_price REAL NOT NULL,
                lot REAL NOT NULL,
                pips REAL NOT NULL,
                trade_type TEXT NOT NULL CHECK (trade_type IN ('buy', 'sell')),
                profit INTEGER NOT NULL,
                entry_memo TEXT NOT NULL DEFAULT '',
                exit_memo TEXT NOT NULL DEFAULT '',
                image_path TEXT NOT NULL DEFAULT '',
                m15_image_path TEXT NOT NULL DEFAULT '',
                h1_image_path TEXT NOT NULL DEFAULT '',
                h4_image_path TEXT NOT NULL DEFAULT '',
                d1_image_path TEXT NOT NULL DEFAULT '',
                m15_comment TEXT NOT NULL DEFAULT '',
                h1_comment TEXT NOT NULL DEFAULT '',
                h4_comment TEXT NOT NULL DEFAULT '',
                d1_comment TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(trades)").fetchall()
        }
        required_columns = {
            "image_path": "TEXT NOT NULL DEFAULT ''",
            "m15_image_path": "TEXT NOT NULL DEFAULT ''",
            "h1_image_path": "TEXT NOT NULL DEFAULT ''",
            "h4_image_path": "TEXT NOT NULL DEFAULT ''",
            "d1_image_path": "TEXT NOT NULL DEFAULT ''",
            "m15_comment": "TEXT NOT NULL DEFAULT ''",
            "h1_comment": "TEXT NOT NULL DEFAULT ''",
            "h4_comment": "TEXT NOT NULL DEFAULT ''",
            "d1_comment": "TEXT NOT NULL DEFAULT ''",
        }
        for column_name, column_definition in required_columns.items():
            if column_name not in columns:
                connection.execute(
                    f"ALTER TABLE trades ADD COLUMN {column_name} {column_definition}"
                )

        connection.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trades_updated_at_trigger
            AFTER UPDATE ON trades
            FOR EACH ROW
            BEGIN
                UPDATE trades
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = OLD.id;
            END;
            """
        )
