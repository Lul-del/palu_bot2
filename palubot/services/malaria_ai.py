def compute_risk(answers: dict) -> tuple[int, str]:
    score = 0

    if answers.get("fever"):
        score += 3
    if answers.get("headache"):
        score += 2
    if answers.get("chills"):
        score += 2
    if answers.get("vomiting"):
        score += 2
    if answers.get("convulsions"):
        score += 4
    if answers.get("breathing_difficulty"):
        score += 4

    days = int(answers.get("duration_days", 0))
    age = int(answers.get("age", 0))

    if days >= 3:
        score += 1
    if age < 5 or age >= 60:
        score += 2

    if score >= 10:
        risk = "urgence médicale"
    elif score >= 6:
        risk = "risque modéré"
    else:
        risk = "faible risque"

    return score, risk


def triage_disclaimer() -> str:
    return "Ce triage est indicatif et ne remplace pas une consultation médicale."
