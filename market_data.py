from datetime import datetime, timedelta
import random
from models import Candle

def synthetic_candles(n=120, start=100.0, bullish=True):
    candles=[]; price=start; now=datetime.now(); drift=0.00035 if bullish else -0.00035
    for i in range(n):
        change=drift+random.gauss(0,0.0012); op=price; close=max(.01,price*(1+change))
        high=max(op,close)*(1+abs(random.gauss(0,.0005)))
        low=min(op,close)*(1-abs(random.gauss(0,.0005)))
        candles.append(Candle(now-timedelta(minutes=n-i),op,high,low,close)); price=close
    return candles
