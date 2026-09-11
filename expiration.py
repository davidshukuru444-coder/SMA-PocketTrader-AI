def choose(score: float, volatility_score: float, default_seconds: int = 60) -> int:
    # Conservative candidate only; this is not an optimization guarantee.
    if score >= 85 and volatility_score >= 8:
        return min(120, max(60, default_seconds))
    if score >= 75:
        return 60
    return 0
