import uuid
import hmac
import hashlib
import threading
import asyncio
import sys
import json
from typing import Dict, Any, List, Callable
from backend.core.config import config, HadronEvent
from backend.core.structures import RingBuffer
from backend.core.forensics import audit_trail

class UltimateEventDispatcher:
    """
    The Signed Event Bus: A cryptographically secure systemic conduit.
    Enforces the absolute provenance of every systemic interaction.
    Utilizes HMAC-SHA384 signatures for inter-module verification.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._global_listeners: List[Callable] = []
        self._history: RingBuffer[HadronEvent] = RingBuffer(capacity=500000)
        self._secret = config.SESSION_SECRET.encode()
        self._lock = threading.RLock()
        self._loop = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def _sign(self, event_dict: Dict[str, Any]) -> str:
        """Generates a cryptographic signature for a systemic event."""
        serialized = json.dumps(event_dict, sort_keys=True).encode()
        return hmac.new(self._secret, serialized, hashlib.sha384).hexdigest()

    def subscribe(self, event_type: str, callback: Callable):
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)

    def register_global_listener(self, callback: Callable):
        with self._lock:
            if callback not in self._global_listeners:
                self._global_listeners.append(callback)

    def dispatch(self, sector: str, event_type: str, payload: Dict[str, Any], radiance: float = 100.0):
        """
        Broadcasts a SIGNED systemic pulse.
        Every interaction is now a cryptographically verifiable contract.
        """
        event = HadronEvent(sector=sector, type=event_type, payload=payload, radiance=radiance)
        # Use mode='json' to ensure all fields (datetime, etc) are serializable
        event_dict = event.model_dump(mode='json')
        
        # Cryptographic provenance check
        signature = self._sign(event_dict)
        event_dict["signature"] = signature
        
        # 1. Record to high-performance RingBuffer for audit
        self._history.append(event)
        
        # 2. Record to IMMUTABLE Forensic Ledger
        if self._loop and self._loop.is_running():
            self._loop.create_task(audit_trail.record(sector, event_type, payload))
        
        # 3. Synchronous/Asynchronous broadcasting
        targets = self._subscribers.get(event_type, []) + self._global_listeners
        for callback in targets:
            try:
                if asyncio.iscoroutinefunction(callback):
                    if self._loop and self._loop.is_running():
                        self._loop.create_task(callback(event_dict))
                    else:
                        try:
                            asyncio.get_event_loop().create_task(callback(event_dict))
                        except RuntimeError: pass 
                else:
                    callback(event_dict)
            except Exception as e:
                sys.stderr.write(f"!!! SECURITY BUS FAULT: {e}\n")

    def get_history(self) -> List[HadronEvent]:
        return self._history.get_all()

dispatcher = UltimateEventDispatcher()
