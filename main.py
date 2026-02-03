from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/guvi-honeypot")
async def guvi_honeypot_endpoint(request: Request):
    """
    Placeholder POST endpoint for guvi-honeypot.
    Accepts any incoming data for honeypot monitoring.
    """
    # In a real implementation, you would log/process the incoming data
    return {"message": "GUVI Honeypot endpoint", "status": "received"}


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to GUVI Honeypot Agent API"}
