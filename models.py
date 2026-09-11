from dataclasses import dataclass
from datetime import datetime

@dataclass
class Candle:
    time: datetime
    open: float
    high: float
    low: float
    close: float

@dataclass
class Analysis:
    trend: float
    structure: float
    support_resistance: float
    price_action: float
    momentum: float
    volatility: float
    liquidity_smc: float
    context: float
    direction: str
    score: float
    reason: str
