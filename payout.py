def break_even_win_rate(payout_percent: float) -> float:
    p = payout_percent / 100.0
    return 100.0 / (1.0 + p) if p > 0 else 100.0


def edge_estimate(win_rate_percent: float, payout_percent: float) -> float:
    w = win_rate_percent / 100.0
    p = payout_percent / 100.0
    return w * p - (1.0 - w)
