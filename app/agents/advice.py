def generate_advice(risk_score: int):
    if risk_score <= 30:
        return {
            "confidence": "Low",
            "advice": "Message appears mostly safe, but stay cautious.",
        }

    if risk_score <= 70:
        return {
            "confidence": "Medium",
            "advice": "Do not click links or share personal details.",
        }

    return {
        "confidence": "High",
        "advice": "Likely scam! Do not respond, block sender, and report immediately.",
    }
