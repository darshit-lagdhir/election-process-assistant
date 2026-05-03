import asyncio
import time
from typing import Dict, Any, Optional
from backend.core.config import config
from backend.core.result import Result, Success, Failure, attempt_async
from backend.core.events import dispatcher
from backend.core.supervision import supervisor
from backend.security.phalanx import security_phalanx, SecurityInterception
from backend.engine.bridge import NeuralReasoningBridge
from backend.engine.synthesizer import ResponseSynthesizer
from backend.telemetry.kernel import radiance_engine, logger

class TransactionCache:
    """The Immutable Ledger: Enforces idempotency across the systemic conduits."""
    def __init__(self, capacity: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._order = []
        self.capacity = capacity
        self._lock = asyncio.Lock()

    async def get(self, request_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            return self._cache.get(request_id)

    async def set(self, request_id: str, result: Dict[str, Any]):
        async with self._lock:
            if request_id not in self._cache:
                if len(self._order) >= self.capacity:
                    oldest = self._order.pop(0)
                    del self._cache[oldest]
                self._cache[request_id] = result
                self._order.append(request_id)

class HadronTranscendentEngine:
    """
    The Supreme Orchestrator: Unified cognitive and resilience substrate.
    Implements Dynamic Latency Optimization and Idempotency.
    """
    def __init__(self):
        self.security = security_phalanx
        self.bridge = NeuralReasoningBridge()
        self.synthesizer = ResponseSynthesizer(security_phalanx)
        self.ledger = TransactionCache()
        self.semaphore = asyncio.Semaphore(config.CPU_CONCURRENCY_THRESHOLD)
        
        self.bridge_guard = supervisor.get_guard("NEURAL_BRIDGE")

    async def execute(self, query: str, session_id: str, request_id: str) -> Dict[str, Any]:
        """
        Executes a cognitive cycle with Dynamic Latency Optimization.
        """
        cached_result = await self.ledger.get(request_id)
        if cached_result:
            return cached_result

        start_ts = time.time()
        
        async with self.semaphore:
            # 1. SECURITY INGRESS
            try:
                safe_query = self.security.intercept(query)
            except SecurityInterception as si:
                return self._handle_failure(str(si), "quarantine", session_id, start_ts)

            # 2. NEURAL REASONING
            try:
                reasoning_res: Result[Dict[str, Any], str] = await asyncio.wait_for(
                    self.bridge_guard.call(self.bridge.infer, safe_query),
                    timeout=config.REASONING_TIMEOUT
                )
            except Exception as e:
                return self._handle_failure(str(e), "bridge_fault", session_id, start_ts)

            if reasoning_res.is_failure():
                return self._handle_failure(reasoning_res.error(), "bridge_fault", session_id, start_ts)

            # 3. RADIANT SYNTHESIS
            try:
                reasoning_data = reasoning_res.unwrap()
                final_response = self.synthesizer.synthesize(
                    reasoning_data, 
                    {"intent_vector": "real-time"}, 
                    session_id
                )
            except Exception as e:
                return self._handle_failure(str(e), "synthesis_fault", session_id, start_ts)
            
            await self.ledger.set(request_id, final_response)
            return final_response

    def _handle_failure(self, error: str, status: str, session_id: str, start_ts: float) -> Dict[str, Any]:
        latency = (time.time() - start_ts) * 1000
        logger.error("engine_execution_failure", status=status, error=error, latency=latency)
        
        dispatcher.dispatch("ENGINE", "CONVERGENCE_FAILURE", 
                          {"session_id": session_id, "error": error, "status": status},
                          radiance=radiance_engine.compute_radiance())
        
        return {
            "status": status,
            "error": error,
            "session_id": session_id,
            "radiance": radiance_engine.compute_radiance(),
            "ts": time.time()
        }

hadron_engine = HadronTranscendentEngine()
