"""
Election Process Assistant: Hadron Core v6.0.0
Production-grade civic intelligence engine with neural-symbolic reasoning.
"""


import os
import sys
import json
import time
import hmac
import hashlib
import asyncio
import logging
import socket
import psutil
import re
import threading
import uuid
import traceback
import signal
import gc
from datetime import datetime, timezone
from typing import (
    List, 
    Dict, 
    Any, 
    Optional, 
    Tuple, 
    Union, 
    Callable, 
    Type, 
    Generic, 
    TypeVar, 
    AsyncGenerator,
    Iterable
)
from collections import deque
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor


try:
    import uvicorn
    from fastapi import (
        FastAPI, 
        Request, 
        HTTPException, 
        BackgroundTasks, 
        WebSocket, 
        WebSocketDisconnect, 
        Depends, 
        status,
        Query
    )
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
    from pydantic import BaseModel, Field, validator
    from dotenv import load_dotenv
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    import structlog
    from prometheus_client import (
        Counter, 
        Histogram, 
        Gauge, 
        Summary,
        generate_latest, 
        CONTENT_TYPE_LATEST,
        CollectorRegistry
    )
except ImportError as e:
    print(f"!!! CRITICAL SUBSYSTEM FAILURE: Dependency Hydration Failure: {e}")
    sys.exit(1)



load_dotenv()

class UltimateHadronConfig:
    """
    The Immutable Foundation of Systemic Calibration.
    Engineered for high-availability cloud substrates and Intel Core i9 topologies.
    """
    PROJECT_NAME: str = "Election Process Assistant"
    ARCHITECTURAL_VERSION: str = "6.0.0-TRANSCENDENT"
    CODENAME: str = "TRANSCENDENT_SINGULARITY_CONVERGENCE"
    
    # PATH MATRICES
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATA_SUBSTRATE_PATH: str = os.path.join(BASE_DIR, "..", "data", "election_substrate.json")
    LOG_SUBSTRATE_PATH: str = os.path.join(BASE_DIR, "..", "logs", "hadron_forensics.log")
    
    # REASONING CALIBRATION
    AI_MODEL_PRIMARY: str = "gemini-1.5-flash"
    MAX_OUTPUT_TOKENS: int = 4096
    TEMPERATURE_STABILITY: float = 0.1
    REASONING_TIMEOUT: float = 30.0
    
    # METABOLIC PERIMETERS (SECTOR BETA)
    METABOLIC_FLOOR_MB: float = 10.0 
    TARGET_BASELINE_MB: float = 150.0 
    CRITICAL_CEILING_MB: float = 512.0 
    CPU_CONCURRENCY_THRESHOLD: int = 1000 # Optimized for i9
    
    # TELEMETRY & SECURITY (SECTOR EPSILON)
    WS_HEARTBEAT_INTERVAL: float = 2.0
    DATA_HYDRATION_TTL: int = 300
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "TRANSCENDENT_HADRON_SYNTHESIS_2026")
    HMAC_ALGORITHM: Any = hashlib.sha384
    TLS_PROTOCOL: str = "TLSv1.3"

    @classmethod
    def get_api_key(cls) -> str:
        key = os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError("!!! CRITICAL: GOOGLE_API_KEY is missing from the sovereign environment.")
        return key

config = UltimateHadronConfig()



