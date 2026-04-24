from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Trade:
    id: int | None
    trade_date: str
    trade_time: str
    currency_pair: str
    order_price: float
    settlement_price: float
    lot: float
    pips: float
    trade_type: str
    profit: int
    entry_memo: str
    exit_memo: str
    image_path: str
    m15_image_path: str
    h1_image_path: str
    h4_image_path: str
    d1_image_path: str
    m15_comment: str
    h1_comment: str
    h4_comment: str
    d1_comment: str
