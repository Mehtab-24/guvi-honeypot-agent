from dataclasses import dataclass, field
from typing import List, Dict, Optional
from agents import OrchestratorAgent, PersonaAgent, ExtractionAgent

@dataclass
class WorkflowState:
    history: List[Dict] = field(default_factory=list)
    current_input: str = ""
    extracted_intel: Dict = field(default_factory=lambda: {
        "upi_id": None, "bank_details": None, "phishing_links": []
    })
    scam_detected: bool = False
    suspicion_level: str = "LOW" # LOW, MEDIUM, HIGH
    reasoning: str = "" # Explanation from Orchestrator
    current_reply: str = ""

class StateGraph:
    def __init__(self, api_key: str):
        self.orchestrator = OrchestratorAgent(api_key)
        self.persona = PersonaAgent(api_key)
        self.extractor = ExtractionAgent(api_key)
    
    def run(self, message: str, history: List[Dict]) -> WorkflowState:
        # Initialize State
        state = WorkflowState(history=history, current_input=message)
        
        # Step 1: Parallel Execution (Conceptually)
        # - Extract Intelligence
        # - Orchestrate Decision
        
        # A. Extraction
        new_intel = self.extractor.extract_intelligence(message)
        self._merge_intel(state, new_intel)
        
        # B. Orchestration
        decision = self.orchestrator.decide_next_step(message, history)
        state.scam_detected = decision.get("scam_detected", False)
        state.suspicion_level = decision.get("suspicion_level", "LOW")
        state.reasoning = decision.get("reasoning", "")
        
        # Step 2: Generate Response based on State
        # The logic for "Self-Correction" is handled inside the PersonaAgent's prompt 
        # by passing the `suspicion_level`. If HIGH, it apologizes.
        
        reply = self.persona.generate_response(
            message, 
            decision, 
            state.extracted_intel
        )
        state.current_reply = reply
        
        return state

    def _merge_intel(self, state: WorkflowState, new_intel: Dict):
        """Merges new intelligence into the existing state."""
        if new_intel.get("upi_id"):
            state.extracted_intel["upi_id"] = new_intel["upi_id"]
        if new_intel.get("bank_details"):
            state.extracted_intel["bank_details"] = new_intel["bank_details"]
        if new_intel.get("phishing_links"):
            # Avoid duplicates
            existing = set(state.extracted_intel["phishing_links"])
            new_links = set(new_intel["phishing_links"])
            state.extracted_intel["phishing_links"] = list(existing.union(new_links))
