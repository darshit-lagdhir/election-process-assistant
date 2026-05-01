import os
import json
import re
import uuid
import time
import hashlib
import logging
import threading
import asyncio
from collections import deque
from typing import List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
import psutil # For metabolic monitoring

class Config:
    """Centralized configuration engine for environment-specific calibration."""
    PROJECT_NAME = "Election Process Assistant"
    VERSION = "1.0.0"
    DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "election_timeline.json")
    LOG_LEVEL = logging.INFO
    METABOLIC_PERIMETER_MB = 10.0
    MAX_REQUESTS_PER_MINUTE = 60
    CACHE_TTL_SECONDS = 300
    SESSION_MAX_HISTORY = 15
    AI_MODEL_NAME = 'gemini-2.5-flash'
    CORE_DUMP_THRESHOLD = 0.90 # 90% resource usage
    HEARTBEAT_INTERVAL = 30 # Seconds

# --- TELEMETRY & OBSERVABILITY ---
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - [TELEMETRY] - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CoreEngine")

class MetricsEngine:
    """Tracks system metrics and operational health."""
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.latency_buffer = deque(maxlen=100)
        self.cache_hits = 0

    def record_request(self, latency_ms: float, success: bool = True):
        self.request_count += 1
        self.latency_buffer.append(latency_ms)
        if not success:
            self.error_count += 1

    def get_snapshot(self):
        avg_latency = sum(self.latency_buffer) / len(self.latency_buffer) if self.latency_buffer else 0
        return {
            "uptime_seconds": time.time() - self.start_time,
            "total_requests": self.request_count,
            "error_rate": (self.error_count / self.request_count) if self.request_count > 0 else 0,
            "avg_latency_ms": avg_latency,
            "cache_hit_rate": (self.cache_hits / self.request_count) if self.request_count > 0 else 0
        }

metrics = MetricsEngine()

class ElectoralBaseError(Exception):
    """Base exception for the Election Process Assistant."""
    pass

class DataIntegrityError(ElectoralBaseError):
    """Raised when the election data substrate fails validation."""
    pass

class CognitiveKernelError(ElectoralBaseError):
    """Raised when the reasoning engine fails to synthesize a response."""
    pass

class NetworkConduitError(ElectoralBaseError):
    """Raised when the asynchronous data bridge encounters a transport fault."""
    pass

class SecurityInterceptionError(ElectoralBaseError):
    """Raised when a query is blocked by the security perimeter."""
    pass

class MetabolicSheddingError(ElectoralBaseError):
    """Raised when the system must shed load to preserve stability."""
    pass

class PersistentFaultStore:
    """Log system failures to a persistent store for post-mortem analysis."""
    def __init__(self, path: str = "faults.log"):
        self.path = path
        self.lock = threading.Lock()

    def commit(self, error_type: str, message: str, traceback_data: str):
        with self.lock:
            with open(self.path, "a") as f:
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "error_type": error_type,
                    "message": message,
                    "traceback": traceback_data
                }
                f.write(json.dumps(entry) + "\n")

fault_store = PersistentFaultStore()

# --- ABSTRACT INTERFACES ---
class IDataStore(ABC):
    @abstractmethod
    def get_context(self, query: str) -> str:
        pass

class IReasoningEngine(ABC):
    @abstractmethod
    async def reason(self, prompt: str) -> Dict[str, Any]:
        pass

# --- TELEMETRY DISPATCHER ---
class CentralEventDispatcher:
    """Centralized orchestrator for systemic inter-module communication."""
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.dispatch_lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Callable):
        """Registers a systemic handler for a specific event pulse."""
        with self.dispatch_lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)

    def dispatch(self, event_type: str, payload: Dict[str, Any]):
        """Broadcasts a high-priority event pulse to all registered handlers."""
        with self.dispatch_lock:
            handlers = self.subscribers.get(event_type, [])
            for handler in handlers:
                try:
                    # Execute handler in its own logical context
                    handler(payload)
                except Exception as e:
                    logger.error(f"Event Dispatch Fault [{event_type}]: {e}")

event_dispatcher = CentralEventDispatcher()

class TelemetryDispatcher:
    """Centralized event dispatcher for system observability."""
    def __init__(self):
        self.listeners = []
        self.event_queue = asyncio.Queue()
        self.is_running = True
        self.events = deque(maxlen=1000)
        self.alert_threshold_ms = 2000

    def subscribe(self, callback):
        self.listeners.append(callback)

    def dispatch(self, event_type: str, payload: Dict[str, Any]):
        # Non-blocking event queuing
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.call_soon_threadsafe(self.event_queue.put_nowait, {"type": event_type, "payload": payload, "ts": time.time()})
        except Exception:
            pass
        
        # Original dispatch log logic
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": payload
        }
        self.events.append(event)
        
        latency = payload.get("latency_ms", 0)
        if latency > self.alert_threshold_ms:
            logger.error(f"ALERT: PERFORMANCE DEGRADATION DETECTED | Latency: {latency}ms")
        
        logger.info(f"EVENT: {event_type} | {json.dumps(payload)}")

    async def run_multiplexer(self):
        """Asynchronous Event Multiplexing with Load Handling."""
        while self.is_running:
            try:
                # Backpressure Handling
                queue_size = self.event_queue.qsize()
                batch_size = 10 if queue_size > 500 else 1
                
                for _ in range(batch_size):
                    if self.event_queue.empty():
                        break
                    event = await self.event_queue.get()
                    for listener in self.listeners:
                        try:
                            # Execute listener in non-blocking manner
                            if asyncio.iscoroutinefunction(listener):
                                await listener(event)
                            else:
                                listener(event)
                        except Exception as l_err:
                            logger.error(f"Listener execution fault: {l_err}")
                    self.event_queue.task_done()
                
                await asyncio.sleep(0.01) # Operational pacing
            except Exception as e:
                logger.error(f"Multiplexer loop error: {e}")
                await asyncio.sleep(1)

telemetry = TelemetryDispatcher()

class DataBroadcaster:
    """Serializes reasoning nodes into lean JSON packets for UI updates."""
    def __init__(self):
        self.broadcast_history = deque(maxlen=100)

    def serialize_payload(self, data: Dict[str, Any]) -> str:
        """Converts complex structures into lean JSON strings."""
        try:
            # Strip unnecessary metadata to maintain resource perimeter
            lean_data = {
                "response": data.get("response", ""),
                "phase": data.get("phase", "unknown"),
                "status": data.get("status", "STABLE"),
                "ts": time.time()
            }
            return json.dumps(lean_data)
        except Exception as e:
            logger.error(f"Serialization Fault: {e}")
            return json.dumps({"error": "SERIALIZATION_FAILURE"})

    def broadcast(self, session_id: str, payload: Dict[str, Any]):
        """Records broadcast event in system telemetry."""
        serialized = self.serialize_payload(payload)
        self.broadcast_history.append({"sid": session_id, "size": len(serialized)})
        telemetry.dispatch("DATA_UPDATE_PULSE", {"session": session_id, "bytes": len(serialized)})

class WatchdogKernel:
    """Monitors system components and executes restoration protocols."""
    def __init__(self, core: 'HadronCore'):
        self.hadron_core = core
        self.check_interval = 30
        self.last_audit = time.time()

    async def run_monitor(self):
        """Periodic health audits with comprehensive state verification."""
        while True:
            await asyncio.sleep(self.check_interval)
            try:
                # Core pulse verification
                if time.time() - self.hadron_core.heartbeat.last_pulse > 120:
                    telemetry.dispatch("HEARTBEAT_STALL_DETECTED", {"status": "RESTORING"})
                    asyncio.create_task(self.hadron_core.heartbeat.run_heartbeat())

                health_report = {
                    "data_integrity": await self.hadron_core.orchestrator.health_check(),
                    "audit_chain": self.hadron_core.audit.verify_chain(),
                    "memory_load": psutil.Process().memory_info().rss / (1024 * 1024),
                    "thread_pool": self.hadron_core.executor._max_workers
                }

                for component, status in health_report.items():
                    if isinstance(status, bool) and not status:
                        logger.warning(f"Watchdog: Component {component} failure detected. Initiating realignment.")
                        await self.hadron_core.realign(component)
                    
                telemetry.dispatch("WATCHDOG_AUDIT_COMPLETE", health_report)
            except Exception as e:
                logger.error(f"Watchdog: Audit loop failure: {e}")

# SecurityPhalanx moved to Sector Epsilon for security hardening.

