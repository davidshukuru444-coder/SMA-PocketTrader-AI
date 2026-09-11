from math import sqrt
from statistics import mean
from typing import List

from models import Analysis, Candle


def ema(values: List[float], period: int) -> float:
    if len(values) < period:
        raise ValueError("Pas assez de données pour EMA")
    alpha = 2 / (period + 1)
    result = values[0]
    for value in values[1:]:
        result = alpha * value + (1 - alpha) * result
    return result


def atr(candles: List[Candle], period: int = 14) -> float:
    if len(candles) < period + 1:
        raise ValueError("Pas assez de données pour ATR")
    trs = []
    for i in range(1, len(candles)):
        c, p = candles[i], candles[i - 1]
        trs.append(max(c.high - c.low, abs(c.high - p.close), abs(c.low - p.close)))
    return mean(trs[-period:])


def rsi(candles: List[Candle], period: int = 14) -> float:
    closes = [c.close for c in candles]
    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    if len(changes) < period:
        raise ValueError("Pas assez de données pour RSI")
    gains = [max(x, 0) for x in changes[-period:]]
    losses = [max(-x, 0) for x in changes[-period:]]
    avg_gain, avg_loss = mean(gains), mean(losses)
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def analyze(candles: List[Candle], symbol: str, interval: str) -> Analysis:
    if len(candles) < 60:
        raise ValueError("Il faut au moins 60 bougies de marché réel.")

    closes = [c.close for c in candles]
    fast = ema(closes[-80:], 9)
    slow = ema(closes[-80:], 21)
    current = candles[-1]
    atr_value = atr(candles, 14)
    rsi_value = rsi(candles, 14)

    # Trend (20): EMA alignment + recent slope.
    slope = closes[-1] - closes[-10]
    trend = 20 if fast > slow and slope > 0 else 20 if fast < slow and slope < 0 else 10
    direction = "CALL" if fast > slow and slope > 0 else "PUT" if fast < slow and slope < 0 else "WAIT"

    # Structure (15): simple HH/HL or LH/LL proxy over two windows.
    prev_high = max(c.high for c in candles[-30:-10])
    recent_high = max(c.high for c in candles[-10:])
    prev_low = min(c.low for c in candles[-30:-10])
    recent_low = min(c.low for c in candles[-10:])
    if direction == "CALL" and recent_high > prev_high and recent_low >= prev_low:
        structure = 15
    elif direction == "PUT" and recent_low < prev_low and recent_high <= prev_high:
        structure = 15
    else:
        structure = 8

    # S/R (15): proximity to recent range edge, avoiding mid-range entries.
    window = candles[-40:]
    support = min(c.low for c in window)
    resistance = max(c.high for c in window)
    span = max(resistance - support, 1e-12)
    position = (current.close - support) / span
    sr = 15 if (direction == "CALL" and position <= 0.30) or (direction == "PUT" and position >= 0.70) else 8

    # Price action (15): body strength and close location.
    candle_range = max(current.high - current.low, 1e-12)
    body_ratio = abs(current.close - current.open) / candle_range
    close_location = (current.close - current.low) / candle_range
    pa = 15 if body_ratio >= 0.60 and ((direction == "CALL" and close_location >= 0.65) or (direction == "PUT" and close_location <= 0.35)) else 8

    # Momentum (10): RSI confirmation without treating RSI as a standalone signal.
    if direction == "CALL":
        momentum = 10 if 52 <= rsi_value <= 68 else 6 if rsi_value < 75 else 2
    elif direction == "PUT":
        momentum = 10 if 32 <= rsi_value <= 48 else 6 if rsi_value > 25 else 2
    else:
        momentum = 4

    # Volatility (10): ATR relative to price, penalize extremely dead markets.
    atr_pct = atr_value / current.close if current.close else 0
    volatility = 10 if atr_pct >= 0.0005 else 6 if atr_pct >= 0.0002 else 2

    # Liquidity/SMC proxy (10): recent sweep/rejection of a 20-bar extreme.
    prior = candles[-21:-1]
    prior_high = max(c.high for c in prior)
    prior_low = min(c.low for c in prior)
    sweep_call = current.low < prior_low and current.close > prior_low
    sweep_put = current.high > prior_high and current.close < prior_high
    liquidity = 10 if (direction == "CALL" and sweep_call) or (direction == "PUT" and sweep_put) else 6

    # Context (5): alignment across 5m-like aggregation is approximated from 1m data.
    context_slope = closes[-1] - closes[-30]
    context = 5 if (direction == "CALL" and context_slope > 0) or (direction == "PUT" and context_slope < 0) else 2

    score = round(max(0, min(100, trend + structure + sr + pa + momentum + volatility + liquidity + context)), 2)
    tier = "PRIME" if score >= 85 and direction != "WAIT" else "STANDARD" if score >= 70 and direction != "WAIT" else "ATTENTE"

    reasons = [
        f"EMA9={fast:.5f} / EMA21={slow:.5f}",
        f"RSI={rsi_value:.1f}",
        f"ATR={atr_value:.5f}",
        f"position range={position:.2f}",
    ]
    if sweep_call or sweep_put:
        reasons.append("sweep/rejet de liquidité détecté")

    return Analysis(
        symbol=symbol, interval=interval, price=current.close, direction=direction, score=score, tier=tier,
        trend=float(trend), structure=float(structure), support_resistance=float(sr), price_action=float(pa),
        momentum=float(momentum), volatility=float(volatility), liquidity_smc=float(liquidity), context=float(context),
        rsi=round(rsi_value, 2), ema_fast=fast, ema_slow=slow, atr=atr_value,
        support=support, resistance=resistance, reason="; ".join(reasons)
    )
