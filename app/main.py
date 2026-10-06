# app/main.py

import asyncio

from app.discovery.client import DexScreenerClient
from app.discovery.scanner import CandidateScanner


async def main():

    client = DexScreenerClient()

    scanner = CandidateScanner(
        client,

        min_liquidity_usd=10_000,
        min_volume_5m_usd=5_000,
        min_transactions_5m=20,
        min_price_change_5m=2,
    )

    try:

        candidates = await scanner.discover_candidates(
            chain="solana"
        )

        print(
            f"Found {len(candidates)} candidates"
        )

        for candidate in candidates[:20]:

            print(
                f"""
                {candidate.symbol}
                DEX: {candidate.dex}
                Pair: {candidate.pair_address}
                Price: ${candidate.price_usd}
                Liquidity: ${candidate.liquidity_usd:,.0f}
                Volume 5m: ${candidate.volume_5m_usd:,.0f}
                Transactions: {candidate.transactions_5m}
                Buy ratio: {candidate.buy_ratio_5m:.2%}
                Price change 5m: {candidate.price_change_5m:.2f}%
                Score: {candidate.activity_score:.2f}
                """
            )

    finally:

        await client.close()


if __name__ == "__main__":
    asyncio.run(main())