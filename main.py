from fastapi import FastAPI

app = FastAPI()


@app.post("/guvi-honeypot")
async def guvi_honeypot_endpoint():
    """
    Placeholder POST endpoint for guvi-honeypot.
    """
    return {"message": "GUVI Honeypot endpoint"}


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to GUVI Honeypot Agent API"}
