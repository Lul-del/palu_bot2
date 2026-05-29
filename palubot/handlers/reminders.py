from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from palubot.config import MAIN_MENU, REMINDER_MENU, REMINDER_TEXT, REMINDER_TIME
from palubot.handlers.voice import extract_user_text
from palubot.database.db import add_reminder, list_active_reminders
from palubot.services.responder import send_reply
from palubot.services.scheduler import parse_time_hhmm


async def _send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=f"⏰ Il est temps de prendre votre traitement antipaludique.\n{job.data}",
    )


async def reminder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_reply(
        update,
        context,
        "Gestion des rappels: créez un nouveau rappel ou listez vos rappels.",
        reply_markup=ReplyKeyboardMarkup(REMINDER_MENU, resize_keyboard=True),
    )


async def reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_reply(
        update,
        context,
        "Entrez l'heure du rappel au format HH:MM (ex: 08:30).",
        reply_markup=ReplyKeyboardRemove(),
    )
    return REMINDER_TIME


async def reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    raw = (text or "").strip()
    parsed = parse_time_hhmm(raw)
    if parsed is None:
        await send_reply(update, context, "Format invalide. Utilisez HH:MM (ex: 21:45).")
        return REMINDER_TIME

    context.user_data["reminder_time"] = raw
    context.user_data["reminder_time_obj"] = parsed
    await send_reply(update, context, "Entrez le texte du rappel (ex: Prendre ACT après repas).")
    return REMINDER_TEXT


async def reminder_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    txt = (text or "").strip()
    user_id = update.effective_user.id if update.effective_user else 0
    chat_id = update.effective_chat.id if update.effective_chat else None

    reminder_id = add_reminder(user_id, context.user_data["reminder_time"], txt)
    t = context.user_data["reminder_time_obj"]
    context.job_queue.run_daily(_send_reminder, t, chat_id=chat_id, name=f"reminder_{user_id}_{reminder_id}", data=txt)

    await send_reply(
        update,
        context,
        f"Rappel enregistré pour {context.user_data['reminder_time']}.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True, is_persistent=True),
    )
    return ConversationHandler.END


async def reminder_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id if update.effective_user else 0
    rows = list(list_active_reminders(user_id))
    if not rows:
        await send_reply(update, context, "Aucun rappel actif.")
        return

    lines = ["Vos rappels actifs:"]
    for r in rows:
        lines.append(f"- #{r['id']} à {r['reminder_time']}: {r['text']}")
    await send_reply(update, context, "\n".join(lines))


async def reminder_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_reply(
        update,
        context,
        "Création de rappel annulée.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True, is_persistent=True),
    )
    return ConversationHandler.END
