import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("data/scam_logs.json")


def log_scam(message, scam_type, risk_score, entities):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "scam_type": scam_type,
        "risk_score": risk_score,
        "entities": entities,
    }
           
    # Ensure folder exists and handle file read/write safely        
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        if LOG_FILE.exists():
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(entry)

        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print("Logging failed:", e)
