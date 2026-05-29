import asyncio
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update

from palubot.bot import build_application
from palubot.config import load_settings

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

settings = load_settings()
app_tg = build_application(settings.bot_token, settings.samu_number)

# Application FastAPI (serveur HTTP pour Render)
app = FastAPI()


@app.on_event("startup")
async def startup():
    """Initialise le bot et enregistre le webhook au démarrage."""
    await app_tg.initialize()
    await app_tg.start()

    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await app_tg.bot.set_webhook(
            url=f"{webhook_url}/webhook",
            drop_pending_updates=True,
        )
        logger.info(f"Webhook enregistré : {webhook_url}/webhook")
    else:
        logger.warning("WEBHOOK_URL non défini — webhook non enregistré")

    logger.info("PaluBot démarré 🚀")


@app.on_event("shutdown")
async def shutdown():
    """Arrêt propre du bot."""
    await app_tg.updater.stop() if app_tg.updater else None
    await app_tg.stop()
    await app_tg.shutdown()
    logger.info("PaluBot arrêté.")


@app.post("/webhook")
async def webhook(request: Request):
    """Reçoit les mises à jour Telegram via webhook."""
    data = await request.json()
    update = Update.de_json(data, app_tg.bot)
    await app_tg.process_update(update)
    return {"ok": True}


@app.get("/")
async def health():
    """Health check pour Render."""
    return {"status": "PaluBot en ligne 🚀"}
