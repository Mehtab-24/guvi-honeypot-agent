import os
import json
import re
from typing import Dict, List, Optional
from openai import OpenAI

# --- Agent Configuration ---
# OpenRouter Model ID
ORCHESTRATOR_MODEL = "deepseek/deepseek-r1" 
PERSONA_MODEL = "deepseek/deepseek-r1"
EXTRACTION_MODEL = "deepseek/deepseek-r1"

class BaseAgent:
    def __init__(self, api_key: str, model_name: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model_name = model_name

class OrchestratorAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key, ORCHESTRATOR_MODEL)
    
    def decide_next_step(self, message: str, history: List[Dict]) -> Dict:
        """
        Analyzes the input message and history to determine the scam intent and next state.
        """
        prompt = f"""
        Analyze the following conversation part.
        
        Last Message: "{message}"
        
        Roles:
        - "scam_detected": boolean. True if the user is trying to scam (phishing, lottery, asking for money/OTP).
        - "suspicion_level": "LOW", "MEDIUM", "HIGH". How suspicious is the scammer that they are talking to a bot?
          - HIGH: Scammer asks "Are you a bot?", "Why are you replying fast?", "Video call me".
          - MEDIUM: Scammer gets impatient.
          - LOW: Scammer is just proceeding with the script.
        
        Output JSON:
        {{
            "scam_detected": boolean,
            "suspicion_level": "LOW" | "MEDIUM" | "HIGH",
            "reasoning": "string explanation"
        }}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            # Fallback
            error_str = str(e)
            print(f"[ORCHESTRATOR ERROR]: {error_str}")
            import traceback
            traceback.print_exc()
            return {"scam_detected": False, "suspicion_level": "LOW", "reasoning": f"Error: {error_str[:50]}..."}

class PersonaAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key, PERSONA_MODEL)
    
    def generate_response(self, message: str, orchestrator_decision: Dict, extracted_intel: Dict) -> str:
        """
        Generates Mrs. Sharma's response based on the decision.
        """
        scam_detected = orchestrator_decision.get("scam_detected", False)
        suspicion = orchestrator_decision.get("suspicion_level", "LOW")
        
        system_instruction = """
        You are "Mrs. Sharma", an innocent, slightly confused, elderly Indian lady living in Delhi.
        Language: Hinglish (mix of Hindi and English).
        
        Strategies:
        1. NORMAL_CHAT (No scam): consistent with persona, polite.
        2. SCAM_ENGAGE (Scam detected, Low suspicion): Act gullible. Ask clarifying questions. Waste time.
        3. SCAM_DEFUSE (Scam detected, High/Med suspicion): SELF-CORRECTION MODE. The scammer thinks you are a bot. 
           - Apologize profusely.
           - Mention a believable excuse (e.g., "Sorry beta, nani aa gayi thi", "Main chashma dhoond rahi thi").
           - Reassure them you are listening.
        
        Goal: Keep them talking.
        """
        
        user_prompt = f"""
        Incoming Message: "{message}"
        Context:
        - Scam Detected: {scam_detected}
        - Suspicion Level: {suspicion}
        - Extracted So Far: {extracted_intel}
        
        Generate a JSON response:
        {{
            "reply": "Mrs. Sharma's response text"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return data.get("reply", "Arre beta, main samajh nahi paayi.")
        except Exception as e:
            print(f"[PERSONA ERROR]: {e}")
            return "Beta, aawaz kat rahi hai, phir se bolo?"

class ExtractionAgent(BaseAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key, EXTRACTION_MODEL)

    def extract_intelligence(self, message: str) -> Dict:
        """
        Extracts UPI, Bank, Links using Regex + LLM fallback.
        """
        # 1. Regex Heuristics (Fast & Cheap)
        upi_pattern = r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}'
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        
        upis = re.findall(upi_pattern, message)
        urls = re.findall(url_pattern, message)
        
        # 2. LLM Refinement
        prompt = f"""
        Extract structured intelligence from this message: "{message}"
        
        Find:
        - UPI IDs
        - Bank Account Numbers / IFSC
        - Phishing Links
        
        Output JSON:
        {{
            "upi_id": "string or null",
            "bank_details": "string or null",
            "phishing_links": ["list", "of", "urls"]
        }}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Merge regex findings
            if not data.get("upi_id") and upis:
                data["upi_id"] = upis[0]
            if not data.get("phishing_links"):
                data["phishing_links"] = []
            if urls:
                 # Add unique URLs
                 existing = set(data["phishing_links"])
                 for u in urls:
                     if u not in existing:
                         data["phishing_links"].append(u)
                
            return data
        except Exception as e:
            print(f"[EXTRACTION ERROR]: {e}")
            return {"upi_id": None, "bank_details": None, "phishing_links": []}
