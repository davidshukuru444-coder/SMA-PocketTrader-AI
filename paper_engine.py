import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from models import PaperTrade


class PaperEngine:
    def __init__(self, settings, provider, journal, risk):
        self.settings = settings
        self.provider = provider
        self.journal = journal
        self.risk = risk
        self.open_trades = {}
        self.lock = asyncio.Lock()

    def list_open(self):
        return list(self.open_trades.values())

    async def open(self, analysis, expiration_seconds: int, chat_id=None):
        async with self.lock:
            ok, msg = self.risk.can_trade(len(self.open_trades))
            if not ok:
                raise RuntimeError(msg)
            if analysis.direction == "WAIT":
                raise RuntimeError("Aucune direction exploitable.")
            if expiration_seconds <= 0:
                raise RuntimeError("Expiration invalide.")
            entry = analysis.price
            now = datetime.now(timezone.utc)
            trade = PaperTrade(
                id=uuid4().hex[:10], created_at=now.isoformat(), symbol=analysis.symbol,
                interval=analysis.interval, direction=analysis.direction, entry=entry,
                stake=self.risk.stake(), payout_percent=self.settings.payout_percent,
                expiration_seconds=expiration_seconds, score=analysis.score,
                expiry_at=(now + timedelta(seconds=expiration_seconds)).isoformat(),
            )
            if chat_id is not None:
                trade._chat_id = chat_id
            self.open_trades[trade.id] = trade
            row = {**trade.__dict__, "event": "OPEN", "status": "OPEN"}
            if chat_id is not None:
                row["chat_id"] = chat_id
            self.journal.append(row)
            return trade

    async def evaluate_due(self):
        now = datetime.now(timezone.utc)
        due = []
        for trade in list(self.open_trades.values()):
            expiry = datetime.fromisoformat(trade.expiry_at)
            if expiry <= now:
                due.append(trade)
        results = []
        for trade in due:
            try:
                exit_price = await self.provider.latest_close(trade.symbol, trade.interval)
            except Exception as exc:
                print(f"Paper evaluation error for {trade.id}: {exc}")
                continue
            if trade.direction == "CALL":
                result = "WIN" if exit_price > trade.entry else "LOSS" if exit_price < trade.entry else "TIE"
            else:
                result = "WIN" if exit_price < trade.entry else "LOSS" if exit_price > trade.entry else "TIE"
            if result == "WIN":
                pnl = round(trade.stake * trade.payout_percent / 100.0, 2)
            elif result == "LOSS":
                pnl = round(-trade.stake, 2)
            else:
                pnl = 0.0
            trade.status = "CLOSED"
            trade.result = result
            trade.pnl = pnl
            trade.exit_price = exit_price
            self.risk.register(pnl)
            row = {**trade.__dict__, "event": "CLOSE"}
            chat_id = getattr(trade, "_chat_id", None)
            if chat_id is not None:
                row["chat_id"] = chat_id
            self.journal.append(row)
            self.open_trades.pop(trade.id, None)
            results.append(trade)
        return results
