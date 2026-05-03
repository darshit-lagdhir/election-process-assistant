import asyncio
import uuid
import time
from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from backend.core.config import config
from backend.engine.orchestrator import hadron_engine
from backend.telemetry.kernel import radiance_engine, logger
from backend.core.events import dispatcher
from backend.core.proxy import data_proxy

from fastapi.staticfiles import StaticFiles
from backend.core.supervision import SystemicLifecycleOrchestrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Systemic Ignition
    await SystemicLifecycleOrchestrator.ignite()
    yield
    # Systemic Extinction
    await SystemicLifecycleOrchestrator.extinguish()

app = FastAPI(
    title="Hadron Core API",
    version=config.ARCHITECTURAL_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MOUNT RADIANT UI SUBSTRATE
from backend.core.config import paths
app.mount("/static", StaticFiles(directory=str(paths.ROOT_DIR / "frontend")), name="static")

@app.middleware("http")
async def distributed_tracing_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    request.state.trace_id = trace_id
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = (time.time() - start_time) * 1000
    response.headers["X-Trace-ID"] = trace_id
    response.headers["X-Response-Time-Ms"] = str(duration)
    
    return response

@app.get("/")
async def sovereign_gateway():
    """The Radiant Ingress of the Hadron Core: Serving the UI Substrate."""
    ui_path = paths.ROOT_DIR / "frontend" / "index.html"
    return FileResponse(str(ui_path))

@app.get("/kernel/health")
async def health_check():
    """
    DEEP HEALTH AUDIT: Executes a multi-factor analysis of kernel vitality.
    Verifies data integrity, cognitive availability, and metabolic stability.
    """
    citizen_ok = await data_proxy.reconcile_state("citizen")
    radiance = radiance_engine.compute_radiance()
    
    status = "VIBRANT" if citizen_ok and radiance > 0.8 else "DEGRADED"
    if not citizen_ok: status = "CRITICAL_INTEGRITY_FAULT"
    
    return {
        "status": status,
        "radiance": radiance,
        "neural_conduit": "ACTIVE" if config.get_api_key() else "DISCONNECTED",
        "integrity": {"citizen": citizen_ok},
        "metabolism": radiance_engine.pulse(),
        "ts": time.time()
    }

@app.post("/api/v1/reason")
async def reason(request: Request):
    """The Radiant Ingress: Unified entry point for citizen reasoning."""
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON substrate: {str(e)}")

    query = body.get("query")
    session_id = body.get("session_id", "anonymous")
    request_id = request.state.trace_id

    if not query:
        raise HTTPException(status_code=400, detail="Query is non-existent.")

    # ORCHESTRATION WITH RESILIENCE
    try:
        result = await hadron_engine.execute(query, session_id, request_id)
        
        if result.get("status") in ["quarantine", "bridge_fault", "latency_limit"]:
            return JSONResponse(status_code=503, content=result)

        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "kernel_crash",
            "error": "Internal processing fault"
        })

@app.get("/kernel/metrics")
async def metrics():
    """Exports metabolic status at millisecond resolution for autonomic maintenance."""
    return radiance_engine.pulse()

@app.websocket("/ws/v6/hadron/telemetry")
async def telemetry_conduit(websocket: WebSocket):
    """The Real-Time Metabolic Conduit: Broadcasting systemic radiance."""
    await websocket.accept()
    try:
        while True:
            # Broadcast radiance metrics every 2 seconds
            await websocket.send_json(radiance_engine.pulse())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("WEBSOCKET_FAULT", error=str(e))
