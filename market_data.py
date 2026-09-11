import asyncio
from datetime import datetime, timezone
from typing import List

import httpx

from models import Candle


class MarketDataError(RuntimeError):
    pass


class TwelveDataProvider:
    """Live/historical market data provider. Synthetic candles are deliberately unsupported."""

    def __init__(self, api_key: str, base_url: str, timeout: float = 12.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def configured(self) -> bool:
        return bool(self.api_key)

    async def candles(self, symbol: str, interval: str, outputsize: int = 120) -> List[Candle]:
        if not self.api_key:
            raise MarketDataError(
                "TWELVE_DATA_API_KEY n'est pas configurée. V1.1 refuse de fabriquer des bougies."
            )
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": max(30, min(int(outputsize), 5000)),
            "apikey": self.api_key,
            "timezone": "UTC",
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/time_series", params=params)
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise MarketDataError(f"Impossible de récupérer les données de marché: {exc}") from exc

        if payload.get("status") == "error" or "values" not in payload:
            raise MarketDataError(payload.get("message", "Réponse Twelve Data invalide."))

        candles: List[Candle] = []
        for row in reversed(payload["values"]):
            try:
                dt = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                candles.append(Candle(dt, float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"])))
            except (KeyError, TypeError, ValueError):
                continue
        if len(candles) < 30:
            raise MarketDataError(f"Données insuffisantes: {len(candles)} bougies reçues.")
        return candles

    async def latest_close(self, symbol: str, interval: str) -> float:
        candles = await self.candles(symbol, interval, outputsize=2)
        return candles[-1].close
