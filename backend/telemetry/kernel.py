import os
import psutil
import threading
import structlog
import time
from datetime import datetime, timezone
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from prometheus_client import (
    Counter, 
    Histogram, 
    Gauge, 
    CollectorRegistry
)
from backend.core.config import config

# [SECTOR TELEMETRY] Kernel-Level Observability Initialized
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger("HADRON_TELEMETRY")

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
            "uss_mb": getattr(full_info, 'uss', 0) / (1024 * 1024),
            "shared_mb": getattr(info, 'shared', 0) / (1024 * 1024)
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
        self._radiance_history: List[float] = []
        self._lock = threading.Lock()
        
        # EVENT LOOP TELEMETRY (Loop Lag Monitor)
        self._loop_lag = 0.0
        self._last_tick = time.time()

    def _monitor_loop_health(self):
        """Measures the asynchronous event loop lag for jitter analysis."""
        now = time.time()
        self._loop_lag = (now - self._last_tick) * 1000
        self._last_tick = now

    def compute_radiance(self) -> float:
        """Executes a multi-factor algorithmic check to determine systemic health."""
        self._monitor_loop_health()
        
        cpu = self.cpu_m.scan()
        mem = self.mem_m.scan()
        
        # PENALTY LOGIC: Metabolic Bloat & Loop Lag
        lag_penalty = max(0, self._loop_lag - 50) / 10.0
        mem_excess = max(0, mem["rss_mb"] - config.TARGET_BASELINE_MB)
        mem_penalty = (mem_excess ** 1.3) / 2.5
        cpu_penalty = cpu["usage_pct"] / 2.0
        
        with self._lock:
            # SELF-HEALING: Reconcile if data seems corrupted
            raw_score = 100.0 - mem_penalty - cpu_penalty - lag_penalty
            if raw_score != raw_score or raw_score < 0:
                raw_score = self._radiance_history[-1] if self._radiance_history else 50.0
                
            self._current_radiance = max(0.0, min(100.0, raw_score))
            self._radiance_history.append(self._current_radiance)
            if len(self._radiance_history) > 100:
                self._radiance_history.pop(0)
                
            self.MEM_GAUGE.set(mem["rss_mb"])
            self.RADIANCE_GAUGE.set(self._current_radiance)
        
        return round(self._current_radiance, 2)

    def analyze_trend(self) -> str:
        """
        ANTICIPATORY RESILIENCE: Analyzes the radiance trend to predict systemic collapse.
        Returns 'STABLE', 'DEGRADING', or 'COLLAPSING'.
        """
        with self._lock:
            if len(self._radiance_history) < 10:
                return "STABLE"
            
            recent = self._radiance_history[-10:]
            avg_delta = (recent[-1] - recent[0]) / 10
            
            if avg_delta < -2.0: return "COLLAPSING"
            if avg_delta < -0.5: return "DEGRADING"
            return "STABLE"

    def pulse(self) -> Dict[str, Any]:
        """Broadcasts a metabolic radiograph of the system state."""
        radiance = self.compute_radiance()
        return {
            "radiance": radiance,
            "trend": self.analyze_trend(),
            "loop_lag_ms": round(self._loop_lag, 2),
            "cpu": self.cpu_m.scan(),
            "memory": self.mem_m.scan(),
            "io": self.io_m.scan(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": "VIBRANT" if radiance > 85 else "STABLE" if radiance > 60 else "DEGRADED"
        }

radiance_engine = SystemicRadianceEngine()
