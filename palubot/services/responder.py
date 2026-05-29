from io import BytesIO

from telegram import InputFile, Update
from telegram.ext import ContextTypes

from palubot.services.voice_ai import get_last_voice_error, has_voice_ai, synthesize_voice_bytes


async def send_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
) -> None:
    if not update.message:
        return

    mode = context.user_data.get("mode", "text")
    if mode == "voice":
        voice_data = synthesize_voice_bytes(text)
        if voice_data:
            try:
                voice_file = InputFile(BytesIO(voice_data), filename="reply.ogg")
                await update.message.reply_voice(voice=voice_file, reply_markup=reply_markup)
                return
            except Exception:
                try:
                    # Fallback: send playable audio if Telegram rejects voice container.
                    audio_file = InputFile(BytesIO(voice_data), filename="reply.ogg")
                    await update.message.reply_audio(audio=audio_file, reply_markup=reply_markup)
                    return
                except Exception:
                    if not context.user_data.get("voice_send_warned"):
                        context.user_data["voice_send_warned"] = True
                        err = get_last_voice_error() or "Erreur inconnue."
                        await update.message.reply_text(
                            "Le mode vocal est actif, mais l'envoi audio a échoué. "
                            f"Détail: {err}"
                        )
        elif has_voice_ai() and not context.user_data.get("voice_gen_warned"):
            context.user_data["voice_gen_warned"] = True
            err = get_last_voice_error() or "Erreur inconnue."
            await update.message.reply_text(
                "Le mode vocal est actif, mais la génération de voix a échoué. "
                f"Détail: {err}"
            )
        elif not has_voice_ai() and not context.user_data.get("voice_setup_warned"):
            context.user_data["voice_setup_warned"] = True
            await update.message.reply_text(
                "Le mode vocal est actif, mais le moteur vocal n'est pas disponible. "
                "J'envoie donc du texte en attendant."
            )

    await update.message.reply_text(text, reply_markup=reply_markup)
