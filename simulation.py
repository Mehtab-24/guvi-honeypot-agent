import requests
import json
import time
import uuid

url = "http://localhost:8002/guvi-honeypot"

def run_simulation():
    test_client_id = str(uuid.uuid4())
    messages = [
        "Hello madam. I am calling from your bank. Urgent verification needed.",
        "Madam why are you not replying? I need 5000rs immediately to unblock card.",
        "Are you listening? Send money to police@axisb immediately or police will come.",
        "Ok tell me your OTP then. I am waiting.",
        "You are wasting my time. Last warning."
    ]

    print(f"--- Starting Simulation for Client ID: {test_client_id} ---")

    for i, msg in enumerate(messages):
        payload = {"message": msg, "client_id": test_client_id}
        try:
            r = requests.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            
            print(f"\nScammer: {msg}")
            print(f"Mrs. Sharma: {data.get('reply_to_scammer')}")
            
            new_count = data.get('engagement_metrics', {}).get('turns_count', 0)
            print(f"Turns Count {i+1}: {new_count}")

            time.sleep(1) 

        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    run_simulation()