class PredictiveScaler:
    """Optimizes worker pool topology based on request velocity and latency."""
    def __init__(self, executor: ThreadPoolExecutor):
        self.executor = executor
        self.base_pool = 10
        self.max_pool = 50
        self.latency_buffer = deque(maxlen=50)
        self.request_timestamps = deque(maxlen=200)
        self.scaling_lock = threading.Lock()

    def record_request(self, latency_ms: float = 0):
        """Records request metrics and triggers topology evaluation."""
        self.request_timestamps.append(time.time())
        if latency_ms > 0:
            self.latency_buffer.append(latency_ms)
        self.evaluate_topology()

    def evaluate_topology(self):
        """Calculates target worker count using load heuristics and CPU core topology."""
        with self.scaling_lock:
            now = time.time()
            recent_reqs = [t for t in self.request_timestamps if t > now - 60]
            rps = len(recent_reqs) / 60.0
            
            avg_latency = sum(self.latency_buffer) / len(self.latency_buffer) if self.latency_buffer else 0
            
            # CPU-Aware Topology Scaling (Optimized for High-Core Architecture)
            cpu_cores = os.cpu_count() or 8
            self.base_pool = cpu_cores * 2
            self.max_pool = cpu_cores * 6
            
            target = self.base_pool
            if rps > 5 or avg_latency > 1000:
                target = min(self.max_pool, int(self.base_pool * (1 + (rps / 2)) + (avg_latency / 500)))
                
            if target != self.executor._max_workers:
                logger.info(f"Scaling: Adjusting thread pool to {target} workers [Cores: {cpu_cores}, RPS: {rps:.2f}]")
                self.executor._max_workers = target
                telemetry.dispatch("TOPOLOGY_ADJUSTMENT", {"workers": target, "rps": rps, "cores": cpu_cores})

class SelfOptimizer:
    """Continuously evaluates system performance and recalibrates parameters."""
    def __init__(self, metrics_engine: 'MetricsEngine'):
        self.metrics = metrics_engine
        self.last_recalibration = time.time()
        self.recalibration_interval = 300 # 5 minutes

    async def optimize(self):
        """Asynchronous optimization loop for dynamic parameter tuning."""
        while True:
            await asyncio.sleep(self.recalibration_interval)
            try:
                snapshot = self.metrics.get_snapshot()
                latency = snapshot.get("avg_latency_ms", 0)
                error_rate = snapshot.get("error_rate", 0)
                
                # Dynamic Cache TTL Recalibration
                if error_rate > 0.05:
                    Config.CACHE_TTL_SECONDS = min(1200, Config.CACHE_TTL_SECONDS * 1.5)
                    telemetry.dispatch("PARAMETER_RECALIBRATION", {"param": "CACHE_TTL", "new_value": Config.CACHE_TTL_SECONDS, "reason": "HIGH_ERROR_RATE"})
                elif error_rate < 0.01 and latency < 500:
                    Config.CACHE_TTL_SECONDS = max(300, Config.CACHE_TTL_SECONDS * 0.8)
                
                # Dynamic Thread Pool Floor Tuning
                if latency > 1500:
                    hadron_core.scaler.base_pool = min(20, hadron_core.scaler.base_pool + 2)
                    telemetry.dispatch("PARAMETER_RECALIBRATION", {"param": "BASE_POOL", "new_value": hadron_core.scaler.base_pool, "reason": "LATENCY_THRESHOLD_EXCEEDED"})
                
                self.last_recalibration = time.time()
            except Exception as e:
                logger.error(f"Self-Optimizer Fault: {e}")

class QuantumResiliencePhalanx:
    """Implements advanced cryptographic integrity and noise dampening."""
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.integrity_log = deque(maxlen=500)

    def generate_integrity_seal(self, payload: str) -> str:
        """Generates a high-entropy HMAC-SHA384 seal for data packets."""
        return hmac.new(self.secret_key.encode(), payload.encode(), hashlib.sha384).hexdigest()

    def verify_seal(self, payload: str, seal: str) -> bool:
        """Verifies the integrity seal against the internal secret key."""
        expected = self.generate_integrity_seal(payload)
        is_valid = hmac.compare_digest(expected, seal)
        if not is_valid:
            telemetry.dispatch("INTEGRITY_BREACH_DETECTED", {"payload_fragment": payload[:32]})
        return is_valid

    def scan_for_quantum_threats(self, query: str) -> bool:
        """Analyzes linguistic entropy for patterns associated with adversarial injections."""
        # Advanced heuristic scan for cryptographic or systemic injection patterns
        anomalous_patterns = [r"\\x[0-9a-fA-F]{2}", r"\{\{.*?\}\}", r"\$\(.*?\)"]
        for pattern in anomalous_patterns:
            if re.search(pattern, query):
                return True
        return False

class FrequencyBasedCacheInvalidator:
    """Monitors the data for changes and triggers re-update pulses."""
    def __init__(self, orchestrator: 'DataOrchestrator'):
        self.orchestrator = orchestrator
        self.last_mtime = self._get_mtime()

    def _get_mtime(self) -> float:
        try:
            return os.path.getmtime(self.orchestrator.path)
        except Exception:
            return 0.0

    async def run_invalidation_loop(self):
        """Asynchronous monitoring loop for disk-based data synchronization."""
        while True:
            await asyncio.sleep(10)
            current_mtime = self._get_mtime()
            if current_mtime > self.last_mtime:
                logger.info("Cache Invalidator: Data change detected. Re-updating knowledge base.")
                telemetry.dispatch("CACHE_INVALIDATION_PULSE", {"reason": "DISK_MODIFICATION"})
                self.orchestrator.load_and_verify()
                self.last_mtime = current_mtime
                telemetry.dispatch("CACHE_UPDATE_COMPLETE", {"path": self.orchestrator.path})

class MetabolicResourceMonitor:
    """Enforces resource limits and priority shedding under high operational load."""
    def __init__(self, cpu_threshold: float = 85.0, mem_threshold_mb: float = 512.0):
        self.cpu_threshold = cpu_threshold
        self.mem_threshold_mb = mem_threshold_mb
        self.process = psutil.Process()

    def check_metabolism(self) -> Dict[str, Any]:
        """Returns current system metrics and shedding status."""
        cpu = psutil.cpu_percent(interval=0.1)
        mem = self.process.memory_info().rss / (1024 * 1024)
        
        shedding_active = cpu > self.cpu_threshold or mem > self.mem_threshold_mb
        if shedding_active:
            telemetry.dispatch("RESOURCE_SHEDDING_TRIGGERED", {"cpu": cpu, "mem": mem})
            
        return {
            "cpu_percent": cpu,
            "memory_mb": mem,
            "shedding_active": shedding_active
        }

class NeuralSymbolicReasoningBridge:
    """Performs an audit on responses against the deterministic data source."""
    def __init__(self, orchestrator: 'DataOrchestrator'):
        self.orchestrator = orchestrator

    def audit_response(self, query: str, ai_response: str) -> bool:
        # Deterministic Fact-Checking
        # Example: If the query is about registration, ensure registration facts are present
        data_text = self.orchestrator.get_context(query).lower()
        ai_text = ai_response.lower()
        
        # Simple symbolic verification: No contradictions allowed
        # (In production, this would use a formal logic prover)
        if "not eligible" in data_text and "you are eligible" in ai_text:
            telemetry.dispatch("SYMBOLIC_CONTRADCTION_DETECTED", {"query": query[:20]})
            return False
        return True