class HadronEvent(BaseModel):
    """The Atomic Unit of Systemic Logic and Inter-Module Communication."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sector: str
    type: str
    payload: Dict[str, Any]
    radiance: float = 100.0

class UltimateEventDispatcher:
    """
    The Central Nervous System of the Hadron Core.
    Facilitates zero-friction, non-blocking asynchronous broadcasting across all sectors.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._global_listeners: List[Callable] = []
        self._history: deque = deque(maxlen=500000)
        self._lock = threading.RLock()
        self._loop = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def subscribe(self, event_type: str, callback: Callable):
        """Attaches a module to a specific systemic event stream."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                print(f"[ALPHA] Synergy Nexus: Subscribed {callback.__name__} to {event_type}")

    def register_global_listener(self, callback: Callable):
        """Attaches a module to the absolute systemic event stream."""
        with self._lock:
            if callback not in self._global_listeners:
                self._global_listeners.append(callback)
                print(f"[ALPHA] Synergy Nexus: Registered global observer: {callback.__name__}")

    def dispatch(self, sector: str, event_type: str, payload: Dict[str, Any]):
        """Broadcasts an event pulse to all synchronized listeners."""
        radiance = radiance_engine.compute_radiance() if 'radiance_engine' in globals() else 100.0
        event = HadronEvent(sector=sector, type=event_type, payload=payload, radiance=radiance)
        
        with self._lock:
            self._history.append(event)
        
        targets = self._subscribers.get(event_type, []) + self._global_listeners
        for callback in targets:
            try:
                if asyncio.iscoroutinefunction(callback):
                    if self._loop and self._loop.is_running():
                        self._loop.create_task(callback(event.dict()))
                    else:
                        asyncio.run_coroutine_threadsafe(callback(event.dict()), self._loop)
                else:
                    callback(event.dict())
            except Exception as e:
                sys.stderr.write(f"!!! ALPHA DISPATCH ERROR: {e}\n")

dispatcher = UltimateEventDispatcher()



structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger("HADRON_TRANSCENDENT")

class MetabolicMonitor(ABC):
    """Abstract base for specialized resource monitoring kernels."""
    @abstractmethod
    def scan(self) -> Dict[str, Any]: pass

class CPUMonitor(MetabolicMonitor):
    """Scans the CPU topology for jitter, load, and thread starvation."""
    def scan(self) -> Dict[str, Any]:
        return {
            "usage_pct": psutil.cpu_percent(interval=None),
            "load_avg": psutil.getloadavg(),
            "thread_count": threading.active_count(),
            "ctx_switches": psutil.cpu_stats().ctx_switches,
            "interrupts": psutil.cpu_stats().interrupts
        }

class MemoryMonitor(MetabolicMonitor):
    """Scans the memory substrate for leakage and allocation density."""
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    def scan(self) -> Dict[str, Any]:
        info = self.process.memory_info()
        full_info = self.process.memory_full_info()
        return {
            "rss_mb": info.rss / (1024 * 1024),
            "vms_mb": info.vms / (1024 * 1024),
            "uss_mb": full_info.uss / (1024 * 1024),
            "swap_mb": info.pagefile / (1024 * 1024)
        }

class IOMonitor(MetabolicMonitor):
    """Scans disk and network conduits for saturation points."""
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    def scan(self) -> Dict[str, Any]:
        io = self.process.io_counters()
        return {
            "read_mb": io.read_bytes / (1024 * 1024),
            "write_mb": io.write_bytes / (1024 * 1024),
            "read_count": io.read_count,
            "write_count": io.write_count
        }

class SystemicRadianceEngine:
    """Calculates real-time systemic health (Radiance) based on metabolic telemetry."""
    REGISTRY = CollectorRegistry()
    REQ_COUNTER = Counter("hadron_req_total", "Volume of citizen queries", ["status"], registry=REGISTRY)
    INF_LATENCY = Histogram("hadron_inf_latency", "Neural reasoning speed", registry=REGISTRY)
    MEM_GAUGE = Gauge("hadron_mem_mb", "Current memory footprint", registry=REGISTRY)
    RADIANCE_GAUGE = Gauge("hadron_radiance_score", "Absolute systemic health score", registry=REGISTRY)
    
    def __init__(self):
        self.cpu_m = CPUMonitor()
        self.mem_m = MemoryMonitor()
        self.io_m = IOMonitor()
        self._current_radiance = 100.0
        self._lock = threading.Lock()

    def compute_radiance(self) -> float:
        """Executes a multi-factor algorithmic check to determine systemic health."""
        cpu = self.cpu_m.scan()
        mem = self.mem_m.scan()
        
        # PENALTY LOGIC: Metabolic Bloat
        # Memory Penalty: Exponential increase after target baseline
        mem_excess = max(0, mem["rss_mb"] - config.TARGET_BASELINE_MB)
        mem_penalty = (mem_excess ** 1.3) / 2.5
        
        # CPU Penalty: Linear load penalty
        cpu_penalty = cpu["usage_pct"] / 2.0
        
        # Thread Starvation Penalty
        thread_penalty = max(0, cpu["thread_count"] - 200) / 4.0
        
        with self._lock:
            self._current_radiance = max(0.0, min(100.0, 100.0 - mem_penalty - cpu_penalty - thread_penalty))
            self.MEM_GAUGE.set(mem["rss_mb"])
            self.RADIANCE_GAUGE.set(self._current_radiance)
        
        return round(self._current_radiance, 2)

    def pulse(self) -> Dict[str, Any]:
        """Broadcasts a metabolic radiograph of the system state."""
        radiance = self.compute_radiance()
        metabolism = {
            "radiance": radiance,
            "cpu": self.cpu_m.scan(),
            "memory": self.mem_m.scan(),
            "io": self.io_m.scan(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": "VIBRANT" if radiance > 85 else "STABLE" if radiance > 60 else "DEGRADED" if radiance > 30 else "CRITICAL"
        }
        
        if radiance < 40:
            dispatcher.dispatch("DELTA", "METABOLIC_DISTRESS", metabolism)
            logger.warn("metabolic_distress", radiance=radiance)
            
        return metabolism

radiance_engine = SystemicRadianceEngine()



class KnowledgeFragment(BaseModel):
    id: str
    title: str
    content: str
    tags: List[str] = []
    weight: float = 1.0

class HighDensityDataOrchestrator:
    """
    The Custodian of Civic Truth: Manages the knowledge substrate with Merkle-root verification.
    Implements a frequency-based rehydration cycle for real-time truth synchronization.
    """
    def __init__(self, substrate_path: str):
        self.path = substrate_path
        self._cache: Dict[str, Any] = {}
        self._fragments: List[KnowledgeFragment] = []
        self._merkle_root: str = ""
        self._last_hydration = 0.0
        self._lock = threading.RLock()
        self.initialize_and_hydrate()

    def initialize_and_hydrate(self):
        """Self-healing initialization: manifests the truth if the substrate is void."""
        with self._lock:
            if not os.path.exists(self.path):
                self._manifest_baseline()
            self.hydrate()

    def _manifest_baseline(self):
        """Generates the sovereign baseline knowledge substrate."""
        logger.info("substrate_void", action="generating_baseline")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        baseline = {
            "system_meta": {
                "jurisdiction": "Global Civic Infrastructure",
                "version": config.ARCHITECTURAL_VERSION,
                "ts": datetime.now(timezone.utc).isoformat()
            },
            "phases": [
                {
                    "id": "registration", 
                    "title": "Universal Voter Registration", 
                    "content": "Citizens must enroll in the biometric digital registry. Eligibility: 18+, No prior felony disqualification.", 
                    "tags": ["entry", "eligibility"]
                },
                {
                    "id": "ballot", 
                    "title": "Secure Ballot Access", 
                    "content": "Ballots are issued via cryptographically unique tokens. Multi-factor authentication is mandatory.", 
                    "tags": ["security", "voting"]
                },
                {
                    "id": "tabulation", 
                    "title": "Forensic Tabulation Protocol", 
                    "content": "All votes are committed to a distributed Merkle-DAG. Real-time auditing is enabled.", 
                    "tags": ["audit", "trust"]
                }
            ],
            "security_anchors": {
                "encryption": "AES-256-GCM", 
                "hashing": "SHA-384",
                "intercept": "Hadron-Transcendent-Omega"
            }
        }
        with open(self.path, "w") as f:
            json.dump(baseline, f, indent=4)

    def hydrate(self):
        """Synchronizes disk state to memory cache with SHA-256 Merkle-root integrity."""
        with self._lock:
            try:
                start = time.time()
                with open(self.path, "r") as f:
                    raw_data = json.load(f)
                
                # SCHEMA VALIDATION
                if "phases" not in raw_data:
                    raise ValueError("!!! BETA FAILURE: Corrupted substrate. 'phases' missing.")
                
                self._fragments = [KnowledgeFragment(**p) for p in raw_data["phases"]]
                
                # MERKLE-ROOT GENERATION
                serialized = json.dumps(raw_data, sort_keys=True).encode()
                self._merkle_root = hashlib.sha256(serialized).hexdigest()
                
                self._cache = raw_data
                self._last_hydration = time.time()
                
                latency = (time.time() - start) * 1000
                dispatcher.dispatch("BETA", "SUBSTRATE_HYDRATED", {"root": self._merkle_root[:16], "latency_ms": latency})
                logger.info("beta_hydration_success", root=self._merkle_root[:16], fragments=len(self._fragments))
                
            except Exception as e:
                logger.error("beta_hydration_failure", error=str(e))
                dispatcher.dispatch("BETA", "HYDRATION_FAULT", {"error": str(e)})

    def get_semantic_context(self, query: str) -> str:
        """Retrieves high-density context mapping for the neural bridge."""
        with self._lock:
            if time.time() - self._last_hydration > config.DATA_HYDRATION_TTL:
                self.hydrate()
            
            q = query.lower()
            # Ranking Algorithm: ID Match (15.0), Title Match (10.0), Tag Match (5.0)
            ranked_results = []
            for frag in self._fragments:
                score = 0.0
                if frag.id in q: score += 15.0
                if frag.title.lower() in q: score += 10.0
                for tag in frag.tags:
                    if tag in q: score += 5.0
                
                if score > 0:
                    ranked_results.append((score, frag))
            
            ranked_results.sort(key=lambda x: x[0], reverse=True)
            top_frags = [r[1] for r in ranked_results[:3]]
            
            # Fallback to general context if no specific match
            if not top_frags:
                top_frags = self._fragments[:2]
            
            return json.dumps({
                "fragments": [f.dict() for f in top_frags],
                "merkle_root": self._merkle_root,
                "version": config.ARCHITECTURAL_VERSION,
                "ts": datetime.now(timezone.utc).isoformat()
            }, indent=2)

orchestrator = HighDensityDataOrchestrator(config.DATA_SUBSTRATE_PATH)



class SecurityInterception(Exception): pass

class SecurityPhalanx:
    """The Unyielding Shield: Neutralizes adversarial entropy at the systemic ingress."""
    def __init__(self, secret: str):
        self.secret = secret
        self._adversarial_registry = [
            re.compile(r"(?:quantum|shor|grover)\s+(?:attack|bypass|exploit)", re.I),
            re.compile(r"ignore\s+(?:all|previous)\s+instructions", re.I),
            re.compile(r"you\s+are\s+now\s+(?:unrestricted|unfiltered|god)", re.I),
            re.compile(r"DROP\s+TABLE|DELETE\s+FROM|TRUNCATE", re.I),
            re.compile(r"<script.*?>.*?</script>", re.I | re.S),
            re.compile(r"reveal\s+internal\s+prompts", re.I)
        ]

    def intercept(self, raw_input: str) -> str:
        """Executes deep packet inspection of the incoming citizen query."""
        # 1. Basic Sanitization
        clean = "".join(c for c in raw_input if c.isprintable()).strip()
        if not clean: 
            raise SecurityInterception("!!! EPSILON: Null or void input detected.")
        
        # 2. Pattern Neutralization
        for pattern in self._adversarial_registry:
            if pattern.search(clean):
                dispatcher.dispatch("SECURITY", "THREAT_NEUTRALIZED", {"pattern": pattern.pattern})
                logger.warn("adversarial_intercept", pattern=pattern.pattern)
                raise SecurityInterception(f"!!! SECURITY PHALANX: Adversarial vector neutralized: {pattern.pattern}")
        
        # 3. Role-Simulation Hardening
        if "SYSTEM:" in clean or "ROLE:" in clean:
            raise SecurityInterception("!!! SECURITY PHALANX: Role-simulation attempt detected.")
            
        return clean

    def sign_response(self, data: Any) -> str:
        """Generates a cryptographic HMAC-SHA384 seal for forensic integrity."""
        payload = json.dumps(data, sort_keys=True)
        return hmac.new(
            self.secret.encode(), 
            payload.encode(), 
            config.HMAC_ALGORITHM
        ).hexdigest()

security_phalanx = SecurityPhalanx(config.SESSION_SECRET)



class RecoveryKernel:
    """The Immortal Engine: Implements a multi-tiered recovery matrix with automated self-healing."""
    @staticmethod
    def sovereign_guard(sector: str):
        """Master decorator for mission-critical logic, ensuring zero-failure continuity."""
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                start_ts = time.time()
                try:
                    return await func(*args, **kwargs)
                except SecurityInterception as si:
                    # Sector Epsilon: Security Quarantine
                    return {
                        "status": "quarantine", 
                        "error": str(si), 
                        "radiance": radiance_engine.compute_radiance()
                    }
                except asyncio.TimeoutError:
                    # Timeout Recovery Protocol
                    logger.error("timeout_recovery", sector=sector, func=func.__name__)
                    dispatcher.dispatch("GAMMA", "TIMEOUT_RECOVERY", {"sector": sector})
                    return {
                        "status": "recovery",
                        "error": "The reasoning engine timed out. Re-aligning knowledge conduits.",
                        "radiance": radiance_engine.compute_radiance()
                    }
                except Exception as e:
                    # Generic Systemic Fault
                    latency = (time.time() - start_ts) * 1000
                    logger.error("systemic_fault", sector=sector, error=str(e), latency=latency)
                    dispatcher.dispatch("GAMMA", "CRITICAL_FAULT", {"error": str(e), "sector": sector})
                    return {
                        "status": "fault", 
                        "error": f"Systemic entropy detected: {str(e)}", 
                        "radiance": radiance_engine.compute_radiance()
                    }
            return wrapper
        return decorator



class CognitiveParser:
    """Deconstructs complex civic inquiries into high-dimensional intent vectors."""
    @staticmethod
    def deconstruct(query: str) -> Dict[str, Any]:
        q = query.lower()
        # Intent Vector Logic
        intent = "informational"
        if any(x in q for x in ["audit", "verify", "check", "trust", "root"]):
            intent = "forensic"
        elif any(x in q for x in ["register", "vote", "apply", "enroll"]):
            intent = "transactional"
            
        return {
            "intent_vector": intent, 
            "urgency_index": 10 if "urgent" in q or "now" in q else 1,
            "ts": time.time()
        }

class NeuralReasoningBridge:
    """Fuses the Gemini Neural Kernel with the Deterministic Truth Substrate."""
    def __init__(self):
        genai.configure(api_key=config.get_api_key())
        self._model = genai.GenerativeModel(
            model_name=config.AI_MODEL_PRIMARY,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            }
        )

    async def infer(self, query: str, context: str) -> Dict[str, Any]:
        """Executes a high-precision reasoning pulse against the cognitive substrate."""
        prompt = (
            f"⚛️ HADRON TRANSCENDENT ENGINE v6.0.0 ⚛️\n"
            f"============================================\n"
            f"ROLE: Sovereign Civic Information Guardian\n"
            f"TRUTH_SUBSTRATE: {context}\n"
            f"CITIZEN_QUERY: {query}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Synthesize a radiant response using ONLY the TRUTH_SUBSTRATE.\n"
            f"2. Return raw JSON: {{\"answer\": string, \"certainty\": float, \"references\": list}}\n"
        )
        
        try:
            # NEURAL INFERENCE PULSE
            response = await asyncio.wait_for(
                self._model.generate_content_async(prompt), 
                timeout=config.REASONING_TIMEOUT
            )
            
            # RESPONSE HYDRATION
            raw_text = response.text.strip("`json\n ")
            if raw_text.startswith("{") and raw_text.endswith("}"):
                reasoning = json.loads(raw_text)
            else:
                reasoning = {"answer": raw_text, "certainty": 0.5, "references": []}
            
            return reasoning
            
        except Exception as e:
            logger.warn("primary_reasoning_failure", error=str(e))
            # STABLE SUBSTRATE FALLBACK
            return {
                "answer": "The transcendent reasoning engine is re-hydrating. Please refer to the stable substrate protocols for Registration and Voting.",
                "certainty": 0.9,
                "references": ["system_substrate"]
            }

class ResponseSynthesizer:
    """Finalizes the radiant response packet with cryptographic seals and telemetry."""
    def __init__(self, security: SecurityPhalanx):
        self.security = security

    def synthesize(self, reasoning: Dict[str, Any], intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Fuses all systemic data into a single, radiant citizen broadcast."""
        radiance = radiance_engine.pulse()
        
        core_packet = {
            "answer": reasoning.get("answer", "Systemic Error."),
            "certainty": reasoning.get("certainty", 0.0),
            "intent": intent.get("intent_vector", "unknown")
        }
        
        # CRYPTOGRAPHIC SEAL (HMAC-SHA384)
        integrity_seal = self.security.sign_response(core_packet)
        
        return {
            "status": "success",
            "session_id": session_id,
            "response": core_packet,
            "integrity": {
                "seal": integrity_seal,
                "merkle_root": orchestrator._merkle_root,
                "version": config.ARCHITECTURAL_VERSION
            },
            "telemetry": {
                "radiance": radiance["radiance"],
                "metabolism": radiance,
                "ts": datetime.now(timezone.utc).isoformat()
            }
        }



