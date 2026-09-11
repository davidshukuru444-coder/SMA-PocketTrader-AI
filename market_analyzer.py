from statistics import mean

def analyze(candles):
    if len(candles)<30: raise ValueError('Il faut au moins 30 bougies.')
    recent=candles[-10:]; closes=[c.close for c in recent]; slope=closes[-1]-closes[0]
    bullish=sum(c.close>c.open for c in recent); bearish=sum(c.close<c.open for c in recent)
    highs=[c.high for c in candles[-20:]]; lows=[c.low for c in candles[-20:]]
    price=candles[-1].close; rng=max(highs)-min(lows); pos=(price-min(lows))/rng if rng else .5
    body=abs(candles[-1].close-candles[-1].open); cr=candles[-1].high-candles[-1].low; br=body/cr if cr else 0
    rets=[(c.close-c.open)/c.open for c in recent]; vol=mean(abs(x) for x in rets) if rets else 0
    momentum=abs(slope)/price if price else 0
    trend=min(20,10+(bullish-bearish)*1.2) if slope>0 else min(20,10+(bearish-bullish)*1.2)
    structure=12 if abs(slope)>price*.0002 else 7
    sr=12 if pos<.2 or pos>.8 else 7; pa=13 if br>=.55 else 8
    mom=min(10,5+momentum*5000); volatility=8 if vol>.0001 else 5
    liquidity=8 if pos<.15 or pos>.85 else 5; context=4 if vol<.003 else 2
    direction='CALL' if slope>0 else 'PUT' if slope<0 else 'WAIT'
    score=round(max(0,min(100,trend+structure+sr+pa+mom+volatility+liquidity+context)),2)
    reason=f"Tendance={'haussière' if slope>0 else 'baissière' if slope<0 else 'neutre'}; position range={pos:.2f}; corps dernière bougie={br:.2f}"
    return dict(trend=round(trend,2),structure=round(structure,2),support_resistance=round(sr,2),price_action=round(pa,2),momentum=round(mom,2),volatility=round(volatility,2),liquidity_smc=round(liquidity,2),context=round(context,2),direction=direction,score=score,reason=reason)