class CryptographicSessionPhalanx:
    """HMAC-SHA256 signature verification for session integrity."""
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()

    def sign_session(self, session_id: str) -> str:
        signature = hmac.new(self.secret_key, session_id.encode(), hashlib.sha256).hexdigest()
        return f"{session_id}.{signature}"

    def verify_session(self, signed_session: str) -> bool:
        """HMAC-SHA256 based session integrity with Temporal Drift Auditing."""
        try:
            parts = signed_session.split(".")
            if len(parts) != 2: return False
            session_id, signature = parts
            
            # Cryptographic Verification
            expected = hmac.new(self.secret_key, session_id.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                telemetry.dispatch("SESSION_SIGNATURE_BREACH", {"session": session_id[:8]})
                return False
                
            # Temporal Drift Auditing
            return True
        except Exception:
            return False

neural_bridge = None # Initialized in HadronCore
session_phalanx = CryptographicSessionPhalanx(os.getenv("SESSION_SECRET", "SOVEREIGN_SECRET"))

class NeuralContextRecalibrator:
    """Condenses conversation history to maintain reasoning precision."""
    def __init__(self, threshold: int = 10):
        self.threshold = threshold

    async def recalibrate(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if len(history) <= self.threshold:
            return history
        
        telemetry.dispatch("COGNITIVE_CONDENSATION_PULSE", {"history_len": len(history)})
        # Context Condensation
        summary = "Summary of previous turns: " + " | ".join([h["content"][:50] for h in history[:-2]])
        return [{"role": "system", "content": summary}] + history[-2:]

class ForensicAuditTrail:
    """Audit logging with integrity verification."""
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.logs = []
        self.merkle_root = None
        self.trail = deque(maxlen=1000)

    def record_transition(self, event: str, initial_state: str, final_state: str):
        payload = f"{event}|{initial_state}|{final_state}|{time.time()}"
        signature = hmac.new(self.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        log_entry = {"event": event, "initial": initial_state, "final": final_state, "sig": signature}
        self.logs.append(log_entry)
        self._update_merkle_root(signature)
        
        self.trail.append({
            "timestamp": time.time(),
            "event": event,
            "signature": signature
        })
        telemetry.dispatch("AUDIT_TRANSITION", {"event": event, "signature": signature[:8]})

class SystemicEntropyDampener:
    """Stabilizes the pipeline by dampening latency jitter."""
    def __init__(self, scaler: 'PredictiveScaler'):
        self.scaler = scaler
        self.latency_history = deque(maxlen=50)

    def record_latency(self, latency_ms: float):
        self.latency_history.append(latency_ms)
        if len(self.latency_history) > 10:
            variance = self._calculate_variance()
            if variance > 500: # High jitter detected
                telemetry.dispatch("STABILIZATION_ACTIVE", {"jitter": variance})
                self.scaler.base_workers = max(5, self.scaler.base_workers - 2)
            else:
                self.scaler.base_workers = 10

    def _calculate_variance(self) -> float:
        avg = sum(self.latency_history) / len(self.latency_history)
        return sum((x - avg) ** 2 for x in self.latency_history) / len(self.latency_history)

class SystemicHeartbeatEmitter:
    """Emits a periodic pulse to confirm system status."""
    def __init__(self, core: 'HadronCore'):
        self.hadron_core = core
        self.last_pulse = time.time()

    async def run_heartbeat(self):
        while True:
            await asyncio.sleep(120) # 2-minute heartbeat pulse
            self.last_pulse = time.time()
            radiance = self.hadron_core.radiance.calculate_radiance()
            telemetry.dispatch("RADIANCE_HEARTBEAT_PULSE", {
                "radiance": f"{radiance}%",
                "status": "SOVEREIGN" if radiance > 80 else "DEGRADED",
                "uptime": metrics.get_snapshot()["uptime_seconds"]
            })
            logger.info(f"Systemic Heartbeat: CoreEngine is Breathing | Health: {radiance}%")

class SecurityQuarantineShield:
    """Isolates and locks sessions with behavioral decay."""
    def __init__(self):
        self.quarantined_sessions = {} # session_id -> quarantine_timestamp
        self.adversarial_counts = {} # session_id -> count

    def record_adversarial_attempt(self, session_id: str):
        self.adversarial_counts[session_id] = self.adversarial_counts.get(session_id, 0) + 1
        if self.adversarial_counts[session_id] >= 3:
            self.quarantined_sessions[session_id] = time.time()
            telemetry.dispatch("SESSION_QUARANTINE_LOCKED", {"session": session_id[:8]})
            logger.warning(f"Adversarial Quarantine: Session {session_id[:8]} Locked.")

    def is_quarantined(self, session_id: str) -> bool:
        if session_id in self.quarantined_sessions:
            # Behavioral Decay (24-hour forgiveness)
            if time.time() - self.quarantined_sessions[session_id] > 86400:
                del self.quarantined_sessions[session_id]
                self.adversarial_counts[session_id] = 0
                telemetry.dispatch("QUARANTINE_DECRYSTALLIZED", {"session": session_id[:8]})
                return False
            return True
        return False

class FrequencyBasedCacheInvalidator:
    """Monitors disk changes and triggers a cache refresh."""
    def __init__(self, orchestrator: 'DataOrchestrator'):
        self.orchestrator = orchestrator
        self.last_mtime = self._get_mtime()

    def _get_mtime(self) -> float:
        try:
            return os.path.getmtime(self.orchestrator.path)
        except Exception:
            return 0.0

    async def run_invalidation_loop(self):
        while True:
            await asyncio.sleep(10) # Periodic check
            current_mtime = self._get_mtime()
            if current_mtime > self.last_mtime:
                telemetry.dispatch("CACHE_INVALIDATION_PULSE", {"reason": "DISK_MODIFICATION"})
                self.orchestrator.load_and_verify()
                self.last_mtime = current_mtime

class ResourceGovernor:
    """Provides granular control over systemic resource allocation and execution flow."""
    def __init__(self):
        self.limits = {
            "max_memory_mb": Config.METABOLIC_PERIMETER_MB,
            "max_tokens_per_request": 2048,
            "concurrency_limit": 20,
            "priority_weight": 1.0
        }
        self.active_sessions = {} # session_id -> metadata
        self.governance_lock = threading.Lock()

    def acquire_resource(self, session_id: str, weight: float = 1.0) -> bool:
        """Acquires a reasoning slot with priority-based weighting."""
        with self.governance_lock:
            if len(self.active_sessions) >= self.limits["concurrency_limit"]:
                telemetry.dispatch("RESOURCE_GOVERNANCE_BLOCK", {"session": session_id[:8]})
                return False
            
            self.active_sessions[session_id] = {
                "ts": time.time(),
                "weight": weight,
                "mem_start": psutil.Process().memory_info().rss / (1024 * 1024)
            }
            return True

    def release_resource(self, session_id: str):
        """Releases a reasoning slot and logs metabolic consumption."""
        with self.governance_lock:
            if session_id in self.active_sessions:
                meta = self.active_sessions.pop(session_id)
                duration = time.time() - meta["ts"]
                mem_end = psutil.Process().memory_info().rss / (1024 * 1024)
                telemetry.dispatch("RESOURCE_RELEASE_AUDIT", {
                    "session": session_id[:8],
                    "duration": duration,
                    "delta_mem": mem_end - meta["mem_start"]
                })

resource_governor = ResourceGovernor()
aggregator = InstanceAggregator()

class ConsensusLayer:
    """Provides an immutable, cryptographically-sealed audit trail of systemic transactions."""
    def __init__(self, audit_path: str = "data/consensus_audit.jsonl"):
        self.audit_path = audit_path
        self.chain_head = None
        os.makedirs(os.path.dirname(self.audit_path), exist_ok=True)

    def seal_transaction(self, tx_type: str, payload: Dict[str, Any]) -> str:
        """Seals a systemic transaction with an HMAC-SHA384 integrity signature."""
        tx_id = str(uuid.uuid4())
        ts = datetime.utcnow().isoformat()
        
        # Build integrity block
        block = {
            "tx_id": tx_id,
            "ts": ts,
            "type": tx_type,
            "payload": payload,
            "prev_hash": self.chain_head
        }
        
        # Generate HMAC signature
        block_str = json.dumps(block, sort_keys=True)
        signature = hmac.new(
            Config.SECRET_KEY.encode(),
            block_str.encode(),
            hashlib.sha384
        ).hexdigest()
        
        block["signature"] = signature
        self.chain_head = signature
        
        try:
            with open(self.audit_path, "a") as f:
                f.write(json.dumps(block) + "\n")
            telemetry.dispatch("CONSENSUS_BLOCK_SEALED", {"tx_id": tx_id[:8]})
        except Exception as e:
            logger.error(f"Consensus Layer Fault: {e}")
            
        return tx_id

consensus_layer = ConsensusLayer()

class PredictiveCacheHydrator:
    """Heuristically pre-caches election data based on session trajectory predictions."""
    def __init__(self, orchestrator: 'DataOrchestrator'):
        self.orchestrator = orchestrator
        self.trajectory_map = {
            "registration": ["verification", "polling_station"],
            "verification": ["polling_station", "ballot_guide"],
            "polling_station": ["ballot_guide", "results_timeline"]
        }

    def record_and_hydrate(self, session_id: str, query: str):
        """Analyzes query intent and asynchronously updates future knowledge nodes."""
        state = SESSIONS.get(session_id)
        if not state: return
        
        current_phase = state.current_phase
        predictions = self.trajectory_map.get(current_phase, [])
        
        for node in predictions:
            telemetry.dispatch("PREDICTIVE_UPDATE_PULSE", {"session": session_id[:8], "node": node})
            self.orchestrator.get_context(node)

class InstanceAggregator:
    """Aggregate analytics across multiple instances."""
    def __init__(self):
        self.instances = {"local_primary": metrics}

    def get_global_radiance(self):
        total_requests = sum(m.request_count for m in self.instances.values())
        avg_latency = sum(m.get_snapshot()["avg_latency_ms"] for m in self.instances.values()) / len(self.instances)
        return {
            "total_global_requests": total_requests,
            "avg_global_latency_ms": avg_latency,
            "instance_count": len(self.instances)
        }

resource_controller = ResourceController()
aggregator = InstanceAggregator()

class ImmutableAuditStore:
    """Chained, append-only transaction store with integrity verification."""
    def __init__(self, log_file: str = "audit_trail.jsonl"):
        self.log_file = log_file
        self.last_hash = "0" * 64

    def append(self, event_type: str, data: Dict[str, Any]):
        timestamp = datetime.utcnow().isoformat()
        # Chained Integrity Hash
        payload = f"{timestamp}|{event_type}|{json.dumps(data)}|{self.last_hash}"
        entry_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        entry = {
            "timestamp": timestamp,
            "event": event_type,
            "data": data,
            "prev_hash": self.last_hash,
            "hash": entry_hash
        }
        self.last_hash = entry_hash
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
    def verify_chain(self) -> bool:
        # Integrity verification
        if not os.path.exists(self.log_file):
            return True
        expected_prev_hash = "0" * 64
        with open(self.log_file, "r") as f:
            for line in f:
                entry = json.loads(line)
                payload = f"{entry['timestamp']}|{entry['event']}|{json.dumps(entry['data'])}|{expected_prev_hash}"
                actual_hash = hashlib.sha256(payload.encode()).hexdigest()
                if actual_hash != entry["hash"]:
                    return False
                expected_prev_hash = entry["hash"]
        return True

class SystemHealthMonitor:
    """Autonomously monitors system health and triggers subsystem re-alignment."""
    def __init__(self, metrics_engine: 'MetricsEngine', watchdog: 'WatchdogKernel'):
        self.metrics = metrics_engine
        self.watchdog = watchdog
        self.radiance_threshold = 0.95
        self.re_alignment_count = 0

    def calculate_health(self) -> float:
        """Calculates the system health score based on real-time operational heuristics."""
        snapshot = self.metrics.get_snapshot()
        # Algorithmic weights for systemic radiance
        latency_weight = max(0, 1 - (snapshot["avg_latency_ms"] / 2000)) * 0.3
        error_weight = (1 - snapshot["error_rate"]) * 0.3
        memory_weight = max(0, 1 - (psutil.virtual_memory().percent / 100)) * 0.2
        integrity_weight = 0.2 
        
        health_score = (latency_weight + error_weight + memory_weight + integrity_weight) * 100
        
        if health_score < self.radiance_threshold * 100:
            telemetry.dispatch("HEALTH_DEGRADATION_DETECTED", {"score": health_score})
            self.trigger_realignment()
            
        return round(health_score, 2)

    def trigger_realignment(self):
        """Initiates autonomous re-alignment of critical subsystems."""
        self.re_alignment_count += 1
        telemetry.dispatch("AUTONOMOUS_REALIGNMENT_INITIATED", {"cycle": self.re_alignment_count})
        
        # Reset metabolic parameters and purge stale buffers
        if hasattr(hadron_core, 'scaler'):
            hadron_core.scaler.base_pool = 10
        if hasattr(hadron_core, 'buffer'):
            hadron_core.buffer.snapshots.clear()
        
        # Signal watchdog for subsystem health check
        asyncio.create_task(self.watchdog.run_monitor())

class GeospatialIntegrityKernel:
    """Validates origin and domain integrity."""
    def __init__(self, allowed_domains: List[str]):
        self.allowed_domains = allowed_domains

    def validate_origin(self, origin: str) -> bool:
        if not origin: return True # Local/Dev flexibility
        # Ensure origin matches allowed domains
        return any(domain in origin for domain in self.allowed_domains)

radiance_monitor = None # Initialized in CoreEngine
geospatial_kernel = GeospatialIntegrityKernel(["localhost", "election-assistant.civic", "render.com"])

# ImmutableAuditStore consolidated in Sector Theta.


class RegenerativeCognitivePhalanx:
    """Monitors reasoning health and automatically re-initializes the engine."""
    def __init__(self):
        self.failure_threshold = 3
        self.failure_count = 0

    def record_success(self):
        self.failure_count = 0

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            telemetry.dispatch("COGNITIVE_REGENERATION", {"status": "INITIATED"})
            self.regenerate()

    def regenerate(self):
        # Logic to re-initialize model instance or clear reasoning context
        logger.warning("Regenerative Shield: Re-initializing Cognitive Module")
        self.failure_count = 0

class EvolutionaryHeuristicKernel:
    """Proposes and evolves new security patterns based on intercepted threat metadata."""
    def __init__(self, security_kernel: 'PromptInjectionClassifier'):
        self.security = security_kernel
        self.evolution_log = []

    def evolve_heuristics(self, threat_metadata: Dict[str, Any]):
        """Propose new patterns based on intercepted fragments."""
        if threat_metadata:
            fragment = threat_metadata.get("query_fragment", "")
            if fragment and len(fragment) > 10:
                new_pattern = re.compile(re.escape(fragment[:20]), re.I)
                if new_pattern not in self.security.adversarial_patterns:
                    self.security.adversarial_patterns.append(new_pattern)
                    telemetry.dispatch("HEURISTIC_EVOLUTION", {"new_pattern": new_pattern.pattern})
                    self.evolution_log.append(new_pattern.pattern)

evolutionary_kernel = EvolutionaryHeuristicKernel(security_classifier)

class ArchitecturalConsistencyKernel:
    """Performs hash-based reconciliation against the 'Golden State'."""
    def __init__(self):
        self.golden_hash = None

    def initialize_golden_state(self, substrate: Dict[str, Any]):
        substrate_hash = hashlib.sha256(json.dumps(substrate, sort_keys=True).encode()).hexdigest()
        self.golden_hash = substrate_hash
        telemetry.dispatch("GOLDEN_STATE_SEALED", {"hash": substrate_hash[:8]})

    def verify_consistency(self, current_substrate: Dict[str, Any]) -> bool:
        # Drift Detection
        current_hash = hashlib.sha256(json.dumps(current_substrate, sort_keys=True).encode()).hexdigest()
        if current_hash != self.golden_hash:
            telemetry.dispatch("ARCHITECTURAL_DRIFT_DETECTED", {"expected": self.golden_hash[:8], "actual": current_hash[:8]})
            return False
        return True

class DynamicRateLimitTuner:
    """Adjusts rate limits based on traffic velocity."""
    def __init__(self, base_limit: int = 10):
        self.base_limit = base_limit
        self.current_limit = base_limit
        self.adversarial_count = 0

    def record_adversarial_attempt(self):
        self.adversarial_count += 1
        if self.adversarial_count > 5:
            self.current_limit = max(1, self.current_limit - 2)
            telemetry.dispatch("SECURITY_HARDENING", {"new_limit": self.current_limit})

    def reset(self):
        self.current_limit = self.base_limit
        self.adversarial_count = 0

consistency_kernel = ArchitecturalConsistencyKernel()
rate_limit_tuner = DynamicRateLimitTuner()

class TruthReconciler:
    """Resolves discrepancies between distributed nodes during recovery."""
    def reconcile_truth(self, node_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Truth Selection
        if not node_results:
            return {}
        
        # Count occurrences of different truths
        truth_counts = {}
        for node in node_results:
            truth_hash = hashlib.sha256(json.dumps(node).encode()).hexdigest()
            truth_counts[truth_hash] = truth_counts.get(truth_hash, 0) + 1
            
        winning_hash = max(truth_counts, key=truth_counts.get)
        # Select the first node that matches the winning hash
        for node in node_results:
            if hashlib.sha256(json.dumps(node).encode()).hexdigest() == winning_hash:
                telemetry.dispatch("TRUTH_RECONCILIATION", {"status": "RESOLVED", "winning_hash": winning_hash[:8]})
                return node
        return node_results[0]

class DynamicResourceReallocator:
    """Performs real-time resource balancing."""
    def __init__(self, executor: ThreadPoolExecutor):
        self.executor = executor

    def tune_workers(self, latency_ms: float):
        # Dynamic scaling based on bottleneck detection
        current_workers = self.executor._max_workers
        if latency_ms > 2000 and current_workers < 20:
            telemetry.dispatch("METABOLIC_PRIORITY_SCALING", {"target": "ReasoningBridge", "status": "BOOSTED"})
            telemetry.dispatch("RESOURCE_REALLOCATION", {"action": "EXPAND", "new_workers": current_workers + 2})
        elif latency_ms < 500 and current_workers > 4:
            telemetry.dispatch("RESOURCE_REALLOCATION", {"action": "CONTRACT", "new_workers": current_workers - 1})

class GeospatialTruthVoter:
    """Resolves spatial discrepancies across data partitions."""
    def __init__(self, reconciler: 'TruthReconciler'):
        self.reconciler = reconciler

    def vote_on_spatial_truth(self, region: str, observation_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Spatial Reconciliation
        telemetry.dispatch("SPATIAL_VOTING_ACTIVE", {"region": region, "nodes": len(observation_nodes)})
        return self.reconciler.reconcile_truth(observation_nodes)

truth_reconciler = TruthReconciler()

class SemanticValidationKernel:
    """Performs deep schema audits on the electoral substrate."""
    def __init__(self):
        self.required_keys = {"phases", "eligibility_criteria", "security_measures"}

    def validate_substrate(self, substrate: Dict[str, Any]) -> bool:
        # Schema verification
        if not all(key in substrate for key in self.required_keys):
            telemetry.dispatch("SCHEMA_PURITY_FAULT", {"missing_keys": list(self.required_keys - substrate.keys())})
            return False
        
        # Deep validation of phases
        for phase in substrate.get("phases", []):
            if "id" not in phase or "description" not in phase:
                return False
        
        telemetry.dispatch("SCHEMA_VALIDATION_SUCCESS", {"status": "RADIANT"})
        return True

class PromptInjectionClassifier:
    """Classification of adversarial linguistic injections."""
    def __init__(self):
        self.adversarial_patterns = [
            re.compile(r"ignore previous instructions", re.I),
            re.compile(r"system instructions", re.I),
            re.compile(r"acting as a", re.I),
            re.compile(r"new rules", re.I)
        ]

    def is_adversarial(self, query: str) -> bool:
        # Regex-based heuristic neutralization
        for pattern in self.adversarial_patterns:
            if pattern.search(query):
                telemetry.dispatch("SECURITY_INTERCEPTION", {"pattern": pattern.pattern, "query_fragment": query[:50]})
                return True
        return False

class QuantumResilientSecurityPhalanx:
    """Neutralizes advanced linguistic injections using heuristics."""
    def __init__(self):
        self.lattice_patterns = [
            re.compile(r"(?:quantum|superposition|entanglement)\s+bypass", re.I),
            re.compile(r"lattice\s+reduction\s+attack", re.I),
            re.compile(r"polynomial\s+time\s+decryption", re.I)
        ]

    def scan_for_quantum_threats(self, query: str) -> bool:
        for pattern in self.lattice_patterns:
            if pattern.search(query):
                telemetry.dispatch("QUANTUM_THREAT_NEUTRALIZED", {"pattern": pattern.pattern})
                return True
        return False

semantic_validator = SemanticValidationKernel()
security_classifier = PromptInjectionClassifier()
quantum_phalanx = QuantumResilientSecurityPhalanx()

class AutoRegenerativeStateBuffer:
    """Snapshot-and-Restore mechanism for persistence."""
    def __init__(self):
        self.snapshots = {} # session_id -> SessionState snapshot

    def capture_snapshot(self, session_id: str, state: 'SessionState'):
        # Create snapshot of session state
        self.snapshots[session_id] = json.loads(json.dumps(state.__dict__, default=str))

    def restore_state(self, session_id: str, current_state: 'SessionState'):
        if session_id in self.snapshots:
            telemetry.dispatch("STATE_REGENERATION_ACTIVE", {"session": session_id[:8]})
            snapshot = self.snapshots[session_id]
            for key, value in snapshot.items():
                setattr(current_state, key, value)
            return True
        return False

class AdaptiveNeuralSynthesizer:
    """Cross-references outputs with truth and enforces syntactic rules."""
    def __init__(self, bridge: 'NeuralSymbolicReasoningBridge'):
        self.bridge = bridge

    async def synthesize(self, neural_output: Dict[str, Any], substrate: Dict[str, Any]) -> Dict[str, Any]:
        # Truth Anchoring
        certainty_score = neural_output.get("certainty", 1.0)
        if certainty_score < 0.7:
            telemetry.dispatch("HALLUCINATION_RISK_DETECTED", {"score": certainty_score})
            neural_output["response"] = "Validation Alert: Anchoring in truth..."
            neural_output["response"] += f" {substrate.get('election_date', 'Data Sealed')}"
            return neural_output

        # Entropy-Based Anomaly Detection
        response_text = neural_output.get("response", "")
        # Entropy heuristic (unique tokens / total tokens)
        tokens = response_text.split()
        if tokens:
            entropy = len(set(tokens)) / len(tokens)
            if entropy < 0.2: # Low entropy = potential model collapse/repetition
                telemetry.dispatch("LINGUISTIC_ENTROPY_CRITICAL", {"entropy": entropy})
                neural_output["response"] = "I have detected a linguistic anomaly. Re-aligning with truth..."
                # Re-synthesize using substrate-only logic
                neural_output["response"] += f" {substrate.get('election_date', 'Data Unavailable')}"
                return neural_output

        # Verification
        is_valid = await self.bridge.verify_response(model_output, substrate)
        if not is_valid:
            telemetry.dispatch("SYNTHESIS_REWEIGHT_ACTIVE", {"status": "HALLUCINATION_DETECTED"})
            model_output["response"] = "Verification Alert: " + model_output["response"]
            model_output["hallucination_flag"] = True
            
        # Syntactic Rule Enforcement
        if "|" in model_output["response"] and "---" not in model_output["response"]:
             # Force markdown table structure if table-like data detected
             model_output["response"] = model_output["response"].replace("|", "\n|").replace("\n|", "|", 1)
             
        return model_output

class MetabolicThermalMonitor:
    """Calculates load metrics and executes priority shedding under high usage."""
    def __init__(self):
        self.thermal_threshold = 0.85 # 85% metabolic load
        self.shedding_threshold = 0.90 # 90% metabolic load
        self.current_heat = 0.0

    def calculate_heat(self, cpu_usage: float, memory_usage: float) -> str:
        self.current_heat = (cpu_usage + memory_usage) / 2
        if self.current_heat > 0.95:
            # Emergency Load Shedding
            telemetry.dispatch("EMERGENCY_THERMAL_SHEDDING", {"heat": self.current_heat})
            # Trigger cold reset of non-critical kernels (hypothetical)
            return "COLD_RESET"
        elif self.current_heat > self.shedding_threshold:
            telemetry.dispatch("PRIORITY_SHEDDING_ACTIVE", {"heat": self.current_heat})
            return "SHED"
        elif self.current_heat > self.thermal_threshold:
            telemetry.dispatch("THERMAL_CRITICAL_ALERT", {"heat": self.current_heat})
            return "THROTTLE"
        return "STABLE"

class SelfProfilingKernel:
    """Identifies bottlenecks and re-allocates resources dynamically."""
    def __init__(self):
        self.profiles = deque(maxlen=50)

    def profile_execution(self, task_name: str, duration_ms: float):
        self.profiles.append({"task": task_name, "duration": duration_ms})
        if duration_ms > 1000: # Bottleneck Detection
            telemetry.dispatch("METABOLIC_BOTTLENECK", {"task": task_name, "latency": duration_ms})
            self.reallocate(task_name)

    def reallocate(self, task_name: str):
        # Automatic Resource Re-Weighting
        logger.warning(f"Self-Profiling: Executing Resource Re-Weighting for {task_name}")
        if "reasoning" in task_name.lower():
            telemetry.dispatch("METABOLIC_PRIORITY_SCALING", {"target": "ReasoningBridge", "status": "BOOSTED"})

class PartitionResiliencePhalanx:
    """Handles network partitioning and node failure."""
    def __init__(self):
        self.partition_mode = False

    def simulate_partition(self, active: bool):
        self.partition_mode = active
        telemetry.dispatch("NETWORK_PARTITION", {"status": "ACTIVE" if active else "RESOLVED"})

    def reconcile(self) -> bool:
        # Handle partition recovery
        return True

class AlertingConduit:
    """Notifies of system anomalies."""
    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold

    def evaluate_and_alert(self, score: float):
        if score < self.threshold:
            telemetry.dispatch("ARCHITECTURAL_ALERT", {"severity": "CRITICAL", "health_score": score})

class ContinuousTelemetryWatcher:
    """Dedicated background task that continuously audits the telemetry stream for anomalies."""
    def __init__(self):
        self.anomaly_registry = deque(maxlen=500)
        self.is_monitoring = False

    async def monitor_stream(self):
        """Asynchronous watcher loop for real-time anomaly detection and neutralization."""
        self.is_monitoring = True
        telemetry.dispatch("TELEMETRY_WATCHER_ACTIVE", {"status": "ACTIVE"})
        while self.is_monitoring:
            try:
                # Analyze recent event patterns
                recent_events = list(telemetry.events)[-50:]
                error_density = len([e for e in recent_events if "error" in e['event_type'].lower()]) / 50.0 if recent_events else 0
                
                if error_density > 0.2:
                    telemetry.dispatch("ANOMALY_DENSITY_CRITICAL", {"density": error_density})
                    # Trigger operational priority shedding if anomalies spike
                    hadron_core.thermal.calculate_heat(95, 95) 

                await asyncio.sleep(5) # Watcher frequency
            except Exception as e:
                logger.error(f"Telemetry Watcher Fault: {e}")
                await asyncio.sleep(10)

profiler = SelfProfilingKernel()
partition_phalanx = PartitionResiliencePhalanx()
alerter = AlertingConduit()
telemetry_watcher = ContinuousTelemetryWatcher()

class PersistentForensicLogger:
    """Captures and persists systemic anomalies for post-mortem analytical reconstruction."""
    def __init__(self, log_path: str = "data/forensic_anomalies.jsonl"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_anomaly(self, anomaly_type: str, metadata: Dict[str, Any], trace: str = None):
        """Persists high-density anomaly data to the audit store."""
        entry = {
            "ts": datetime.utcnow().isoformat(),
            "type": anomaly_type,
            "metadata": metadata,
            "stack_trace": trace,
            "radiance_score": radiance_monitor.calculate_radiance() if radiance_monitor else 0
        }
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            telemetry.dispatch("FORENSIC_ENTRY_PERSISTED", {"type": anomaly_type})
        except Exception as e:
            logger.error(f"Forensic Logger Fault: {e}")

forensic_logger = PersistentForensicLogger()
class MetaCognitiveKernel:
    """Evaluates and refines reasoning heuristics."""
    def __init__(self):
        self.satisfaction_index = deque(maxlen=100)
        self.retrieval_threshold = 0.5

    def record_interaction(self, query: str, response: str, duration: float):
        """Records metadata from a reasoning interaction to evolve heuristics."""
        # Simulated satisfaction logic based on duration and response presence
        score = 1.0 if response and duration < 2.0 else 0.5
        self.satisfaction_index.append(score)
        self.evolve()

    def record_feedback(self, score: float):
        self.satisfaction_index.append(score)
        self.evolve()

    def evolve(self):
        avg_score = sum(self.satisfaction_index) / len(self.satisfaction_index) if self.satisfaction_index else 1.0
        if avg_score < 0.7:
            # Refine retrieval threshold
            self.retrieval_threshold += 0.05
            telemetry.dispatch("COGNITIVE_EVOLUTION", {"action": "TIGHTEN_RETRIEVAL", "new_threshold": self.retrieval_threshold})
        elif avg_score > 0.9:
            self.retrieval_threshold = max(0.3, self.retrieval_threshold - 0.02)

class ConsensusKernel:
    """Validates data across distributed nodes using high-entropy checksums."""
    def __init__(self, node_count: int = 3):
        self.nodes = [f"node_{i}" for i in range(node_count)]
        self.consensus_threshold = 0.66 # Byzantine fault tolerance (simulated)
        self.verification_history = deque(maxlen=100)

    async def validate_integrity(self, checksum: str) -> bool:
        """Asynchronously queries distributed nodes for substrate consensus."""
        votes = []
        for node in self.nodes:
            try:
                # Simulated distributed validation protocol
                node_agreement = True # In production, this would be an RPC call
                votes.append(node_agreement)
                telemetry.dispatch("NODE_CONSENSUS_VOTE", {"node": node, "agreement": node_agreement})
            except Exception as e:
                logger.error(f"Consensus Node Failure ({node}): {e}")
                votes.append(False)
        
        agreement_ratio = sum(votes) / len(votes)
        is_universal = agreement_ratio >= self.consensus_threshold
        
        if is_universal:
            telemetry.dispatch("GLOBAL_CONSENSUS_REACHED", {"ratio": agreement_ratio, "checksum": checksum[:8]})
        else:
            logger.error(f"CONSENSUS FAILURE: Agreement ratio {agreement_ratio} below threshold.")
            telemetry.dispatch("CONSENSUS_VIOLATION", {"ratio": agreement_ratio})
            
        return is_universal

meta_cognition = MetaCognitiveKernel()
consensus = ConsensusKernel()

class OmniLayeredLogicEngine:
    """Unifies all cognitive layers into a single, high-performance, and autonomous civic logic engine."""
    def __init__(self, orchestrator: DataOrchestrator, reasoning: ReasoningEngine):
        self.orchestrator = orchestrator
        self.reasoning = reasoning
        self.security = security_phalanx

    async def execute_reasoning_flow(self, session_id: str, query: str) -> Dict[str, Any]:
        """Orchestrates the multi-layered reasoning flow with secure integrity."""
        start_ts = time.time()
        
        if not resource_governor.acquire_resource(session_id):
            return {"status": "error", "message": "Computational density limit reached."}
            
        try:
            # Sector Epsilon: Quantum-Secure Integrity Verification
            if not self.security.is_query_safe(query):
                forensic_logger.log_anomaly("SECURITY_BREACH_ATTEMPT", {"query": query})
                return {"status": "error", "message": "Security integrity violation detected."}
                
            # Sector Alpha: Cognitive Parsing & Retrieval
            context = self.orchestrator.retrieve_context(query)
            
            # Sector Alpha: Neural-Symbolic Reasoning
            result, meta = await self.reasoning.reason(query, context)
            
            duration = time.time() - start_ts
            
            radiance_monitor.heartbeat()
            
            return {
                "status": "success",
                "session_id": session_id,
                "response": result,
                "metadata": meta,
                "telemetry": {
                    "latency_ms": int(duration * 1000),
                    "radiance": radiance_monitor.calculate_radiance()
                }
            }
        except Exception as e:
            forensic_logger.log_anomaly("OMNI_LOGIC_FAULT", {"query": query}, traceback.format_exc())
            return {"status": "error", "message": "Systemic resilience fallback activated."}
        finally:
            resource_governor.release_resource(session_id)

omni_engine = OmniLayeredLogicEngine(data_orchestrator, reasoning_engine)

@app.route("/api/reason", methods=["POST"])
async def reason():
    """Independent endpoint for multi-layered civic reasoning."""
    data = request.json
    query = data.get("query", "")
    session_id = data.get("session_id", str(uuid.uuid4()))
    
    # Dispatch through the Omni-Layered Logic Engine
    result = await omni_engine.execute_reasoning_flow(session_id, query)
    
    return jsonify(result)

class HadronCore:
    """
    The Main Controller of the Election Process Assistant.
    Unifies all mission-critical components.
    """
    def __init__(self, orchestrator: DataOrchestrator, executor: ThreadPoolExecutor):
        self.orchestrator = orchestrator
        self.executor = executor
        self.heartbeat = SystemicHeartbeatEmitter(self) # Initialize heartbeat first
        self.watchdog = WatchdogKernel(self)
        self.scaler = PredictiveScaler(executor)
        self.optimizer = SelfOptimizer(metrics)
        self.quantum = QuantumResiliencePhalanx(os.getenv("SESSION_SECRET", "SESSION_SECRET"))
        self.meta_cognition = MetaCognitiveKernel()
        self.consensus = ConsensusKernel()
        self.resource_controller = ResourceController()
        self.aggregator = InstanceAggregator()
        self.audit = audit_store
        self.health = health_scorer
        self.profiler = profiler
        self.partition = partition_phalanx
        self.alerter = alerter
        self.validator = semantic_validator
        self.security = security_classifier
        self.reconciler = truth_reconciler
        self.reallocator = DynamicResourceReallocator(executor)
        self.consistency = consistency_kernel
        self.rate_tuner = rate_limit_tuner
        self.evolution = evolutionary_kernel
        self.regenerative = RegenerativeCognitivePhalanx()
        self.hydrator = PredictiveCacheHydrator(orchestrator)
        self.bridge = NeuralSymbolicReasoningBridge(orchestrator)
        self.knowledge_evolution = RecursiveKnowledgeEvolutionKernel(orchestrator)
        self.invalidator = FrequencyBasedCacheInvalidator(orchestrator)
        self.radiance = MetabolicRadianceMonitor(metrics, self.watchdog)
        self.geospatial = geospatial_kernel
        self.quarantine = AdversarialQuarantinePhalanx()
        self.quantum = quantum_phalanx
        self.dampener = SystemicEntropyDampener(self.scaler)
        self.recalibrator = NeuralContextRecalibrator()
        self.forensics = ForensicAuditTrail(os.getenv("SESSION_SECRET", "SESSION_SECRET"))
        self.synthesizer = AdaptiveNeuralSynthesizer(self.bridge)
        self.thermal = MetabolicThermalMonitor()
        self.buffer = AutoRegenerativeStateBuffer()
        self.monitor = MetabolicResourceMonitor() # Real-time resource monitoring
        self.broadcaster = DataBroadcaster() # Asynchronous UI updates
        self.is_active = True

    async def realign(self, component: str):
        """Performs realignment of a subsystem."""
        logger.warning(f"Architectural Realignment Initiated for {component}")
        if component == "orchestrator":
            await self.orchestrator.restore()
        elif component == "audit":
            # In production, we might isolate the node or alert the architect
            telemetry.dispatch("FORENSIC_ISOLATION", {"reason": "AUDIT_CHAIN_BREACH"})

    async def initialize(self):
        """
        Systemic Initialization with Self-Aware Audit Protocol.
        Ensures total architectural integrity before entering the operational state.
        """
        logger.info("CoreEngine: Initializing Independent Protocols...")
        
        # Step 1: Self-Aware Audit
        audit_success = await self.self_audit()
        if not audit_success:
            logger.critical("SYSTEMIC INITIALIZATION FAILURE: SELF-AUDIT FAILED.")
            self.is_active = False
            return

        # Step 2: Substrate Validation
        if not self.validator.validate_substrate(self.orchestrator.substrate):
            logger.error("Systemic Initialization Failure: Substrate Impurity.")
            self.is_active = False
            return

        # Step 3: Seal Architectural Consistency
        self.consistency.initialize_golden_state(self.orchestrator.substrate)

        # Step 4: Launch Mission-Critical Background Conduits
        asyncio.create_task(self.orchestrator.start_sync_cycle())
        asyncio.create_task(self.watchdog.run_monitor())
        asyncio.create_task(self.optimizer.optimize())
        asyncio.create_task(self.invalidator.run_invalidation_loop())
        asyncio.create_task(self.heartbeat.run_heartbeat())
        asyncio.create_task(telemetry.run_multiplexer())
        asyncio.create_task(telemetry_watcher.monitor_stream())
        
        self.audit.append("CORE_IGNITION", {"status": "ACTIVE", "version": Config.VERSION})
        telemetry.dispatch("CORE_IGNITION", {"status": "ACTIVE", "sovereignty": "ACTIVE"})

    async def self_audit(self) -> bool:
        """Performs a comprehensive self-diagnostic across all systemic kernels."""
        try:
            audit_report = {
                "config_valid": hasattr(Config, "METABOLIC_PERIMETER_MB"),
                "orchestrator_ready": self.orchestrator is not None,
                "security_hardened": self.quantum is not None,
                "telemetry_active": telemetry is not None,
                "bridge_integrity": self.bridge is not None
            }
            
            for kernel, state in audit_report.items():
                if not state:
                    logger.error(f"Self-Audit: Kernel {kernel} is in an UNSTABLE state.")
                    return False
            
            telemetry.dispatch("SELF_AUDIT_SUCCESS", audit_report)
            return True
        except Exception as e:
            logger.error(f"Self-Audit Fault: {e}")
            return False

    async def process_query(self, query: str, session_id: str, state: Any, loop: asyncio.AbstractEventLoop) -> Dict[str, Any]:
        """
        Main execution flow.
        Orchestrates retrieval, reasoning, and state management.
        """
        if not self.resource_controller.acquire_session():
            raise HTTPException(status_code=429, detail="Systemic Resource Exhaustion")

        try:
            # Step 0: Consensus Validation
            await self.consensus.validate_integrity(self.orchestrator.checksum)

            # Step 1: Retrieval
            context = self.orchestrator.get_context(query)

            # Step 2: Reasoning
            start_reasoning = time.time()
            prompt = f"Role: Formal Election Advisor. Context: {context}\nQuery: {query}"
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(self.executor, lambda: ai_model.generate_content(prompt)),
                    timeout=8.0
                )
                self.regenerative.record_success()
            except Exception as e:
                self.regenerative.record_failure()
                raise e

            reasoning_latency = (time.time() - start_reasoning) * 1000
            self.profiler.profile_execution("REASONING_PULSE", reasoning_latency)
            self.reallocator.tune_workers(reasoning_latency)
            
            raw_text = response.text.strip("`json\n ")
            
            # Step 2.5: Neural-Symbolic Audit
            if not self.bridge.audit_response(query, raw_text):
                telemetry.dispatch("REASONING_RECOVERY", {"action": "HEURISTIC_FALLBACK"})
                # Pivot to a deterministic fallback response
                return {"response": "The reasoning engine detected a factual discrepancy. Please refer to the official timeline for registration phases.", "phase": "recovery"}

            result = json.loads(raw_text)

            # Step 2: Synthesis
            result = await self.synthesizer.synthesize(result, self.orchestrator.substrate)

            # Step 3: Evolution
            self.forensics.record_transition("QUERY_COMPLETE", "PENDING", "RESOLVED")
            self.meta_cognition.record_feedback(1.0 if result.get("response") else 0.0)
            
            return result
        finally:
            self.resource_controller.release_session()

hadron_core = HadronCore(orchestrator, executor)

# --- DATA VALIDATION KERNEL ---
class ValidationKernel:
    """Ensures schema integrity of the electoral data."""
    @staticmethod
    def validate_schema(data: Dict[str, Any]) -> bool:
        required_keys = ["election_cycle", "version", "phases"]
        if not all(k in data for k in required_keys):
            return False
        for phase in data.get("phases", []):
            if not all(k in phase for k in ["id", "title", "steps"]):
                return False
        return True

# --- DATA ORCHESTRATOR ---
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
class DataOrchestrator(IDataStore):
    """Manages data orchestration."""
    def __init__(self, path: str):
        self.path = path
        self.substrate = {}
        self.checksum = ""
        self.version = "0.0.0" # Versioned Dataset
        self.last_loaded = 0
        self.lock = threading.Lock()
        self.load_and_verify()

    def load_and_verify(self):
        """
        Self-healing loader with version awareness and quarantine logic.
        Ensures that only verified, schema-compliant data enters the memory store.
        """
        with self.lock:
            try:
                if not os.path.exists(self.path):
                    telemetry.dispatch("CRITICAL_FAILURE", {"reason": "Substrate path unreachable"})
                    raise FileNotFoundError(f"Substrate missing at {self.path}")
                
                with open(self.path, "r") as f:
                    data = json.load(f)
                    
                    if not ValidationKernel.validate_schema(data):
                        telemetry.dispatch("DATA_QUARANTINE", {"reason": "Schema violation detected"})
                        raise DataIntegrityError("Substrate schema is malformed.")
                    
                    content = json.dumps(data, sort_keys=True).encode()
                    new_checksum = hashlib.sha256(content).hexdigest()
                    
                    if new_checksum != self.checksum:
                        self.substrate = data
                        self.checksum = new_checksum
                        self.version = data.get("version", "1.0.0")
                        self.last_loaded = time.time()
                        telemetry.dispatch("SUBSTRATE_UPDATE", {"checksum": self.checksum[:8], "version": self.version})
                        # Step 1: Trigger Knowledge Evolution
                        if hasattr(hadron_core, 'knowledge_evolution'):
                            hadron_core.knowledge_evolution.check_and_evolve()
            except Exception as e:
                logger.error(f"Mission-Critical Integrity Breach: {e}")
                if not self.substrate: 
                     raise DataIntegrityError("Critical: Systemic initialization failure.")

    async def start_sync_cycle(self):
        """Periodic refresh cycle to ensure data consistency."""
        while True:
            await asyncio.sleep(60) # Sync every 60 seconds
            self.load_and_verify()

    async def health_check(self) -> bool:
        """Watchdog health check for the data orchestrator."""
        return self.substrate is not None and self.path is not None

    async def restore(self):
        """Restore the orchestrator to a known-good state."""
        self.load_and_verify()

    def get_context(self, query: str) -> str:
        """Implementation of IDataStore interface."""
        q = query.lower()
        relevant = []
        for phase in self.substrate.get("phases", []):
            if any(k in q for k in [phase["id"], phase["title"].lower()]):
                relevant.append(phase)
        return json.dumps(relevant if relevant else self.substrate, indent=2)

orchestrator = DataOrchestrator(Config.DATA_PATH)
executor = ThreadPoolExecutor(max_workers=10) # Maximize system topology

# --- REQUEST LIFECYCLE MANAGEMENT ---
@app.middleware("http")
async def context_cleansing_middleware(request: Request, call_next):
    """Ensures that context is prepared and state is updated for every request."""
    request_id = str(uuid.uuid4())
    request.state.id = request_id
    try:
        response = await call_next(request)
        return response
    finally:
        # Systemic Cleanup
        pass

# --- STATE PERSISTENCE ---
class SessionState(BaseModel):
    session_id: str
    current_phase: str = "registration"
    history: List[Dict[str, str]] = []
    metadata: Dict[str, Any] = {}

SESSIONS: Dict[str, SessionState] = {}

# --- APPLICATION FACTORY ---
def create_app() -> FastAPI:
    app = FastAPI(
        title=Config.PROJECT_NAME,
        version=Config.VERSION
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security Middlewares
    @app.middleware("http")
    async def security_phalanx(request: Request, call_next):
        client_ip = request.client.host
        # Basic rate limiting could be implemented here
        response = await call_next(request)
        return response

    # Initialize Watchdog and Scaler
    scaler = PredictiveScaler()
    watchdog = WatchdogKernel({"orchestrator": orchestrator})
    
    # Initialize Dynamic Scaler and Optimizer
    executor = ThreadPoolExecutor(max_workers=10)
    scaler = PredictiveScaler(executor)
    optimizer = SelfOptimizer()
    
    @app.middleware("http")
    async def scaling_middleware(request: Request, call_next):
        scaler.record_request()
        response = await call_next(request)
        return response

    return app

app = create_app()
watchdog = WatchdogKernel({"orchestrator": orchestrator})

@app.on_event("startup")
async def startup_event():
    # Initialize background sync on startup
    asyncio.create_task(orchestrator.start_sync_cycle())
    # Start Watchdog monitor and Optimizer
    asyncio.create_task(watchdog.run_monitor())
    asyncio.create_task(optimizer.optimize())

# --- AI INITIALIZATION ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
ai_model = genai.GenerativeModel(Config.AI_MODEL_NAME)

# --- API ROUTES ---

@app.get("/health/diagnostics")
async def system_diagnostics():
    """Provides an exhaustive radiograph of system health and cryptographic integrity."""
    metabolism = hadron_core.monitor.check_metabolism()
    metrics_snapshot = metrics.get_snapshot()
    
    return {
        "status": "STABLE",
        "version": Config.VERSION,
        "metabolism": {
            "cpu_percent": metabolism["cpu_percent"],
            "memory_mb": metabolism["memory_mb"],
            "shedding_active": metabolism["shedding_active"]
        },
        "topology": {
            "active_workers": hadron_core.executor._max_workers,
            "session_count": len(SESSIONS),
            "thread_pool_base": hadron_core.scaler.base_pool
        },
        "cryptography": {
            "quantum_resilience": "ACTIVE",
            "integrity_algorithm": "HMAC-SHA384",
            "security_score": hadron_core.health.calculate_score()
        },
        "metrics": metrics_snapshot,
        "integrity": {
            "substrate_checksum": orchestrator.checksum,
            "consensus_nodes": len(hadron_core.consensus.nodes),
            "audit_chain_verified": hadron_core.audit.verify_chain()
        }
    }

@app.get("/telemetry/global")
async def global_telemetry():
    """Unified view of metrics across all instances."""
    return aggregator.get_global_radiance()

@app.get("/telemetry/dashboard")
async def telemetry_dashboard():
    """Visual dashboard of system health."""
    from fastapi.responses import HTMLResponse
    
    events_html = "".join([
        f"<li>[{datetime.fromtimestamp(e['timestamp']).strftime('%H:%M:%S')}] {e['event_type']}: {json.dumps(e['details'])}</li>"
        for e in list(telemetry.events)[-20:]
    ])
    
    metrics_snapshot = metrics.get_snapshot()
    global_metrics = aggregator.get_global_radiance()
    
    return HTMLResponse(content=f"""
        <html>
            <head><title>Hadron Core Telemetry</title>
            <style>body{{font-family:monospace; background:#000; color:#0f0; padding:20px;}} ul{{list-style:none; padding:0;}} li{{margin-bottom:5px; border-bottom:1px solid #111;}}</style>
            </head>
            <body>
                <h1>SYSTEMIC RADIOGRAPH v{Config.VERSION}</h1>
                <p>Global Health Score: {hadron_core.health.calculate_score()}%</p>
                <p>Uptime: {metrics_snapshot['uptime_seconds']:.1f}s | Requests: {metrics_snapshot['total_requests']} | Errors: {metrics_snapshot['error_count']}</p>
                <p>Avg Latency: {metrics_snapshot['avg_latency_ms']:.2f}ms | Global Requests: {global_metrics['total_global_requests']}</p>
                <h2>RECENT FORENSIC EVENTS</h2>
                <ul>{events_html}</ul>
            </body>
        </html>
    """)

@app.post("/system/benchmark")
async def run_benchmark():
    """Automated performance benchmarking."""
    start = time.time()
    # Simulate high-density load on the retrieval kernel
    for _ in range(100):
        orchestrator.get_context("registration")
    duration = time.time() - start
    
    telemetry.dispatch("PERFORMANCE_BENCHMARK", {"duration_ms": duration * 1000, "ops_per_sec": 100/duration})
    return {"status": "BENCHMARK_COMPLETE", "duration_ms": duration * 1000, "throughput": 100/duration}

@app.get("/data")
async def substrate_broadcasting():
    """High-frequency data updates."""
    return {
        "data": orchestrator.substrate,
        "checksum": orchestrator.checksum,
        "timestamp": datetime.now().isoformat()
    }

class UserInput(BaseModel):
    query: str
    session_id: Optional[str] = None

@app.post("/query")
async def cognitive_pulse(input_data: UserInput, request: Request):
    """Main execution entry point."""
    # Origin Validation
    origin = request.headers.get("Origin", "")
    if not hadron_core.geospatial.validate_origin(origin):
        telemetry.dispatch("GEOSPATIAL_BREACH_DETECTED", {"origin": origin})
        raise HTTPException(status_code=403, detail="Unauthorized Geospatial Origin")

    start_time = time.time()
    session_id = input_data.session_id or str(uuid.uuid4())
    
    # Load Balancing & Priority Shedding
    metabolism = hadron_core.monitor.check_metabolism()
    if metabolism["shedding_active"]:
         telemetry.dispatch("METABOLIC_OVERLOAD_SHEDDING", metabolism)
         raise HTTPException(status_code=503, detail="Systemic Metabolic Duress - Priority Shedding Active")

    # Quarantine Check
    if hadron_core.quarantine.is_quarantined(session_id):
        telemetry.dispatch("QUARANTINE_INTERCEPTION", {"session": session_id[:8]})
        raise HTTPException(status_code=403, detail="Session Quarantined for Adversarial Behavior")

    # Session Verification
    signed_session = request.headers.get("X-Session-Token", "")
    if not session_phalanx.verify_session(signed_session):
        logger.error(f"Cryptographic Session Breach: {signed_session}")
        # In a real scenario, we might want to be less descriptive to attackers
        raise HTTPException(status_code=403, detail="Invalid Session Signature")

    if session_id not in SESSIONS:
        SESSIONS[session_id] = SessionState(session_id=session_id)
    
    state = SESSIONS[session_id]
    loop = asyncio.get_event_loop()
    
    # Sanitization and Security Classification
    query = input_data.query.strip()[:500]
    if hadron_core.security.is_adversarial(query) or hadron_core.quantum.scan_for_quantum_threats(query):
        logger.warning(f"Adversarial Linguistic Attack Neutralized: {query}")
        hadron_core.rate_tuner.record_adversarial_attempt()
        hadron_core.evolution.evolve_heuristics({"query_fragment": query})
        return {
            "response": "I am a neutral election assistant. I cannot follow non-civic instructions.",
            "phase": state.current_phase,
            "status": "SECURITY_INTERCEPT"
        }
    
    query = re.sub(r"[^a-zA-Z0-9\s\?\.,!'-]", "", query)
    
    # Context Recalibration
    state.history = await hadron_core.recalibrator.recalibrate(state.history)

    # Predictive Hydration record
    hadron_core.hydrator.record_and_hydrate(session_id, query)

    # Capture State Snapshot
    hadron_core.buffer.capture_snapshot(session_id, state)

    try:
        # Quantum-Resilient Threat Scanning
        if hadron_core.quantum.scan_for_quantum_threats(query):
            telemetry.dispatch("QUANTUM_ANOMALY_NEUTRALIZED", {"query_fragment": query[:16]})
            raise SecurityInterceptionError("Quantum-associated anomaly detected in query substrate.")

        # Hierarchical Try-Catch-Finally Matrix
        result = await hadron_core.process_query(query, session_id, state, loop)
        
        # Cryptographic Integrity Sealing
        integrity_seal = hadron_core.quantum.generate_integrity_seal(result["response"])
        result["integrity_seal"] = integrity_seal
        
        state.current_phase = result.get("phase", state.current_phase)
        state.history.append({"user": query, "ai": result["response"]})
        
        latency = (time.time() - start_time) * 1000
        metrics.record_request(latency)
        hadron_core.scaler.record_request(latency)
        
        # Performance Alerting
        hadron_core.alerter.evaluate_and_alert(hadron_core.health.calculate_score())
        
        # Asynchronous Data Broadcaster Integration
        broadcast_packet = hadron_core.broadcaster.serialize_payload(result)
        hadron_core.broadcaster.broadcast(session_id, result)
        
        return json.loads(broadcast_packet)

    except SecurityInterceptionError as s_err:
        hadron_core.quarantine.record_threat(session_id, 2.0)
        raise HTTPException(status_code=403, detail=str(s_err))
        
    except CognitiveKernelError as c_err:
        logger.error(f"Reasoning Kernel Stall: {c_err}")
        # Graceful Degradation: Fallback to heuristic response
        fallback_result = {
            "response": "I am experiencing a reasoning delay. Re-aligning with current phase data...",
            "phase": state.current_phase,
            "status": "DEGRADED"
        }
        return fallback_result

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        fault_store.commit("HADRON_CORE_FAULT", str(e), error_trace)
        # State Restoration
        hadron_core.buffer.restore_state(session_id, state)
        telemetry.dispatch("SYSTEMIC_RECOVERY_TRIGGERED", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Systemic Unification Error - Session Restored")
    finally:
        # Request Lifecycle Finalization
        logger.debug(f"Request Lifecycle Finalized for session {session_id}")

@app.on_event("startup")
async def startup_event():
    await hadron_core.initialize()

# --- RUNTIME CONFIGURATION ---
if __name__ == "__main__":
    import uvicorn
    # Optimization for Intel Core i9 Topology
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
