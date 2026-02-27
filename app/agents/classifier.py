from transformers import pipeline

# Load a pre-trained text classification model
classifier_pipeline = pipeline(
    "text-classification", model="distilbert-base-uncased-finetuned-sst-2-english"
)


def classify_scam(text: str):
    """
    Uses Hugging Face model to classify sentiment,
    then maps it to scam categories (basic mapping for demo).
    """

    result = classifier_pipeline(text)[0]
    label = result["label"]
    score = result["score"]

    text_lower = text.lower()

    # Simple mapping logic on top of AI output
    if "kyc" in text_lower or "account" in text_lower:
        return "KYC Phishing"
    if "lottery" in text_lower or "won" in text_lower:
        return "Lottery Scam"
    if "job" in text_lower or "hiring" in text_lower:
        return "Job Scam"
    if "loan" in text_lower or "credit" in text_lower:
        return "Loan Scam"

    # Fallback based on model sentiment
    if label == "NEGATIVE" and score > 0.8:
        return "Phishing / Scam (AI Detected)"

    return "Unknown"
