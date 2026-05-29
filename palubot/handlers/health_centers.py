from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from palubot.services.geolocation import find_nearest_centers
from palubot.services.responder import send_reply


async def ask_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    kb = [[KeyboardButton("📍 Envoyer ma position", request_location=True)]]
    await send_reply(
        update,
        context,
        "Partage ta position pour trouver les centres de santé proches.",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True),
    )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    loc = update.message.location if update.message else None
    if not loc:
        return

    centers = find_nearest_centers(loc.latitude, loc.longitude)
    lines = ["Centres proches:"]
    for c in centers:
        lines.append(f"- {c['name']} | {c['distance_km']} km | {c['phone']}")

    await send_reply(update, context, "\n".join(lines))
