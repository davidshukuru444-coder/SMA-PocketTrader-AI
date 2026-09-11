import csv
from pathlib import Path
PATH=Path('trade_journal.csv')
FIELDS=['time','symbol','direction','stake','expiration_seconds','score','payout_percent','result','pnl']
def log(row):
    exists=PATH.exists()
    with PATH.open('a',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if not exists:w.writeheader()
        w.writerow({k:row.get(k,'') for k in FIELDS})
def stats():
    if not PATH.exists():return {'trades':0,'wins':0,'losses':0,'win_rate':0.,'pnl':0.}
    rows=list(csv.DictReader(PATH.open(encoding='utf-8'))); wins=sum(r['result']=='WIN' for r in rows); losses=sum(r['result']=='LOSS' for r in rows); total=wins+losses; pnl=sum(float(r['pnl']) for r in rows)
    return {'trades':total,'wins':wins,'losses':losses,'win_rate':round(wins/total*100,2) if total else 0.,'pnl':round(pnl,2)}
