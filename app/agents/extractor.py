import re


def extract_entities(text: str):
    # Phone numbers (10 digits)
    phone_pattern = r"\b\d{10}\b"
    phones = re.findall(phone_pattern, text)

    # URLs
    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, text)

    # Email addresses
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)

    # UPI IDs (basic pattern)
    upi_pattern = r"\b[\w.\-]{2,}@[a-zA-Z]{2,}\b"
    upis = re.findall(upi_pattern, text)

    # Bank names (simple keyword match)
    bank_keywords = [
        "sbi",
        "hdfc",
        "icici",
        "axis",
        "kotak",
        "pnb",
        "bank of india",
        "canara",
        "union bank",
    ]

    found_banks = []
    text_lower = text.lower()
    for bank in bank_keywords:
        if bank in text_lower:
            found_banks.append(bank)

    # Scam-related keywords
    keywords_list = [
        "urgent",
        "blocked",
        "kyc",
        "lottery",
        "prize",
        "account",
        "verify",
        "click",
        "winner",
    ]

    found_keywords = []
    for word in keywords_list:
        if word in text_lower:
            found_keywords.append(word)

    return {
        "phone_numbers": phones,
        "urls": urls,
        "emails": emails,
        "upi_ids": upis,
        "banks": found_banks,
        "keywords": found_keywords,
    }
