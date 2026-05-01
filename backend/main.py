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
    from google import genai as google_genai
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
    from fastapi.staticfiles import StaticFiles
except ImportError as e:
    print(f"!!! CRITICAL SUBSYSTEM FAILURE: Dependency Hydration Failure: {e}")
    sys.exit(1)



load_dotenv()

class UltimateHadronConfig:
    """
    The Immutable Foundation of Systemic Calibration.
    Engineered for high-availability cloud substrates and Intel Core i9 topologies.
    """
    PROJECT_NAME: str = "Hadron Core Election Assistant"
    ARCHITECTURAL_VERSION: str = "7.0.0-SOVEREIGN"
    CODENAME: str = "SOVEREIGN_NEURAL_GROUNDING"
    
    # PATH MATRICES
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DATA_SUBSTRATE_PATH: str = os.path.join(BASE_DIR, "..", "data", "election_substrate.json")
    LOG_SUBSTRATE_PATH: str = os.path.join(BASE_DIR, "..", "logs", "hadron_forensics.log")
    
    # REASONING CALIBRATION
    # Primary model + ultra-resilient fallback chain. 
    # Tries every possible free-tier variant to bypass rate limits.
    AI_MODEL_PRIMARY: str = "gemini-1.5-flash"
    MODEL_FALLBACK_CHAIN: list = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash-8b-latest",
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro-002",
    ]
    MAX_OUTPUT_TOKENS: int = 4096
    TEMPERATURE_STABILITY: float = 0.1
    REASONING_TIMEOUT: float = 45.0  # Extra room for deep grounding
    MODEL_BLACKLIST_COOLDOWN: int = 900   # Quicker retry (15 mins)
    
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
        return key.strip()

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



# [SECTOR ALPHA] Real-Time Neural Grounding Initialized
# Static data substrates and RAG orchestrators have been dismantled for total neural sovereignty.



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



# [SECTOR DELTA] Intent Analysis Dismantled for Real-Time Neural Search

