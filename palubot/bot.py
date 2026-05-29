from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from palubot.config import (
    MENU_CENTERS,
    MENU_EMERGENCY,
    MENU_INFO,
    MENU_REMINDERS,
    MENU_TRIAGE,
    MODE_TEXT,
    MODE_VOICE,
    REMINDER_BACK,
    REMINDER_LIST,
    REMINDER_NEW,
    REMINDER_TEXT,
    REMINDER_TIME,
    TRIAGE_AGE,
    TRIAGE_BREATHING,
    TRIAGE_CHILLS,
    TRIAGE_CONVULSIONS,
    TRIAGE_DURATION,
    TRIAGE_FEVER,
    TRIAGE_HEADACHE,
    TRIAGE_VOMITING,
)
from palubot.database.db import init_db
from palubot.handlers.emergency import show_emergency
from palubot.handlers.health_centers import ask_location, handle_location
from palubot.handlers.info import handle_faq, show_info
from palubot.handlers.mode import activate_text_mode, activate_voice_mode, show_mode_choice
from palubot.handlers.reminders import (
    reminder_cancel,
    reminder_list,
    reminder_menu,
    reminder_start,
    reminder_text,
    reminder_time,
)
from palubot.handlers.start import start
from palubot.handlers.triage import (
    triage_age,
    triage_breathing,
    triage_cancel,
    triage_chills,
    triage_convulsions,
    triage_duration,
    triage_fever,
    triage_headache,
    triage_start,
    triage_vomiting,
)
from palubot.handlers.voice import extract_user_text
from palubot.services.responder import send_reply


async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = await extract_user_text(update, context)
    if not text:
        return

    lowered = text.lower().strip()

    if lowered == "allo":
        await show_mode_choice(update, context)
        return

    if text == MODE_TEXT:
        await activate_text_mode(update, context)
        return

    if text == MODE_VOICE:
        await activate_voice_mode(update, context)
        return

    if await handle_faq(update, context, text=text):
        return

    if text == MENU_TRIAGE or "consult" in lowered:
        await triage_start(update, context)
    elif text == MENU_CENTERS or "centre" in lowered or "santé" in lowered:
        await ask_location(update, context)
    elif text == MENU_REMINDERS or "rappel" in lowered:
        await reminder_menu(update, context)
    elif text == REMINDER_LIST:
        await reminder_list(update, context)
    elif text == REMINDER_BACK:
        await start(update, context)
    elif text == MENU_INFO or "info" in lowered or "paludisme" in lowered:
        await show_info(update, context)
    elif text == MENU_EMERGENCY or "urgence" in lowered or "samu" in lowered:
        await show_emergency(update, context)
    else:
        await send_reply(
            update,
            context,
            "Je n'ai pas compris. Dites: Consultation, Centres de santé, Mes rappels, Informations ou Urgence. "
            "Vous pouvez aussi envoyer Allo pour recommencer.",
        )


async def restart_from_allo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await show_mode_choice(update, context)
    return ConversationHandler.END


async def voice_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = "voice"
    await send_reply(update, context, "Test vocal PaluBot. Si tu m'entends, la voix fonctionne.")


def build_application(token: str, samu_number: str = "166") -> Application:
    init_db()
    app = Application.builder().token(token).build()
    app.bot_data["samu_number"] = samu_number

    triage_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f"^{MENU_TRIAGE}$"), triage_start)],
        states={
            TRIAGE_FEVER: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, triage_fever)],
            TRIAGE_HEADACHE: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, triage_headache)],
            TRIAGE_CHILLS: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, triage_chills)],
            TRIAGE_VOMITING: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, triage_vomiting)],
            TRIAGE_CONVULSIONS: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, triage_convulsions)],
            TRIAGE_BREATHING: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, triage_breathing)],
            TRIAGE_DURATION: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, triage_duration)],
            TRIAGE_AGE: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, triage_age)],
        },
        fallbacks=[
            CommandHandler("annuler", triage_cancel),
            MessageHandler(filters.Regex(r"(?i)^allo$"), restart_from_allo),
        ],
    )

    reminder_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f"^{REMINDER_NEW}$"), reminder_start), CommandHandler("rappel_nouveau", reminder_start)],
        states={
            REMINDER_TIME: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, reminder_time)],
            REMINDER_TEXT: [MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, reminder_text)],
        },
        fallbacks=[
            CommandHandler("annuler", reminder_cancel),
            MessageHandler(filters.Regex(r"(?i)^allo$"), restart_from_allo),
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("voicetest", voice_test))
    app.add_handler(CommandHandler("rappel_liste", reminder_list))
    app.add_handler(triage_conv)
    app.add_handler(reminder_conv)
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler((filters.TEXT | filters.VOICE) & ~filters.COMMAND, menu_router))

    return app
