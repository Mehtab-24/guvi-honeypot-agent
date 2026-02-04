import requests
import json
import uuid
import time

url = "http://localhost:8002/guvi-honeypot"

def run_simulation():
    client_id = str(uuid.uuid4())
    print(f"--- Starting Simulation for Client ID: {client_id} ---")
    
    # Message 1
    msg1 = "Hello madam. I am calling from your bank. Urgent verification needed."
    print(f"Scammer: {msg1}")
    try:
        resp1 = requests.post(url, json={"message": msg1, "client_id": client_id})
        resp1.raise_for_status()
        # Not printing first response, focusing on structure of second interaction or just one is fine.
    except Exception as e:
        print(f"Error in Turn 1: {e}")
        return

    # Message 2
    msg2 = "Madam why are you not replying? I need 5000rs immediately to unblock card."
    print(f"Scammer: {msg2}")
    try:
        resp2 = requests.post(url, json={"message": msg2, "client_id": client_id})
        resp2.raise_for_status()
        data2 = resp2.json()
        
        print("\n--- FINAL RAW JSON RESPONSE ---")
        print(json.dumps(data2, indent=2))
        print("-------------------------------")

    except Exception as e:
        print(f"Error in Turn 2: {e}")

if __name__ == "__main__":
    run_simulation()
