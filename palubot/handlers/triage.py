from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from palubot.config import (
    TRIAGE_AGE,
    TRIAGE_BREATHING,
    TRIAGE_CHILLS,
    TRIAGE_CONVULSIONS,
    TRIAGE_DURATION,
    TRIAGE_FEVER,
    TRIAGE_HEADACHE,
    TRIAGE_Q_AGE,
    TRIAGE_Q_BREATHING,
    TRIAGE_Q_CHILLS,
    TRIAGE_Q_CONVULSIONS,
    TRIAGE_Q_DURATION,
    TRIAGE_Q_FEVER,
    TRIAGE_Q_HEADACHE,
    TRIAGE_Q_VOMITING,
    TRIAGE_VOMITING,
    YES_NO_CHOICES,
)
from palubot.database.db import save_triage
from palubot.services.malaria_ai import compute_risk, triage_disclaimer
from palubot.services.responder import send_reply
from palubot.handlers.voice import extract_user_text


def _yes(text: str) -> bool:
    return text.strip().lower() == "oui"


def _guidance_by_risk(risk: str) -> str:
    if risk == "urgence médicale":
        return "Consigne: allez en urgence au centre de santé le plus proche ou appelez le SAMU."
    if risk == "risque modéré":
        return (
            "Consigne: consultez un professionnel de santé dans la journée pour une prise en charge adaptée. "
            "N'utilisez pas d'automédication sans avis médical, hydratez-vous et surveillez l'évolution des symptômes."
        )
    return "Consigne: surveillez les symptômes et consultez rapidement si aggravation."


async def triage_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["triage"] = {}
    await send_reply(update, context, TRIAGE_Q_FEVER, reply_markup=ReplyKeyboardMarkup(YES_NO_CHOICES, resize_keyboard=True))
    return TRIAGE_FEVER


async def triage_fever(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    context.user_data["triage"]["fever"] = _yes(text or "")
    await send_reply(update, context, TRIAGE_Q_HEADACHE, reply_markup=ReplyKeyboardMarkup(YES_NO_CHOICES, resize_keyboard=True))
    return TRIAGE_HEADACHE


async def triage_headache(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    context.user_data["triage"]["headache"] = _yes(text or "")
    await send_reply(update, context, TRIAGE_Q_CHILLS, reply_markup=ReplyKeyboardMarkup(YES_NO_CHOICES, resize_keyboard=True))
    return TRIAGE_CHILLS


async def triage_chills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    context.user_data["triage"]["chills"] = _yes(text or "")
    await send_reply(update, context, TRIAGE_Q_VOMITING, reply_markup=ReplyKeyboardMarkup(YES_NO_CHOICES, resize_keyboard=True))
    return TRIAGE_VOMITING


async def triage_vomiting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    context.user_data["triage"]["vomiting"] = _yes(text or "")
    await send_reply(update, context, TRIAGE_Q_CONVULSIONS, reply_markup=ReplyKeyboardMarkup(YES_NO_CHOICES, resize_keyboard=True))
    return TRIAGE_CONVULSIONS


async def triage_convulsions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    context.user_data["triage"]["convulsions"] = _yes(text or "")
    await send_reply(update, context, TRIAGE_Q_BREATHING, reply_markup=ReplyKeyboardMarkup(YES_NO_CHOICES, resize_keyboard=True))
    return TRIAGE_BREATHING


async def triage_breathing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    context.user_data["triage"]["breathing_difficulty"] = _yes(text or "")
    await send_reply(update, context, TRIAGE_Q_DURATION, reply_markup=ReplyKeyboardRemove())
    return TRIAGE_DURATION


async def triage_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    value = (text or "").strip()
    if not value.isdigit():
        await send_reply(update, context, "Réponse invalide. Entrez un nombre de jours (ex: 2).")
        return TRIAGE_DURATION

    context.user_data["triage"]["duration_days"] = int(value)
    await send_reply(update, context, TRIAGE_Q_AGE)
    return TRIAGE_AGE


async def triage_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = await extract_user_text(update, context)
    value = (text or "").strip()
    if not value.isdigit():
        await send_reply(update, context, "Réponse invalide. Entrez votre âge en nombre.")
        return TRIAGE_AGE

    answers = context.user_data.get("triage", {})
    answers["age"] = int(value)
    score, risk = compute_risk(answers)
    guidance = _guidance_by_risk(risk)

    user_id = update.effective_user.id if update.effective_user else 0
    save_triage(user_id, score, risk, str(answers))

    msg = (
        f"Résultat de la consultation:\n"
        f"- Niveau de risque: {risk}\n\n"
        f"{guidance}\n\n"
        f"{triage_disclaimer()}"
    )
    await send_reply(update, context, msg)
    return ConversationHandler.END


async def triage_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_reply(update, context, "Consultation annulée.")
    return ConversationHandler.END
