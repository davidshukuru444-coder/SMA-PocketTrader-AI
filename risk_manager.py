from datetime import date


class RiskManager:
    def __init__(self, settings):
        self.settings = settings
        self.day = date.today().isoformat()
        self.trades = 0
        self.pnl = 0.0
        self.loss_streak = 0
        self.paused = True

    def _roll_day(self):
        today = date.today().isoformat()
        if today != self.day:
            self.day = today
            self.trades = 0
            self.pnl = 0.0
            self.loss_streak = 0

    def stake(self) -> float:
        return round(self.settings.capital * self.settings.risk_percent / 100.0, 2)

    def can_trade(self, open_trades: int = 0):
        self._roll_day()
        if self.paused:
            return False, "Robot en pause."
        if open_trades >= self.settings.max_open_paper_trades:
            return False, "Nombre maximal de simulations ouvertes atteint."
        if self.trades >= self.settings.max_trades_per_day:
            return False, "Nombre maximal de trades atteint."
        if self.pnl <= -self.settings.capital * self.settings.max_daily_loss_percent / 100.0:
            return False, "Limite de perte journalière atteinte."
        if self.loss_streak >= self.settings.max_consecutive_losses:
            return False, "Limite de pertes consécutives atteinte."
        return True, "OK"

    def register(self, pnl: float):
        self._roll_day()
        self.trades += 1
        self.pnl += pnl
        self.loss_streak = self.loss_streak + 1 if pnl < 0 else 0
