from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from palubot.config import MAIN_MENU, MODE_MENU
from palubot.services.responder import send_reply
from palubot.services.voice_ai import has_voice_ai


async def show_mode_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Bienvenue. Choisissez votre mode:",
        reply_markup=ReplyKeyboardMarkup(MODE_MENU, resize_keyboard=True, is_persistent=True),
    )


async def activate_text_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = "text"
    await update.message.reply_text(
        "Mode message activé.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True, is_persistent=True),
    )


async def activate_voice_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = "voice"
    if not has_voice_ai():
        await update.message.reply_text(
            "Attention: le moteur vocal n'est pas disponible pour le moment. "
            "Le bot restera en texte jusqu'à correction."
        )
    await send_reply(
        update,
        context,
        "Bonjour, je suis PaluBot. Nous sommes en mode vocal. Dites ou écrivez votre besoin: Consultation, Centres de santé, Mes rappels, Informations, ou Urgence.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True, is_persistent=True),
    )