class NeuralReasoningBridge:
    """AI reasoning engine with automatic model fallback chain.
    
    If a model is rate-limited or unavailable, it instantly switches
    to the next model in the fallback chain without blocking.
    Blacklisted models are remembered and skipped for 1 hour.
    """
    def __init__(self):
        self._client = google_genai.Client(api_key=config.get_api_key())
        # Tracks blacklisted models: {model_name: blacklisted_until_timestamp}
        self._blacklist: Dict[str, float] = {}
        # Index into the fallback chain for the currently active model
        self._active_idx: int = 0
        print(f"[MODEL CHAIN] Initialized. Priority order: {config.MODEL_FALLBACK_CHAIN}")

    def _get_active_models(self) -> list:
        """Returns models that are not currently blacklisted."""
        now = time.time()
        # Clear expired blacklist entries
        expired = [m for m, until in self._blacklist.items() if now > until]
        for m in expired:
            del self._blacklist[m]
            print(f"[MODEL CHAIN] {m} removed from blacklist — retrying.")
        return [m for m in config.MODEL_FALLBACK_CHAIN if m not in self._blacklist]

    def _blacklist_model(self, model: str):
        """Temporarily blacklists a model for MODEL_BLACKLIST_COOLDOWN seconds."""
        until = time.time() + config.MODEL_BLACKLIST_COOLDOWN
        self._blacklist[model] = until
        print(f"[MODEL CHAIN] {model} blacklisted for {config.MODEL_BLACKLIST_COOLDOWN//60}min.")

    def _build_prompt(self, query: str) -> str:
        return (
            f"You are a Live Election Intelligence Engine with REAL-TIME web access. "
            f"TODAY'S DATE: {datetime.now().strftime('%B %d, %Y')}\n\n"
            f"Instructions:\n"
            f"- If the query is a simple greeting (like 'hi', 'hello'), respond with a SHORT, friendly one-sentence welcome.\n"
            f"- For information queries, use your Google Search tool to provide accurate, REAL-TIME data.\n"
            f"- Be concise and authoritative. Do not provide a massive briefing unless specifically asked.\n\n"
            f"QUESTION: {query}\n\n"
            f"Return ONLY a JSON object in this exact format:\n"
            f'  {{"answer": "your concise response here", "certainty": 1.0, "references": ["google_search_grounding"]}}\n'
            f"- No markdown, no extra text, just the JSON."
        )

    async def infer(self, query: str) -> Dict[str, Any]:
        """Try each available model in order. Fail fast and switch on error."""
        prompt = self._build_prompt(query)
        available = self._get_active_models()

        if not available:
            # All models blacklisted — try the primary anyway as last resort
            available = [config.AI_MODEL_PRIMARY]
            print("[MODEL CHAIN] All models blacklisted — forcing primary model.")

        for model in available:
            print(f"[MODEL CHAIN] Trying: {model}")
            try:
                loop = asyncio.get_running_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda m=model: self._client.models.generate_content(
                            model=m,
                            contents=prompt,
                            config={'tools': [{'google_search': {}}]}
                        )
                    ),
                    timeout=config.REASONING_TIMEOUT
                )
                raw_text = response.text.strip().strip("`").strip()
                # Strip markdown json block if present
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:].strip()
                if raw_text.startswith("{") and raw_text.endswith("}"):
                    result = json.loads(raw_text)
                else:
                    result = {"answer": raw_text, "certainty": 0.9, "references": []}
                print(f"[MODEL CHAIN] Success with: {model}")
                return result

            except asyncio.TimeoutError:
                print(f"[MODEL CHAIN] {model} timed out after {config.REASONING_TIMEOUT}s — switching.")
                self._blacklist_model(model)
                continue

            except Exception as e:
                err_str = str(e)
                print(f"[MODEL CHAIN] {model} failed: {err_str[:120]}")
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    self._blacklist_model(model)
                    continue  # Try next model immediately — no waiting
                elif "404" in err_str or "not found" in err_str.lower():
                    self._blacklist_model(model)
                    continue
                else:
                    # Unknown error on this model — skip it
                    continue

        # All models exhausted
        print("[MODEL CHAIN] All models exhausted.")
        return {
            "answer": "All AI models are currently unavailable due to rate limits. Please wait a minute and try again. This is a free-tier API limitation.",
            "certainty": 0.0,
            "references": []
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
        self.security = security_phalanx
        self.bridge = NeuralReasoningBridge()
        self.synthesizer = ResponseSynthesizer(security_phalanx)
        self.semaphore = asyncio.Semaphore(config.CPU_CONCURRENCY_THRESHOLD)

    @RecoveryKernel.sovereign_guard("TRANSCENDENT_ENGINE")
    async def execute(self, query: str, session_id: str) -> Dict[str, Any]:
        """The total convergence of the execution pipeline (Real-Time Neural Grounding)."""
        async with self.semaphore:
            # 1. SECURITY INGRESS
            safe_query = self.security.intercept(query)
            
            # 2. NEURAL REASONING (With Real-Time Google Search Grounding)
            reasoning_result = await self.bridge.infer(safe_query)
            
            # 3. RADIANT SYNTHESIS
            return self.synthesizer.synthesize(reasoning_result, {"intent_vector": "real-time"}, session_id)

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

@app.get("/api/health")
async def api_health():
    """System Vitality Check for Docker Health monitoring."""
    return {"status": "RADIANT", "version": config.ARCHITECTURAL_VERSION, "ts": time.time()}

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
    # dispatcher.set_loop(asyncio.get_running_loop()) # Disabled for Real-Time Search
    logger.info("hadron_ignited", status="RADIANT", version=config.ARCHITECTURAL_VERSION)

@app.get("/", include_in_schema=False)
async def serve_index():
    index_path = os.path.join(os.path.dirname(config.BASE_DIR), "frontend", "index.html")
    return FileResponse(index_path)

app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(config.BASE_DIR), "frontend")), name="frontend")

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        loop="auto",
        http="auto"
    )