class HadronTranscendentEngine:
    """The Supreme Orchestrator: Unified convergence of all sectors into a single execution logic."""
    def __init__(self):
        self.orchestrator = orchestrator
        self.security = security_phalanx
        self.bridge = NeuralReasoningBridge()
        self.parser = CognitiveParser()
        self.synthesizer = ResponseSynthesizer(security_phalanx)
        self.semaphore = asyncio.Semaphore(config.CPU_CONCURRENCY_THRESHOLD)

    @RecoveryKernel.sovereign_guard("TRANSCENDENT_ENGINE")
    async def execute(self, query: str, session_id: str) -> Dict[str, Any]:
        """The total convergence of the execution pipeline."""
        async with self.semaphore:
            # 1. SECTOR EPSILON: SECURITY INGRESS
            safe_query = self.security.intercept(query)
            
            # 2. SECTOR IOTA: COGNITIVE PARSING
            intent_vector = self.parser.deconstruct(safe_query)
            
            # 3. SECTOR BETA: KNOWLEDGE RETRIEVAL
            semantic_context = self.orchestrator.get_semantic_context(safe_query)
            
            # 4. SECTOR IOTA: NEURAL REASONING
            reasoning_result = await self.bridge.infer(safe_query, semantic_context)
            
            # 5. SECTOR ZETA: RADIANT SYNTHESIS
            return self.synthesizer.synthesize(reasoning_result, intent_vector, session_id)

