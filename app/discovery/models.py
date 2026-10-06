# app/discovery/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CandidatePair:
    chain: str
    dex: str

    pair_address: str
    token_address: str

    symbol: str
    name: str

    quote_symbol: Optional[str]

    price_usd: Optional[float]

    liquidity_usd: float

    volume_5m_usd: float
    buys_5m: int
    sells_5m: int

    price_change_5m: float

    market_cap: Optional[float]

    pair_created_at: Optional[datetime]

    @property
    def transactions_5m(self) -> int:
        return self.buys_5m + self.sells_5m

    @property
    def buy_ratio_5m(self) -> float:
        txns = self.transactions_5m

        if txns == 0:
            return 0.0

        return self.buys_5m / txns

    @property
    def activity_score(self) -> float:
        """
        Very basic ranking score.

        This is NOT the trading strategy.
        It only helps us decide which candidates
        deserve real-time monitoring.
        """

        volume_score = min(self.volume_5m_usd / 10_000, 10)

        transaction_score = min(
            self.transactions_5m / 100,
            10,
        )

        momentum_score = max(
            self.price_change_5m,
            0,
        )

        buy_pressure = self.buy_ratio_5m * 10

        return (
            volume_score
            + transaction_score
            + momentum_score
            + buy_pressure
        )