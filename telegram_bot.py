import asyncio
from dataclasses import dataclass
from typing import Dict, Set

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import settings
from expiration import choose
from journal import Journal
from market_analyzer import analyze
from market_data import TwelveDataProvider, MarketDataError
from paper_engine import PaperEngine
from payout import break_even_win_rate
from risk_manager import RiskManager


journal = Journal(settings.journal_file)
provider = TwelveDataProvider(settings.market_data_api_key, settings.market_data_base_url)
subscribers: Set[int] = set()


@dataclass
class UserSession:
    risk: RiskManager
    paper: PaperEngine


sessions: Dict[int, UserSession] = {}


def session_for(chat_id: int) -> UserSession:
    if chat_id not in sessions:
        risk = RiskManager(settings)
        sessions[chat_id] = UserSession(risk=risk, paper=PaperEngine(settings, provider, journal, risk))
    return sessions[chat_id]


def fmt_analysis(a):
    return (
        f"🔎 {a.symbol} · {a.interval}\n\n"
        f"{'🟢 CALL' if a.direction == 'CALL' else '🔴 PUT' if a.direction == 'PUT' else '⚪ WAIT'}\n"
        f"Score d'analyse : {a.score}/100\n"
        f"Niveau : {a.tier}\n\n"
        f"Tendance : {a.trend:.0f}/20\nStructure : {a.structure:.0f}/15\n"
        f"Support/Résistance : {a.support_resistance:.0f}/15\nPrice Action : {a.price_action:.0f}/15\n"
        f"Momentum : {a.momentum:.0f}/10\nVolatilité : {a.volatility:.0f}/10\n"
        f"Liquidité/SMC : {a.liquidity_smc:.0f}/10\nContexte : {a.context:.0f}/5\n\n"
        f"Prix : {a.price}\nRSI : {a.rsi:.1f}\n"
        f"Support : {a.support}\nRésistance : {a.resistance}\n"
        f"Source : {a.data_source}\n\n"
        f"ℹ️ {a.reason}\n"
        "⚠️ Le score n'est pas une probabilité de gain."
    )


