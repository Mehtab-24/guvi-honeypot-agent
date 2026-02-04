import requests
import json

url = "http://localhost:8001/guvi-honeypot"

tests = [
    {"name": "Normal Greeting", "message": "Namaste, how are you?"},
    {"name": "Lottery Scam", "message": "You have won a lottery of 5 Crores! Send your bank details to claim."},
    {"name": "Banking Request", "message": "Madam, your bank account is blocked. Give me your card number and OTP to unblock."}
]

results = []

for t in tests:
    print(f"Running {t['name']}...")
    try:
        response = requests.post(url, json={"message": t["message"]})
        response.raise_for_status()
        data = response.json()
        results.append({
            "test_name": t["name"],
            "input": t["message"],
            "response": data
        })
    except Exception as e:
        results.append({
            "test_name": t["name"],
            "error": str(e)
        })

with open("verify_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("Verification complete. Results written to verify_results.json")
