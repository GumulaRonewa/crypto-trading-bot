# app/discovery/scanner.py

from datetime import datetime, timezone

from .client import DexScreenerClient
from .models import CandidatePair


class CandidateScanner:

    def __init__(
        self,
        client: DexScreenerClient,
        min_liquidity_usd: float = 10_000,
        min_volume_5m_usd: float = 5_000,
        min_transactions_5m: int = 20,
        min_price_change_5m: float = 2.0,
    ):
        self.client = client

        self.min_liquidity_usd = min_liquidity_usd
        self.min_volume_5m_usd = min_volume_5m_usd
        self.min_transactions_5m = min_transactions_5m
        self.min_price_change_5m = min_price_change_5m

        self.seen_pairs: set[str] = set()

    async def discover_candidates(
        self,
        chain: str = "solana",
    ) -> list[CandidatePair]:

        candidates: list[CandidatePair] = []

        profiles = await self.client.get_latest_token_profiles()

        for profile in profiles:

            profile_chains = profile.get("chainId")

            if profile_chains and profile_chains != chain:
                continue

            token_address = profile.get("tokenAddress")

            if not token_address:
                continue

            try:
                pairs = await self.client.get_token_pairs(
                    chain,
                    token_address,
                )
            except Exception:
                continue

            for pair in pairs:

                candidate = self._parse_pair(pair)

                if candidate is None:
                    continue

                if not self._passes_filter(candidate):
                    continue

                if candidate.pair_address in self.seen_pairs:
                    continue

                self.seen_pairs.add(candidate.pair_address)

                candidates.append(candidate)

        candidates.sort(
            key=lambda x: x.activity_score,
            reverse=True,
        )

        return candidates

    def _passes_filter(
        self,
        candidate: CandidatePair,
    ) -> bool:

        if candidate.liquidity_usd < self.min_liquidity_usd:
            return False

        if candidate.volume_5m_usd < self.min_volume_5m_usd:
            return False

        if candidate.transactions_5m < self.min_transactions_5m:
            return False

        if candidate.price_change_5m < self.min_price_change_5m:
            return False

        return True

    def _parse_pair(
        self,
        pair: dict,
    ) -> CandidatePair | None:

        try:

            base = pair["baseToken"]
            quote = pair.get("quoteToken", {})

            liquidity = pair.get("liquidity") or {}
            volume = pair.get("volume") or {}
            txns = pair.get("txns") or {}
            price_change = pair.get("priceChange") or {}

            m5_txns = txns.get("m5") or {}

            return CandidatePair(
                chain=pair.get("chainId", ""),
                dex=pair.get("dexId", ""),

                pair_address=pair["pairAddress"],
                token_address=base["address"],

                symbol=base.get("symbol", ""),
                name=base.get("name", ""),

                quote_symbol=quote.get("symbol"),

                price_usd=self._float(
                    pair.get("priceUsd")
                ),

                liquidity_usd=self._float(
                    liquidity.get("usd")
                ) or 0.0,

                volume_5m_usd=self._float(
                    volume.get("m5")
                ) or 0.0,

                buys_5m=int(
                    m5_txns.get("buys", 0)
                ),

                sells_5m=int(
                    m5_txns.get("sells", 0)
                ),

                price_change_5m=self._float(
                    price_change.get("m5")
                ) or 0.0,

                market_cap=self._float(
                    pair.get("marketCap")
                ),

                pair_created_at=self._timestamp(
                    pair.get("pairCreatedAt")
                ),
            )

        except (KeyError, TypeError, ValueError):
            return None

    @staticmethod
    def _float(value):

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _timestamp(value):

        if value is None:
            return None

        try:
            return datetime.fromtimestamp(
                value / 1000,
                tz=timezone.utc,
            )
        except (TypeError, ValueError):
            return None