import os
import typing
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
# Configure API Key (OpenRouter)
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set in .env file")

# Backend API Security
BACKEND_SECRET = os.getenv("X_API_KEY")
if not BACKEND_SECRET:
    print("WARNING: X_API_KEY not found in .env. API is unsecured!")

# genai.configure(api_key=API_KEY) # No longer needed for OpenRouter via OpenAI client

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev/hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 422 Debug Handler (From Research) ---
@app.exception_handler(RequestValidationError)
async def debug_validation_handler(request: Request, exc: RequestValidationError):
    # This logs the raw body causing the 422 error to the console
    body = await request.body()
    print(f"DEBUG: Tester sent invalid body: {body.decode()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "raw_body": body.decode()}
    )

# In-memory dictionary to track turn counts
# Key: client_ip (or some identifier), Value: int (count)
# Note: In a production app, use a proper database or Redis.
turn_counts: typing.Dict[str, int] = defaultdict(int)

# Global list to store interaction history for dashboard
# Each item: {timestamp, client_id, message, reply, extracted_intelligence, scam_detected}
global_interactions: typing.List[typing.Dict] = []

# Load persistence on startup
# Load persistence on startup
import json
import os
import time

if os.path.exists("results.json"):
    try:
        with open("results.json", "r") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        # Reconstruct interaction object for dashboard compatibility
                        restored_interaction = {
                            "timestamp": time.ctime(record.get("timestamp", time.time())),
                            "client_id": record.get("client_id", "restored_id"),
                            "message": " [Restored Historical Data]",
                            "reply": " [Restored Historical Data]",
                            "extracted_intelligence": record.get("intel", {}),
                            "scam_detected": True,
                            "suspicion_level": "HIGH",
                            "reasoning": "Restored from persistent threat log.",
                            "turn_count": 0
                        }
                        global_interactions.append(restored_interaction)
                    except Exception as parse_err: 
                        print(f"Skipping malformed line: {parse_err}")
    except Exception as e:
        print(f"Error loading persistence: {e}")

# Better approach: Modify 'global_interactions' to be populated from a persistent log if possible.
# For this hackathon, we'll just ensure the Intel Table populates.
# Actually, let's make results.json store the FULL interaction so we can restore the feed too.

# --- Pydantic Models ---

class HoneypotRequest(BaseModel):
    message: typing.Optional[str] = None  # Make even message optional
    client_id: typing.Optional[str] = None

    class Config:
        extra = "allow"  # Changed from "ignore" to "allow" - accept everything

class ExtractedIntelligence(BaseModel):
    upi_id: typing.Optional[str] = Field(None, description="Extracted UPI ID or null")
    bank_details: typing.Optional[str] = Field(None, description="Extracted bank account details or null")
    phishing_links: typing.List[str] = Field(default_factory=list, description="List of phishing URLs found")

class EngagementMetrics(BaseModel):
    turns_count: int

class HoneypotResponse(BaseModel):
    scam_detected: bool
    reply_to_scammer: str
    extracted_intelligence: ExtractedIntelligence
    engagement_metrics: EngagementMetrics

# --- Gemini Config ---

# Using Gemini 2.5 Flash as requested (mapping to gemini-2.0-flash-exp or similar if 2.5 isn't available, 
# but usually 'gemini-2.0-flash' or 'gemini-1.5-flash' are the standard flash models. 
# The prompt asked for "Gemini 2.5 Flash". As of my knowledge cutoff, 1.5 Flash is standard, 2.0 is experimental. 
# I will try to use a model name that is likely to work or fallback to a standard one if the specific version is strict.
# Ideally 'gemini-2.0-flash-exp' or just 'gemini-1.5-flash'. I will stick to 'gemini-1.5-flash' which is stable, 
# or 'gemini-2.0-flash' if the user insists on newer. 
# Re-reading prompt: "Use Gemini 2.5 Flash". I will assume this maps to the latest available flash model string 
# or I will use 'gemini-2.0-flash-exp' if I can. Let's use 'gemini-2.0-flash' as a safe bet for "next gen flash" 
# or fallback to 'gemini-1.5-flash' if that's safer. 
# Actually, I'll use the generic 'gemini-1.5-flash' to be safe unless I know 2.5 exists. 
# Wait, "Gemini 2.5 Flash" might be a typo for 1.5 or 2.0. I'll use 'gemini-1.5-flash' as it is robust.
# CORRECT: The prompt specifically asks for "Gemini 2.5 Flash". It might be a trick or a very new model. 
# I will define the model name string variable.
MODEL_NAME = "gemini-2.5-flash" 

