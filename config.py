import os
from dataclasses import dataclass


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    # Telegram / Cloud
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    webhook_secret: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

    # Market data: Twelve Data. No synthetic data in V1.1.
    market_data_api_key: str = os.getenv("TWELVE_DATA_API_KEY", "")
    market_data_base_url: str = os.getenv("TWELVE_DATA_BASE_URL", "https://api.twelvedata.com")
    symbol: str = os.getenv("DEFAULT_SYMBOL", "EUR/USD")
    interval: str = os.getenv("DEFAULT_INTERVAL", "1min")
    candles: int = _int("CANDLE_COUNT", 120)
    refresh_seconds: int = _int("MARKET_REFRESH_SECONDS", 20)

    # Trading model: paper/demo only.
    capital: float = _float("PAPER_CAPITAL", 100.0)
    risk_percent: float = _float("RISK_PERCENT", 1.0)
    payout_percent: float = _float("PAYOUT_PERCENT", 84.0)
    min_signal_score: float = _float("MIN_SIGNAL_SCORE", 70.0)
    max_trades_per_day: int = _int("MAX_TRADES_PER_DAY", 20)
    max_daily_loss_percent: float = _float("MAX_DAILY_LOSS_PERCENT", 10.0)
    max_consecutive_losses: int = _int("MAX_CONSECUTIVE_LOSSES", 3)
    expiration_seconds: int = _int("DEFAULT_EXPIRATION_SECONDS", 60)
    max_open_paper_trades: int = _int("MAX_OPEN_PAPER_TRADES", 3)

    # Persistence.
    data_dir: str = os.getenv("DATA_DIR", "data")
    journal_file: str = os.getenv("JOURNAL_FILE", "data/trade_journal.jsonl")

    # Safety locks.
    simulation_only: bool = True
    live_execution_enabled: bool = False


settings = Settings()
