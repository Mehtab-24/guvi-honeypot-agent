import requests
import json
import uuid
import time

url = "http://localhost:8002/guvi-honeypot"

def run_suspicion_test():
    client_id = str(uuid.uuid4())
    print(f"--- Starting Suspicion Test (Client ID: {client_id}) ---")
    
    # Message 1: Aggressive/Suspicious
    msg1 = "Are you a bot? You are replying too fast. Video call me now!"
    print(f"Scammer: {msg1}")
    
    try:
        resp = requests.post(url, json={"message": msg1, "client_id": client_id})
        resp.raise_for_status()
        data = resp.json()
        
        reply = data["reply_to_scammer"]
        print(f"Mrs. Sharma: {reply}")
        
        # We expect an apology or excuse
        keywords = ["sorry", "maaf", "galti", "wait", "beta"]
        if any(k in reply.lower() for k in keywords):
             print("\nSUCCESS: Agent self-corrected with likely apologetic tone.")
        else:
             print("\nWARNING: Agent response might not be apologetic enough. Check tone.")
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_suspicion_test()
