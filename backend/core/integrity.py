import hmac
import hashlib
import json
import time
import asyncio
from typing import Dict, Any, Optional, List
from backend.core.config import config, paths
from backend.telemetry.kernel import logger

class ImmutableTruthLedger:
    """
    The Self-Verifying Substrate (Final).
    Implements Read-Verification and Multi-Stage Hash Commitment.
    Ensures that every record is verified before retrieval.
    """
    def __init__(self, domain: str):
        self.domain = domain
        self.storage_file = paths.ROOT_DIR / "data" / f"{domain}_integrity.ledger"
        self.secret = config.SESSION_SECRET.encode()
        self._lock = asyncio.Lock()
        self._last_hash = "0" * 96

    async def initialize(self):
        self._last_hash = "0" * 96
        if not self.storage_file.parent.exists():
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "rb") as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1])
                        self._last_hash = last_entry["signature"]
            except Exception:
                logger.error("integrity_reconciliation_required", domain=self.domain)

    async def reset_state(self):
        """Total cryptographic purge for validation isolation."""
        self._last_hash = "0" * 96
        if self.storage_file.exists():
            self.storage_file.unlink()

    async def commit(self, record: Dict[str, Any]) -> str:
        """Commits an immutable record with multi-stage hash commitment."""
        if not self.storage_file.parent.exists():
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
        ts = time.time()
        block = {
            "ts": ts,
            "data": record,
            "prev_hash": self._last_hash
        }
        
        serialized = json.dumps(block, sort_keys=True).encode()
        current_hash = hmac.new(self.secret, serialized, hashlib.sha384).hexdigest()
        block["signature"] = current_hash
        
        async with self._lock:
            with open(self.storage_file, "a") as f:
                f.write(json.dumps(block) + "\n")
            self._last_hash = current_hash
            
        return current_hash

    async def retrieve(self, index: int) -> Optional[Dict[str, Any]]:
        """
        READ-VERIFICATION: Performs a cryptographic check upon retrieval.
        Ensures the absolute purity of the record before it touches the Reasoning Engine.
        """
        try:
            async with self._lock:
                with open(self.storage_file, "r") as f:
                    lines = f.readlines()
                    if index >= len(lines): return None
                    
                    entry = json.loads(lines[index])
                    signature = entry.pop("signature")
                    
                    # Cryptographic Verification
                    serialized = json.dumps(entry, sort_keys=True).encode()
                    actual = hmac.new(self.secret, serialized, hashlib.sha384).hexdigest()
                    
                    if actual != signature:
                        logger.critical("DATA_CORRUPTION_DETECTED", domain=self.domain, index=index)
                        raise RuntimeError("Systemic Integrity Collapse.")
                        
                    return entry["data"]
        except Exception as e:
            logger.error("retrieval_fault", domain=self.domain, error=str(e))
            return None

    async def verify_chain(self) -> bool:
        if not self.storage_file.exists(): return True
        expected_prev = "0" * 96
        try:
            async with self._lock:
                with open(self.storage_file, "r") as f:
                    for line in f:
                        entry = json.loads(line)
                        signature = entry.pop("signature")
                        if entry["prev_hash"] != expected_prev: return False
                        serialized = json.dumps(entry, sort_keys=True).encode()
                        actual = hmac.new(self.secret, serialized, hashlib.sha384).hexdigest()
                        if actual != signature: return False
                        expected_prev = signature
            return True
        except Exception:
            return False

citizen_records_ledger = ImmutableTruthLedger("citizen")
electoral_actions_ledger = ImmutableTruthLedger("electoral")
