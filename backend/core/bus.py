import asyncio
import time
from typing import Dict, List, Any, Callable, Awaitable
from backend.telemetry.kernel import logger

class SystemicEventBus:
    """
    The High-Fidelity Event Dispatcher.
    Orchestrates inter-module communication with millisecond telemetry.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], Awaitable[None]]]] = {}
        self._lock = asyncio.Lock()
        self._event_count = 0
        self._last_dispatch_latency = 0.0

    async def subscribe(self, event_type: str, callback: Callable[[Any], Awaitable[None]]):
        """Subscribes a module conduit to a specific event stream."""
        async with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
            logger.info("BUS_SUBSCRIBER_REGISTERED", type=event_type)

    async def publish(self, event_type: str, data: Any):
        """
        Dispatches an event across the modular ecosystem.
        Captures millisecond-resolution propagation metrics.
        """
        start_ts = time.time()
        
        if event_type not in self._subscribers:
            return

        tasks = []
        for callback in self._subscribers[event_type]:
            tasks.append(self._execute_safe(callback, data))

        if tasks:
            await asyncio.gather(*tasks)

        latency = (time.time() - start_ts) * 1000
        self._last_dispatch_latency = latency
        self._event_count += 1
        
        if latency > 100:
            logger.warning("EVENT_BUS_CONGESTION_DETECTED", type=event_type, latency=round(latency, 2))

    async def _execute_safe(self, callback: Callable[[Any], Awaitable[None]], data: Any):
        """Executes a subscriber callback with bulkhead isolation."""
        try:
            await callback(data)
        except Exception as e:
            logger.error("EVENT_CONSUMER_FAULT", error=str(e))

    def get_metrics(self) -> Dict[str, Any]:
        """Exports the dispatcher's metabolic state."""
        return {
            "total_events": self._event_count,
            "last_latency_ms": round(self._last_dispatch_latency, 2),
            "subscriber_count": sum(len(s) for s in self._subscribers.values())
        }

event_bus = SystemicEventBus()
