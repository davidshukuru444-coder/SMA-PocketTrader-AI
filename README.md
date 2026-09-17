# SMA PocketTrader AI V1.1 — LIVE MARKET / PAPER TRADING

V1.1 remplace les bougies synthétiques de V1 par des données de marché récupérées via Twelve Data.

## Important

- Les données de marché sont réelles/fournies par un fournisseur externe.
- Les opérations sont **PAPER/DEMO uniquement**.
- Aucun ordre Pocket Option n'est envoyé.
- `live_execution_enabled = False` est un verrou de sécurité.
- Le score 0–100 n'est pas une probabilité de gain.
- Le win rate est calculé uniquement à partir de simulations clôturées.

Twelve Data documente un endpoint `/time_series` pour les séries OHLC et prend en charge notamment `EUR/USD` et l'intervalle `1min`.

## Architecture

Telegram → FastAPI/Cloud → Market Data → Analyzer → Risk Manager → Paper Engine → Journal/Stats

## Variables Render

Configurer dans Render :

- `TELEGRAM_BOT_TOKEN`
- `PUBLIC_BASE_URL` (URL HTTPS du service Render)
- `TELEGRAM_WEBHOOK_SECRET`
- `TWELVE_DATA_API_KEY`

Ne jamais mettre ces secrets dans GitHub.

## Test local

```bash
python -m compileall .
python -c "from app import app; print(app.title, app.version)"
```

## Déploiement Render

Build:

```text
pip install -r requirements.txt
```

Start:

```text
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Health:

```text
/health
```

## Telegram

Après déploiement, le serveur configure le webhook vers :

```text
PUBLIC_BASE_URL/telegram/webhook
```

Commandes : `/start`, `/analyze`, `/simulate`, `/status`, `/stats`, `/resume`, `/pause`, `/stop`.

## Limite importante sur Pocket Option / OTC

V1.1 n'essaie pas de se connecter directement à Pocket Option ni de contourner ses mécanismes. Les données Twelve Data peuvent différer des cotations/payouts de la plateforme. Les signaux doivent donc être considérés comme un environnement de recherche/paper trading, pas comme une promesse de résultat sur Pocket Option.


## Notification Fix
V1.1 used a manual `initialize()`/`start()` lifecycle for python-telegram-bot.
With that lifecycle, `post_init` is not automatically invoked. The paper-trade
evaluator therefore did not start, so expired simulations could remain open
without sending a Telegram result notification.

This fixed package starts `evaluator_loop()` explicitly during FastAPI startup,
cancels it cleanly during shutdown, and logs market-data evaluation errors
instead of silently ignoring them.
