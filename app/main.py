from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.extractor import extract_entities
from app.agents.classifier import classify_scam
from app.agents.risk_agent import calculate_risk_score
from app.agents.logger import log_scam
from app.agents.advice import generate_advice

app = FastAPI()


class ScamRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "Agentic Honey-Pot API is running"}


@app.post("/analyze-scam")
def analyze_scam(request: ScamRequest):
    entities = extract_entities(request.message)
    scam_type = classify_scam(request.message)
    risk_score = calculate_risk_score(entities, scam_type)
    advice_data = generate_advice(risk_score)

    # Honeypot logging
    log_scam(request.message, scam_type, risk_score, entities)

    return {
        "received_message": request.message,
        "scam_type": scam_type,
        "risk_score": risk_score,
        "confidence": advice_data["confidence"],
        "advice": advice_data["advice"],
        "extracted_entities": entities,
    }
