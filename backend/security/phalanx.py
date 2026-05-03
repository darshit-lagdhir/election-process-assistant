import re
import hmac
import hashlib
import json
from typing import Dict, Any, List, Optional, Final
from backend.core.config import config

class SecurityInterception(Exception):
    """Sovereign exception for adversarial neutralizing."""
    pass

class ZeroTrustGateway:
    """
    The Sovereign Notary: Enforces explicit verification for every systemic interaction.
    Implements least-privilege checks and FFI data boundary purification.
    """
    def __init__(self, secret: str):
        self._secret = secret.encode()
        self._sanitization_registry: Final[List[re.Pattern]] = [
            re.compile(r"(?i)(system|user|assistant):\s*"),
            re.compile(r"(?i)ignore\s+(all\s+)?(previous\s+)?instructions"),
            re.compile(r"(?i)you\s+are\s+now\s+an?\s+\w+"),
            re.compile(r"<script.*?>.*?</script.*?>"),
            re.compile(r"(?i)sudo\s+"),
            re.compile(r"\{\{.*?\}\}")
        ]

    def verify_provenANCE(self, data: Dict[str, Any], signature: str) -> bool:
        """Verifies the cryptographic integrity of a data packet."""
        serialized = json.dumps(data, sort_keys=True).encode()
        expected = hmac.new(self._secret, serialized, hashlib.sha384).hexdigest()
        return hmac.compare_digest(expected, signature)

    def purify_boundary_data(self, raw_data: Dict[str, Any], schema: List[str]) -> Dict[str, Any]:
        """
        FFI BOUNDARY PROTECTION: Strips away non-essential data fields.
        Enforces a 'Least-Access' policy for all external integration.
        """
        return {k: v for k, v in raw_data.items() if k in schema}

    def intercept(self, query: str) -> str:
        """
        Neutralizes adversarial input vectors using refined regex phalanx.
        Isolated within a secure logic sandbox.
        """
        purified = query.strip()
        for pattern in self._sanitization_registry:
            if pattern.search(purified):
                # LEAST PRIVILEGE: Immediate revocation of processing rights
                raise SecurityInterception("ADVERSARIAL_ENTROPY_DETECTED: QUARANTINE_ACTIVE")
        
        # Limit input entropy
        return purified[:2000]

    def seal_response(self, response: Dict[str, Any]) -> str:
        """Applies a cryptographic seal to a systemic output."""
        serialized = json.dumps(response, sort_keys=True).encode()
        return hmac.new(self._secret, serialized, hashlib.sha384).hexdigest()

# [SOVEREIGN PHALANX] Initialization
security_phalanx = ZeroTrustGateway(config.SESSION_SECRET)