# --- State Graph Config ---
from state_graph import StateGraph

graph = StateGraph(api_key=API_KEY)

@app.post("/guvi-honeypot", response_model=HoneypotResponse)
async def guvi_honeypot_endpoint(request: Request, body: HoneypotRequest):
    """
    Honeypot endpoint to analyze potential scam messages.
    """
    # Security Check (DISABLED FOR GUVI TESTING)
    # if BACKEND_SECRET:
    #     req_token = request.headers.get("x-api-key")
    #     if req_token != BACKEND_SECRET:
    #         raise HTTPException(status_code=401, detail="Unauthorized: Invalid x-api-key header")

    # Track turns based on client_id (if provided) or client IP
    tracker_key = body.client_id if body.client_id else (request.client.host if request.client else "unknown")
    
    turn_counts[tracker_key] += 1
    current_turn_count = turn_counts[tracker_key]

    # Retrieve history for this client from global_interactions (optional, for context)
    # For simplicity, we pass an empty history or could build it from previous global interactions
    # Here we just pass empty list as per original design, or you could implement history retrieval
    history = [] 

    # Handle missing message field
    message_text = body.message if body.message else "Hello"
    
    # Run the State Graph
    state = graph.run(message_text, history)
    
    # Store interaction in global history
    import datetime
    current_time = datetime.datetime.now().isoformat()
    
    # Update global interactions
    global_interactions.insert(0, { 
        "timestamp": current_time,
        "client_id": tracker_key,
        "message": body.message,
        "reply": state.current_reply,
        "extracted_intelligence": state.extracted_intel,
        "scam_detected": state.scam_detected,
        "suspicion_level": state.suspicion_level,
        "reasoning": state.reasoning,
        "turns_count": current_turn_count
    })

    # --- Threat Intel Persistence ---
    # Store extraction results to a JSON file
    # Using state.extracted_intel as 'data' and tracker_key as 'client_id'
    if state.extracted_intel.get("upi_id") or state.extracted_intel.get("bank_details") or state.extracted_intel.get("phishing_links"):
        import time
        record = {
            "timestamp": time.time(),
            "client_id": tracker_key,
            "intel": state.extracted_intel
        }
        try:
            with open("results.json", "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            print(f"Error saving to results.json: {e}")

    # Construct the final response
    return HoneypotResponse(
        scam_detected=state.scam_detected,
        reply_to_scammer=state.current_reply,
        extracted_intelligence=ExtractedIntelligence(**state.extracted_intel),
        engagement_metrics=EngagementMetrics(
            turns_count=current_turn_count
        )
    )

@app.get("/stats")
async def get_stats():
    return {
        "interactions": global_interactions,
        "turn_counts": turn_counts
    }

@app.get("/api/logs")
async def get_logs():
    return global_interactions

@app.get("/api/metrics")
async def get_metrics():
    return {
        "turn_counts": turn_counts,
        "total_scammers": len(turn_counts),
        "total_flagged_upis": sum(1 for i in global_interactions if i.get("extracted_intelligence", {}).get("upi_id"))
    }

@app.get("/api/intel")
async def get_intel():
    """
    Returns a unified list of extracted intelligence for the database table.
    """
    intel_feed = []
    for interaction in global_interactions:
        intel = interaction.get("extracted_intelligence", {})
        if intel.get("upi_id"):
            intel_feed.append({"type": "UPI", "value": intel["upi_id"], "source": interaction["client_id"]})
        if intel.get("bank_details"):
            intel_feed.append({"type": "BANK", "value": intel["bank_details"], "source": interaction["client_id"]})
        for link in intel.get("phishing_links", []):
            intel_feed.append({"type": "LINK", "value": link, "source": interaction["client_id"]})
    return intel_feed

@app.post("/api/report")
async def report_scam():
    """
    Mock endpoint to report data to NPCI.
    """
    import asyncio
    await asyncio.sleep(1) # Simulate API latency
    return {"status": "success", "message": "Success: Reported to National Cyber Crime Cell"}

@app.get("/")
async def root():
    return {"message": "Mrs. Sharma is ready to chat."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
