def break_even_win_rate(payout_percent):
    p=payout_percent/100
    return 100/(1+p) if p>0 else 100

def edge_estimate(win_rate_percent,payout_percent):
    return (win_rate_percent/100)*(payout_percent/100)-(1-win_rate_percent/100)
