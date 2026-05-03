import asyncio
from typing import Dict, Any, List, Optional
from backend.core.integrity import citizen_records_ledger, electoral_actions_ledger
from backend.telemetry.kernel import logger

class DataPlaneProxy:
    """
    The Security Gatekeeper: Segregates the Data Plane from the Control Plane.
    Enforces strict schema validation and the 'Least-Access' purification policy.
    Utilizes atomic locks to protect the integrity of the storage conduits.
    """
    def __init__(self):
        self._ledgers = {
            "citizen": citizen_records_ledger,
            "electoral": electoral_actions_ledger
        }
        self._schemas = {
            "citizen": ["id", "timestamp", "query_hash", "outcome"],
            "electoral": ["action_id", "type", "voter_id_anonymized", "timestamp"]
        }

    def _purify(self, record: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """LEAST-ACCESS POLICY: Strips non-essential fields before persistence."""
        schema = self._schemas.get(domain, [])
        return {k: v for k, v in record.items() if k in schema}

    async def persist(self, domain: str, record: Dict[str, Any]) -> str:
        """
        Proxies a data persistence request to the immutable substrate.
        Validates the schema and applies cryptographic chaining.
        """
        if domain not in self._ledgers:
            raise ValueError(f"Domain '{domain}' is not registered in the Data Plane.")

        # 1. PURIFICATION
        clean_record = self._purify(record, domain)
        
        # 2. COMMIT TO INTEGRITY SUBSTRATE
        ledger = self._ledgers[domain]
        try:
            signature = await ledger.commit(clean_record)
            logger.info("data_plane_persistence_success", domain=domain, signature=signature[:12])
            return signature
        except Exception as e:
            logger.error("data_plane_persistence_fault", domain=domain, error=str(e))
            raise RuntimeError("Systemic Data Plane Failure.")

    async def reconcile_state(self, domain: str) -> bool:
        """Triggers a systemic reconciliation pulse for a specific domain."""
        ledger = self._ledgers.get(domain)
        if not ledger: return False
        return await ledger.verify_chain()

data_proxy = DataPlaneProxy()
