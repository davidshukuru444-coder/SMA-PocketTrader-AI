import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application,CommandHandler,ContextTypes
from config import Settings
from market_data import synthetic_candles
from market_analyzer import analyze
from payout import break_even_win_rate
from risk_manager import RiskManager
from simulator import simulate
from expiration import choose
from journal import log,stats
settings=Settings(); risk=RiskManager(settings)
async def start(u,c): await u.message.reply_text('🤖 SMA PocketTrader AI V1\n🧪 MODE SIMULATION\n\n/analyze = analyser\n/simulate = simuler\n/status = statut\n/stats = statistiques\n/resume = démarrer\n/pause = pause\n/stop = arrêt')
async def status(u,c): await u.message.reply_text(f'Robot: {"🟢 actif" if not risk.paused else "⏸ pause"}\nCapital: ${settings.capital:.2f}\nRisque/trade: {settings.risk_percent}%\nMise: ${risk.stake():.2f}\nTrades: {risk.trades}/{settings.max_trades_per_day}\nP&L: ${risk.pnl:.2f}\nPertes consécutives: {risk.loss_streak}')
async def resume(u,c): risk.paused=False; await u.message.reply_text('▶️ Robot activé — simulation uniquement.')
async def pause(u,c): risk.paused=True; await u.message.reply_text('⏸ Robot en pause.')
async def stop(u,c): risk.paused=True; await u.message.reply_text('⛔ Robot arrêté.')
async def analyze_cmd(u,c):
    a=analyze(synthetic_candles()); be=break_even_win_rate(settings.payout_percent); exp=choose(a['score'],a['volatility'])
    await u.message.reply_text(f"🔎 EUR/USD OTC — {settings.timeframe}\n\nDirection: {a['direction']}\nScore: {a['score']}/100\nTendance: {a['trend']}/20\nStructure: {a['structure']}/15\nS/R: {a['support_resistance']}/15\nPrice Action: {a['price_action']}/15\nMomentum: {a['momentum']}/10\nVolatilité: {a['volatility']}/10\nLiquidité/SMC: {a['liquidity_smc']}/10\nContexte: {a['context']}/5\n\nPayout: {settings.payout_percent}%\nBreak-even théorique: {be:.2f}%\nExpiration candidate: {exp}s\n\nℹ️ {a['reason']}\n⚠️ Score ≠ probabilité prouvée.")
async def simulate_cmd(u,c):
    ok,msg=risk.can_trade()
    if not ok:return await u.message.reply_text('🛑 '+msg)
    a=analyze(synthetic_candles()); direction=a['direction']
    if direction=='WAIT':return await u.message.reply_text('⚪ WAIT — aucun trade simulé.')
    estimated=max(50,min(90,a['score']-5)); result,pnl=simulate(direction,risk.stake(),settings.payout_percent,estimated); risk.register(pnl)
    log({'time':datetime.now().isoformat(timespec='seconds'),'symbol':'EUR/USD OTC','direction':direction,'stake':risk.stake(),'expiration_seconds':choose(a['score'],a['volatility']),'score':a['score'],'payout_percent':settings.payout_percent,'result':result,'pnl':pnl})
    await u.message.reply_text(f'🧪 SIMULATION\n{direction} — mise ${risk.stake():.2f}\nScore {a["score"]}/100\nRésultat: {result}\nP&L: ${pnl:.2f}')
async def stats_cmd(u,c):
    s=stats(); await u.message.reply_text(f"📊 Trades: {s['trades']}\nWins: {s['wins']}\nLosses: {s['losses']}\nWin rate observé: {s['win_rate']}%\nP&L simulé: ${s['pnl']:.2f}")
def run():
    token=os.getenv('TELEGRAM_BOT_TOKEN')
    if not token: raise RuntimeError('TELEGRAM_BOT_TOKEN manquant dans .env')
    app=Application.builder().token(token).build()
    for cmd,fn in [('start',start),('status',status),('analyze',analyze_cmd),('simulate',simulate_cmd),('stats',stats_cmd),('resume',resume),('pause',pause),('stop',stop)]: app.add_handler(CommandHandler(cmd,fn))
    app.run_polling()