async def fetch_analysis():
    candles = await provider.candles(settings.symbol, settings.interval, settings.candles)
    return analyze(candles, settings.symbol, settings.interval)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    session_for(chat_id)
    await update.effective_message.reply_text(
        "🤖 SMA POCKETTRADER AI V1.1\n\n"
        "🟢 Données : marché réel via fournisseur externe\n"
        "🧪 Trading : PAPER/DEMO uniquement\n"
        "🔒 Exécution Pocket Option : verrouillée\n\n"
        "/analyze — analyse du marché\n"
        "/simulate — simulation basée sur le prix réel\n"
        "/status — état du moteur\n"
        "/stats — statistiques observées\n"
        "/resume — autoriser les simulations\n"
        "/pause — pause\n"
        "/stop — arrêt\n"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    session = session_for(chat_id)
    s = journal.stats(chat_id)
    await update.effective_message.reply_text(
        f"🤖 SMA V1.1\n"
        f"État : {'🟢 actif' if not session.risk.paused else '⏸ pause'}\n"
        f"Données : {'🟢 configurées' if provider.configured() else '🔴 API manquante'}\n"
        f"Marché : {settings.symbol} {settings.interval}\n"
        f"Capital papier : ${settings.capital:.2f}\n"
        f"Mise : ${session.risk.stake():.2f}\n"
        f"Ouvertes : {len(session.paper.list_open())}/{settings.max_open_paper_trades}\n"
        f"Trades clôturés : {s['trades']}\n"
        f"Win rate observé : {s['win_rate']}%\n"
        f"P&L papier : ${s['pnl']:.2f}\n"
        f"Live execution : 🔒 OFF"
    )


async def analyze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        a = await fetch_analysis()
    except MarketDataError as exc:
        return await update.effective_message.reply_text(f"⚠️ Données de marché indisponibles.\n{exc}")
    await update.effective_message.reply_text(fmt_analysis(a))


async def simulate_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    session = session_for(chat_id)
    try:
        a = await fetch_analysis()
    except MarketDataError as exc:
        return await update.effective_message.reply_text(f"⚠️ Impossible d'ouvrir une simulation.\n{exc}")
    if a.score < settings.min_signal_score or a.direction == "WAIT":
        return await update.effective_message.reply_text(
            f"⏸ Pas de simulation. Score={a.score}/100, direction={a.direction}.\n"
            "Le moteur attend une configuration suffisante."
        )
    exp = choose(a.score, a.volatility, settings.expiration_seconds)
    if exp <= 0:
        return await update.effective_message.reply_text("⏸ Aucune expiration candidate pour ce setup.")
    try:
        trade = await session.paper.open(a, exp, chat_id=chat_id)
    except RuntimeError as exc:
        return await update.effective_message.reply_text(f"🛑 {exc}")
    be = break_even_win_rate(trade.payout_percent)
    await update.effective_message.reply_text(
        f"🧪 PAPER TRADE OUVERT\n\n"
        f"{trade.direction} · {trade.symbol}\n"
        f"Entrée : {trade.entry}\nMise : ${trade.stake:.2f}\n"
        f"Payout configuré : {trade.payout_percent:.0f}%\n"
        f"Break-even théorique : {be:.2f}%\n"
        f"Expiration : {trade.expiration_seconds}s\n"
        f"Score : {trade.score}/100\n"
        f"ID : {trade.id}\n\n"
        "📡 Le résultat sera calculé à l'expiration avec un prix de marché récupéré."
    )


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    s = journal.stats(chat_id)
    await update.effective_message.reply_text(
        f"📊 STATISTIQUES OBSERVÉES\n\n"
        f"Trades clôturés : {s['trades']}\nWins : {s['wins']}\nLosses : {s['losses']}\n"
        f"Égalités : {s['ties']}\nWin rate observé : {s['win_rate']}%\n"
        f"P&L papier : ${s['pnl']:.2f}\n\n"
        "⚠️ Ces statistiques viennent de simulations basées sur des données de marché reçues; elles ne garantissent pas les résultats futurs."
    )


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_for(update.effective_chat.id).risk.paused = False
    await update.effective_message.reply_text("▶️ Simulations autorisées. Exécution réelle toujours verrouillée.")


async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_for(update.effective_chat.id).risk.paused = True
    await update.effective_message.reply_text("⏸ Simulations en pause.")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_for(update.effective_chat.id).risk.paused = True
    await update.effective_message.reply_text("⛔ Moteur arrêté. Aucune exécution réelle n'est possible en V1.1.")


async def evaluator_loop(app: Application):
    while True:
        try:
            for chat_id, session in list(sessions.items()):
                results = await session.paper.evaluate_due()
                for trade in results:
                    text = (
                        f"📌 SIMULATION CLÔTURÉE\n"
                        f"{trade.direction} {trade.symbol}\n"
                        f"Entrée : {trade.entry}\nSortie : {trade.exit_price}\n"
                        f"Résultat : {'🟢 WIN' if trade.result == 'WIN' else '🔴 LOSS' if trade.result == 'LOSS' else '⚪ TIE'}\n"
                        f"P&L : ${trade.pnl:.2f}\n"
                        f"ID : {trade.id}"
                    )
                    try:
                        await app.bot.send_message(chat_id=chat_id, text=text)
                    except Exception as exc:
                        print(f"Telegram notification error for {chat_id}: {exc}")
        except Exception as exc:
            print(f"Evaluator error: {exc}")
        await asyncio.sleep(max(5, settings.refresh_seconds))


async def post_init(application: Application):
    application.create_task(evaluator_loop(application))


def build_application():
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN manquant.")
    app = Application.builder().token(settings.telegram_bot_token).updater(None).post_init(post_init).build()
    for cmd, fn in [
        ("start", start), ("status", status), ("analyze", analyze_cmd), ("simulate", simulate_cmd),
        ("stats", stats_cmd), ("resume", resume), ("pause", pause), ("stop", stop)
    ]:
        app.add_handler(CommandHandler(cmd, fn))
    return app
