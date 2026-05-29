from telegram import Update
from telegram.ext import ContextTypes

from palubot.services.responder import send_reply

FAQ = {
    "qu’est-ce que le paludisme ?": "Le paludisme est une maladie parasitaire transmise par les moustiques anopheles.",
    "symptômes ?": "Fièvre, frissons, maux de tête, fatigue, nausées ou vomissements.",
    "prévention ?": "Dormir sous moustiquaire imprégnée, éliminer les eaux stagnantes et consulter rapidement en cas de fièvre.",
    "traitements ?": "Le traitement dépend du protocole local et d'un avis médical. Consultez un professionnel de santé.",
    "quand consulter ?": "Consultez vite si fièvre persistante, vomissements, confusion, convulsions ou détresse respiratoire.",
}


async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lines = ["Mini FAQ Paludisme:"] + [f"- {k}" for k in FAQ.keys()]
    lines.append("Envoyez exactement une question ci-dessus pour recevoir la réponse.")
    await send_reply(update, context, "\n".join(lines))


async def handle_faq(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str | None = None) -> bool:
    incoming = (text or update.message.text or "").strip().lower()
    if incoming in FAQ:
        await send_reply(update, context, FAQ[incoming])
        return True
    return False
