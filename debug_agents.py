import os
from dotenv import load_dotenv
from agents import OrchestratorAgent, PersonaAgent

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: API Key not found")
    exit(1)

print(f"✅ API Key found: {api_key[:5]}...")

try:
    print("Testing Orchestrator...")
    orchestrator = OrchestratorAgent(api_key=api_key)
    decision = orchestrator.decide_next_step("Hello, are you a bot?", history=[])
    print(f"✅ Orchestrator Result: {decision}")
except Exception as e:
    print(f"❌ Orchestrator Failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\nTesting Persona...")
    persona = PersonaAgent(api_key=api_key)
    response = persona.generate_response("Hello", {"scam_detected": False, "suspicion_level": "LOW"}, {})
    print(f"✅ Persona Result: {response}")
except Exception as e:
    print(f"❌ Persona Failed: {e}")
    traceback.print_exc()
