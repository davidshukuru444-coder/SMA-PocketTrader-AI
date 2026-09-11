import random

def simulate(direction,stake,payout_percent,estimated_win_rate):
    if direction=='WAIT': return 'WAIT',0.
    if random.random()<estimated_win_rate/100: return 'WIN',round(stake*payout_percent/100,2)
    return 'LOSS',round(-stake,2)
