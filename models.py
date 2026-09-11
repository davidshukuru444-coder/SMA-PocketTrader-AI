from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class Candle:
    time: datetime
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class Analysis:
    symbol: str
    interval: str
    price: float
    direction: str
    score: float
    tier: str
    trend: float
    structure: float
    support_resistance: float
    price_action: float
    momentum: float
    volatility: float
    liquidity_smc: float
    context: float
    rsi: float
    ema_fast: float
    ema_slow: float
    atr: float
    support: float
    resistance: float
    reason: str
    data_source: str = "Twelve Data"

    def to_dict(self):
        return asdict(self)


@dataclass
class PaperTrade:
    id: str
    created_at: str
    symbol: str
    interval: str
    direction: str
    entry: float
    stake: float
    payout_percent: float
    expiration_seconds: int
    score: float
    status: str = "OPEN"
    result: Optional[str] = None
    pnl: float = 0.0
    expiry_at: Optional[str] = None
    exit_price: Optional[float] = None

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
