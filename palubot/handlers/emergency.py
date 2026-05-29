from telegram import Update
from telegram.ext import ContextTypes

from palubot.services.responder import send_reply


def emergency_text(samu_number: str) -> str:
    return (
        "Urgence médicale. "
        f"SAMU: {samu_number}. "
        "Rendez-vous au centre de santé le plus proche si possible. "
        "En cas de convulsions, inconscience ou détresse respiratoire: appel immédiat."
    )


async def show_emergency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    samu_number = context.bot_data.get("samu_number", "166")
    await send_reply(update, context, emergency_text(samu_number))