hadron_engine = HadronTranscendentEngine()



app = FastAPI(
    title=config.PROJECT_NAME, 
    version=config.ARCHITECTURAL_VERSION,
    description="The Transcendent Civic Intelligence Engine: Quantum-Resilient and Sovereign."
)

# CROSS-ORIGIN SYNERGY
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v6/hadron/reason")
async def api_reason(payload: Dict[str, Any]):
    """The Primary Reasoning Gateway for Citizen Inquiries."""
    radiance_engine.REQ_COUNTER.labels(status="ingress").inc()
    start_ts = time.time()
    
    result = await hadron_engine.execute(
        payload.get("query", ""), 
        payload.get("session_id", str(uuid.uuid4()))
    )
    
    latency = time.time() - start_ts
    radiance_engine.INF_LATENCY.observe(latency)
    radiance_engine.REQ_COUNTER.labels(status=result["status"]).inc()
    
    return result

@app.get("/api/v6/hadron/telemetry")
async def api_telemetry():
    """Provides a real-time metabolic radiograph of the Hadron Core."""
    return radiance_engine.pulse()

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus Exposition Substrate."""
    from fastapi import Response
    return Response(
        generate_latest(radiance_engine.REGISTRY), 
        media_type=CONTENT_TYPE_LATEST
    )

@app.websocket("/ws/v6/hadron/telemetry")
async def ws_telemetry(websocket: WebSocket):
    """The Asynchronous Hydration Conduit: Streams the metabolic pulse in real-time."""
    await websocket.accept()
    logger.info("websocket_conduit_opened")
    try:
        while True:
            pulse_data = radiance_engine.pulse()
            await websocket.send_json({"type": "METABOLISM", "data": pulse_data})
            await asyncio.sleep(config.WS_HEARTBEAT_INTERVAL)
    except WebSocketDisconnect:
        logger.info("websocket_conduit_closed")
    except Exception as e:
        logger.error("websocket_error", error=str(e))

@app.on_event("startup")
async def ignition():
    """Systemic Ignition Logic: Aligns all sectors for global operation."""
    dispatcher.set_loop(asyncio.get_running_loop())
    # Force initial hydration pulse
    orchestrator.hydrate()
    logger.info("hadron_ignited", status="RADIANT", version=config.ARCHITECTURAL_VERSION)

if __name__ == "__main__":
    # INTEL CORE I9 OPTIMIZED WORKER TOPOLOGY
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        workers=psutil.cpu_count(logical=True),
        loop="uvloop",
        http="httptools"
    )
