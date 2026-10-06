# app/discovery/client.py

from typing import Any

import httpx


class DexScreenerClient:

    BASE_URL = "https://api.dexscreener.com"

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=10.0,
        )

    async def close(self):
        await self.client.aclose()

    async def get_latest_token_profiles(self) -> list[dict[str, Any]]:
        response = await self.client.get(
            "/token-profiles/latest/v1"
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            return []

        return data

    async def get_token_pairs(
        self,
        chain: str,
        token_address: str,
    ) -> list[dict[str, Any]]:

        response = await self.client.get(
            f"/token-pairs/v1/{chain}/{token_address}"
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            return []

        return data