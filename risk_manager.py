class RiskManager:
    def __init__(self,settings): self.settings=settings; self.trades=0; self.pnl=0.; self.loss_streak=0; self.paused=True
    def stake(self): return round(self.settings.capital*self.settings.risk_percent/100,2)
    def can_trade(self):
        if self.paused:return False,'Robot en pause.'
        if self.trades>=self.settings.max_trades_per_day:return False,'Nombre maximal de trades atteint.'
        if self.pnl<=-self.settings.capital*self.settings.max_daily_loss_percent/100:return False,'Limite de perte journalière atteinte.'
        if self.loss_streak>=self.settings.max_consecutive_losses:return False,'Limite de pertes consécutives atteinte.'
        return True,'OK'
    def register(self,pnl): self.trades+=1; self.pnl+=pnl; self.loss_streak=self.loss_streak+1 if pnl<0 else 0
