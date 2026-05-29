from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from palubot.config import MAIN_MENU
from palubot.database.db import upsert_user
from palubot.services.responder import send_reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user:
        upsert_user(user.id, user.first_name or "utilisateur")

    text = (
        "Bienvenue sur PaluBot. "
        "Choisissez une option du menu principal pour continuer."
    )
    await send_reply(
        update,
        context,
        text,
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True, is_persistent=True),
    )
