import os
import tempfile
from typing import Optional

from faster_whisper import WhisperModel
from gtts import gTTS

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
TTS_LANG = os.getenv("TTS_LANG", "fr")
LAST_VOICE_ERROR: str | None = None
_WHISPER_MODEL: WhisperModel | None = None


def _get_whisper_model() -> WhisperModel:
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        _WHISPER_MODEL = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
    return _WHISPER_MODEL


def has_voice_ai() -> bool:
    return True


def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.ogg") -> Optional[str]:
    global LAST_VOICE_ERROR
    suffix = ".ogg"
    if "." in filename:
        suffix = "." + filename.rsplit(".", 1)[-1].lower()

    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()

            model = _get_whisper_model()
            segments, _info = model.transcribe(tmp.name, language="fr")
            text = " ".join(seg.text.strip() for seg in segments).strip()

        if not text:
            LAST_VOICE_ERROR = "Transcription vide."
            return None

        LAST_VOICE_ERROR = None
        return text
    except Exception as exc:
        LAST_VOICE_ERROR = f"Transcription échouée: {exc}"
        return None


def synthesize_voice_bytes(text: str) -> Optional[bytes]:
    global LAST_VOICE_ERROR
    try:
        tts = gTTS(text=text, lang=TTS_LANG)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as tmp:
            tts.save(tmp.name)
            tmp.seek(0)
            data = tmp.read()

        LAST_VOICE_ERROR = None
        return data
    except Exception as exc:
        LAST_VOICE_ERROR = f"Synthèse échouée: {exc}"
        return None


def get_last_voice_error() -> str | None:
    return LAST_VOICE_ERROR
