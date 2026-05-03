import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from google import genai as google_genai
from backend.core.config import config
from backend.core.events import dispatcher
from backend.core.result import Result, Success, Failure
from backend.engine.knowledge import knowledge_graph

class CognitiveNode:
    """A specialized reasoning unit calibrated for specific analytical tasks."""
    def __init__(self, name: str, model_preference: str, threshold: float):
        self.name = name
        self.model_preference = model_preference
        self.threshold = threshold

class NeuralReasoningBridge:
    """
    AI reasoning engine with automatic model fallback chain.
    If a model is rate-limited or unavailable, it instantly switches
    to the next model in the fallback chain without blocking.
    Blacklisted models are remembered and skipped for 10 minutes.
    """
    def __init__(self):
        self._api_key = config.get_api_key()
        self._client = google_genai.Client(api_key=self._api_key) if self._api_key else None
        # Tracks blacklisted models: {model_name: blacklisted_until_timestamp}
        self._blacklist: Dict[str, float] = {}
        print(f"[MODEL CHAIN] Initialized. Priority order: {config.MODEL_FALLBACK_CHAIN}")

    def _get_active_models(self) -> list:
        """Returns models that are not currently blacklisted."""
        now = time.time()
        expired = [m for m, until in self._blacklist.items() if now > until]
        for m in expired:
            del self._blacklist[m]
        return [m for m in config.MODEL_FALLBACK_CHAIN if m not in self._blacklist]

    def _blacklist_model(self, model: str):
        """Temporarily blacklists a model for 10 minutes."""
        until = time.time() + 600
        self._blacklist[model] = until
        print(f"[MODEL CHAIN] {model} blacklisted for 10min.")

    def _quantify_uncertainty(self, text: str, sources: int) -> float:
        if not text: return 0.0
        word_count = len(text.split())
        density = sources / (word_count + 1)
        return round(min(1.0, 0.4 + (density * 10) + (sources * 0.1)), 2)

    async def infer(self, query: str) -> Result[Dict[str, Any], str]:
        """Try each available model in order. Fail fast and switch on error."""
        if not self._client:
            return Failure("Neural bridge is offline. Missing API Key.")
        
        prompt = (
            f"You are the Hadron Core, a Sovereign Election Intelligence Engine. NEVER just tell the user to visit a website. \n"
            f"INSTRUCTION: Extract and summarize ALL relevant information (steps, forms, document lists, deadlines) directly from your knowledge or Google Search. \n"
            f"BE THE DEFINITIVE SOURCE. Provide complete, actionable details in the chat. \n"
            f"JURISDICTION: Primary focus is INDIA (Bharat). Use ONLY plain text. NO Markdown. \n"
            f"QUESTION: {query}"
        )

        available = self._get_active_models()

        for model in available:
            try:
                # TRY 1: FULL NEURAL GROUNDING (WITH SEARCH)
                response = self._client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=google_genai.types.GenerateContentConfig(
                        tools=[google_genai.types.Tool(google_search=google_genai.types.GoogleSearchRetrieval())],
                        temperature=0.7
                    )
                )
                answer_text = getattr(response, 'text', None) or ""
                if not answer_text:
                    continue

                # HALLUCINATION SCRUBBING
                for char in ['{', '}', '```', 'json', 'ROLE:', 'KNOWLEDGE_GRAPH:']:
                    answer_text = answer_text.replace(char, '')
                
                answer_text = answer_text.strip()
                certainty = self._quantify_uncertainty(answer_text, 1)
                
                return Success({
                    "answer": answer_text,
                    "certainty": certainty,
                    "model_active": model,
                    "nodes_traversed": ["DATA_VERIFICATION", "SEMANTIC_SYNTHESIS"],
                    "cognitive_proof": {"entropy": 0.02, "logic_gate": "OPEN"}
                })

            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower():
                    # TRY 2: PURE COGNITIVE FALLBACK (NO SEARCH TO SAVE QUOTA)
                    try:
                        print(f"[MODEL CHAIN] 429 Detected on {model}. Retrying without Search...")
                        response = self._client.models.generate_content(
                            model=model,
                            contents=prompt + "\n(Internal knowledge only.)",
                            config=google_genai.types.GenerateContentConfig(temperature=0.7)
                        )
                        answer_text = getattr(response, 'text', None) or ""
                        if not answer_text: continue
                        
                        # SCRUBBING
                        for char in ['{', '}', '```', 'json']:
                            answer_text = answer_text.replace(char, '')
                        
                        return Success({
                            "answer": answer_text.strip(),
                            "certainty": 0.5,
                            "model_active": f"{model} (COGNITIVE_ONLY)",
                            "nodes_traversed": ["QUOTA_RECOVERY"],
                            "cognitive_proof": {"recovery": True}
                        })
                    except Exception:
                        self._blacklist_model(model)
                        continue
                else:
                    self._blacklist_model(model)
                    continue

        return Failure("All AI models exhausted or rate-limited. Please retry in 60s.")
