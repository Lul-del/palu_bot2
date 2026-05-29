import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    bot_token: str
    samu_number: str = "166"


MENU_TRIAGE = "🩺 Consultation"
MENU_CENTERS = "🏥 Centres de santé"
MENU_REMINDERS = "⏰ Mes rappels"
MENU_INFO = "ℹ️ Informations"
MENU_EMERGENCY = "📞 Urgence"

MAIN_MENU = [
    [MENU_TRIAGE, MENU_CENTERS],
    [MENU_REMINDERS, MENU_INFO],
    [MENU_EMERGENCY],
]

MODE_TEXT = "Continuer par message"
MODE_VOICE = "Continuer par vocal"
MODE_MENU = [[MODE_TEXT], [MODE_VOICE]]

REMINDER_NEW = "➕ Nouveau rappel"
REMINDER_LIST = "📋 Lister mes rappels"
REMINDER_BACK = "⬅️ Retour menu"
REMINDER_MENU = [
    [REMINDER_NEW, REMINDER_LIST],
    [REMINDER_BACK],
]

TRIAGE_Q_FEVER = "Avez-vous de la fièvre ?"
TRIAGE_Q_HEADACHE = "Avez-vous des maux de tête ?"
TRIAGE_Q_CHILLS = "Avez-vous des frissons ?"
TRIAGE_Q_VOMITING = "Avez-vous des vomissements ?"
TRIAGE_Q_CONVULSIONS = "Avez-vous fait des convulsions ?"
TRIAGE_Q_BREATHING = "Avez-vous des difficultés à respirer ?"
TRIAGE_Q_DURATION = "Depuis combien de jours avez-vous ces symptômes ? (nombre)"
TRIAGE_Q_AGE = "Quel est votre âge ?"

YES_NO_CHOICES = [["Oui", "Non"]]

TRIAGE_FEVER, TRIAGE_HEADACHE, TRIAGE_CHILLS, TRIAGE_VOMITING, TRIAGE_CONVULSIONS, TRIAGE_BREATHING, TRIAGE_DURATION, TRIAGE_AGE = range(8)
REMINDER_TIME, REMINDER_TEXT = range(2)


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN manquant. Crée un fichier .env à partir de .env.example")

    samu = os.getenv("SAMU_NUMBER", "166")
    return Settings(bot_token=token, samu_number=samu)
