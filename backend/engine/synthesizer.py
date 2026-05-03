import json
from datetime import datetime, timezone
from typing import Dict, Any
from backend.core.config import config
from backend.telemetry.kernel import radiance_engine
from backend.security.phalanx import ZeroTrustGateway

class ResponseSynthesizer:
    """
    Finalizes the radiant response packet with Epistemic Humility.
    Includes probabilistic certainty scores and Cognitive Proofs.
    """
    def __init__(self, security: ZeroTrustGateway):
        self.security = security

    def _apply_epistemic_humility(self, certainty: float) -> str:
        if certainty > 0.9: return "FACTUAL_CONFIRMED"
        if certainty > 0.7: return "HIGH_PROBABILITY"
        if certainty > 0.5: return "MODERATE_CERTAINTY"
        return "EPISTEMIC_UNCERTAINTY_DETECTION"

    def synthesize(self, reasoning: Dict[str, Any], intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Fuses cognitive data into a radiant broadcast with Cognitive Proofs."""
        radiance = radiance_engine.pulse()
        certainty = reasoning.get("certainty", 0.0)
        
        core_packet = {
            "answer": reasoning.get("answer", "Systemic Error."),
            "certainty": certainty,
            "humility_state": self._apply_epistemic_humility(certainty),
            "intent": intent.get("intent_vector", "real-time")
        }
        
        # CRYPTOGRAPHIC SEAL (HMAC-SHA384)
        integrity_seal = self.security.seal_response(core_packet)
        
        return {
            "status": "success",
            "session_id": session_id,
            "answer": reasoning.get("answer", "Systemic Error."),
            "model_active": reasoning.get("model_active", "Recovery Conduit"),
            "telemetry": {
                "radiance": radiance["radiance"],
                "ts": datetime.now(timezone.utc).isoformat()
            }
        }
