from dataclasses import dataclass

@dataclass
class Settings:
    capital: float = 100.0
    risk_percent: float = 1.0
    max_trades_per_day: int = 20
    max_daily_loss_percent: float = 10.0
    max_consecutive_losses: int = 3
    payout_percent: float = 84.0
    timeframe: str = "M1"
    min_signal_score: float = 70.0
    simulation_only: bool = True
