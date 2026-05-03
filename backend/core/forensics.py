import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional
from backend.core.config import config, paths
from backend.telemetry.kernel import logger

class CryptographicAuditTrail:
    """
    The Immutable Ledger of Systemic Truth.
    Implements Hash Chaining (HMAC-SHA384) to ensure absolute forensic integrity.
    Each entry includes the hash of the previous entry, creating a verifiable chain.
    """
    def __init__(self):
        self.log_file = paths.ROOT_DIR / "logs" / "hadron_forensics.ledger"
        self.last_hash = "0" * 96 # Genesis Hash (SHA-384 size)
        self.secret = config.SESSION_SECRET.encode()
        self._lock = None # Will be initialized in the first async context

    def _get_lock(self):
        import asyncio
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def record(self, sector: str, event_type: str, payload: Dict[str, Any]):
        """Append a cryptographically chained entry to the forensic ledger."""
        ts = time.time()
        entry_data = {
            "ts": ts,
            "sector": sector,
            "type": event_type,
            "payload": payload,
            "prev_hash": self.last_hash
        }
        
        # Calculate HMAC-SHA384 for the current entry
        serialized = json.dumps(entry_data, sort_keys=True).encode()
        current_hash = hmac.new(self.secret, serialized, hashlib.sha384).hexdigest()
        
        entry_data["signature"] = current_hash
        self.last_hash = current_hash
        
        # Append to the immutable substrate
        async with self._get_lock():
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry_data) + "\n")
                
        logger.info("audit_trail_recorded", sector=sector, type=event_type, signature=current_hash[:12])

    def verify_integrity(self) -> bool:
        """Verifies the mathematical integrity of the entire audit chain."""
        if not self.log_file.exists():
            return True
            
        expected_prev_hash = "0" * 96
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    signature = entry.pop("signature")
                    
                    if entry["prev_hash"] != expected_prev_hash:
                        return False
                        
                    serialized = json.dumps(entry, sort_keys=True).encode()
                    actual_hash = hmac.new(self.secret, serialized, hashlib.sha384).hexdigest()
                    
                    if actual_hash != signature:
                        return False
                    
                    expected_prev_hash = signature
            return True
        except Exception:
            return False

audit_trail = CryptographicAuditTrail()
