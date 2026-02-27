def calculate_risk_score(entities: dict, scam_type: str):
    score = 0

    if entities.get("urls"):
        score += 40

    if entities.get("phone_numbers"):
        score += 20

    score += len(entities.get("keywords", [])) * 5

    if scam_type == "KYC Phishing":
        score += 25
    elif scam_type == "Lottery Scam":
        score += 20
    elif scam_type == "Loan Scam":
        score += 15

    return min(score, 100)
