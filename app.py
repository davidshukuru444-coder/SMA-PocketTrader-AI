import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request

from config import settings
from telegram import Update
from telegram_bot import build_application


ptb_app = build_application()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ptb_app.initialize()
    await ptb_app.start()
    if not settings.public_base_url:
        print("WARNING: PUBLIC_BASE_URL is missing; Telegram webhook cannot be registered.")
    else:
        webhook_url = f"{settings.public_base_url}/telegram/webhook"
        kwargs = {"url": webhook_url, "allowed_updates": Update.ALL_TYPES}
        if settings.webhook_secret:
            kwargs["secret_token"] = settings.webhook_secret
        await ptb_app.bot.set_webhook(**kwargs)
        print(f"Telegram webhook configured: {webhook_url}")
    yield
    await ptb_app.stop()
    await ptb_app.shutdown()


app = FastAPI(title="SMA PocketTrader AI", version="1.1.0", lifespan=lifespan)


@app.get("/")
async def root():
    return {"name": "SMA PocketTrader AI", "version": "1.1.0", "mode": "paper", "live_execution": False}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.1.0",
        "telegram_configured": bool(settings.telegram_bot_token),
        "market_data_configured": bool(settings.market_data_api_key),
        "live_execution": False,
    }


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if settings.webhook_secret:
        received = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if received != settings.webhook_secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
    data = await request.json()
    update = Update.de_json(data=data, bot=ptb_app.bot)
    await ptb_app.update_queue.put(update)
    return {"ok": True}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
