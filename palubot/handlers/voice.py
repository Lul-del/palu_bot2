from telegram import Update
from telegram.ext import ContextTypes

from palubot.services.voice_ai import get_last_voice_error, transcribe_audio_bytes


async def extract_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if not update.message:
        return None

    if update.message.text:
        return update.message.text.strip()

    voice = update.message.voice
    if not voice:
        return None

    tg_file = await context.bot.get_file(voice.file_id)
    data = await tg_file.download_as_bytearray()
    text = transcribe_audio_bytes(bytes(data), filename="voice.ogg")
    if not text and not context.user_data.get("stt_warned"):
        context.user_data["stt_warned"] = True
        err = get_last_voice_error() or "audio non compris"
        await update.message.reply_text(
            f"Je n'ai pas bien compris votre audio ({err}). "
            "Répétez lentement ou envoyez un texte court."
        )
    return text
