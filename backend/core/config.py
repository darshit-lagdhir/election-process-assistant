import os
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

T = TypeVar("T")

class ConfigSchema(BaseModel):
    """The Rigorous Behavioral Schema of the Hadron Core."""
    PROJECT_NAME: str = "Hadron Core Election Assistant"
    ARCHITECTURAL_VERSION: str = "9.0.0-AGNOSTIC"
    CODENAME: str = "PORTABILITY_MATRIX_IGNITION"
    
    # NETWORK PARAMETERS
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # REASONING PARAMETERS
    AI_MODEL_PRIMARY: str = "gemini-flash-latest"
    MODEL_FALLBACK_CHAIN: List[str] = [
        "gemini-flash-latest", "gemini-flash-latest"
    ]
    MAX_OUTPUT_TOKENS: int = 1024
    TEMPERATURE_STABILITY: float = 0.1
    REASONING_TIMEOUT: float = 25.0  
    MODEL_BLACKLIST_COOLDOWN: int = 600   
    
    # METABOLIC PERIMETERS
    METABOLIC_FLOOR_MB: float = 10.0 
    TARGET_BASELINE_MB: float = 150.0 
    CRITICAL_CEILING_MB: float = 512.0 
    CPU_CONCURRENCY_THRESHOLD: int = 1000 
    
    # TELEMETRY & SECURITY
    WS_HEARTBEAT_INTERVAL: float = 2.0
    DATA_HYDRATION_TTL: int = 300
    SESSION_SECRET: str = "TRANSCENDENT_HADRON_SYNTHESIS_2026"
    TLS_PROTOCOL: str = "TLSv1.3"
    HMAC_ALGORITHM: Any = hashlib.sha384

    def get_api_key(self) -> Optional[str]:
        """Provides the validated AI API Key from the execution substrate."""
        return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

class ConfigurationProvider:
    """
    The Hierarchical Configuration Conduit.
    Queries environment variables, secret managers, and defaults with absolute type safety.
    """
    def __init__(self):
        load_dotenv()
        self._raw_config = self._hydrate_hierarchy()
        try:
            self.schema = ConfigSchema(**self._raw_config)
        except ValidationError as e:
            print(f"!!! CRITICAL CONFIGURATION FAULT: {e}")
            # Fallback to defaults to prevent system collapse
            self.schema = ConfigSchema()

        # DYNAMIC PATH RESOLUTION (ABSOLUTE AGNOSTICISM)
        self.BASE_DIR: Path = Path(__file__).resolve().parent.parent
        self.ROOT_DIR: Path = self.BASE_DIR.parent
        self.DATA_DIR: Path = self.ROOT_DIR / "data"
        self.LOGS_DIR: Path = self.ROOT_DIR / "logs"
        self.DATA_PATH: Path = self.DATA_DIR / "election_substrate.json"
        self.LOG_PATH: Path = self.LOGS_DIR / "hadron_forensics.log"

    def _hydrate_hierarchy(self) -> Dict[str, Any]:
        """Implements the multi-tiered lookup strategy."""
        defaults = ConfigSchema().model_dump()
        hydrated = {}
        for key in defaults.keys():
            # Hierarchy: Env Var -> Default
            val = os.getenv(key)
            if val is not None:
                # Handle list types for fallback chain
                if key == "MODEL_FALLBACK_CHAIN" and isinstance(val, str):
                    hydrated[key] = [m.strip() for m in val.split(",")]
                elif key == "PORT" and isinstance(val, str):
                    hydrated[key] = int(val)
                else:
                    hydrated[key] = val
            else:
                hydrated[key] = defaults[key]
        
        # Special handling for secrets
        hydrated["SESSION_SECRET"] = os.getenv("SESSION_SECRET", defaults["SESSION_SECRET"])
        return hydrated

    def get_api_key(self) -> Optional[str]:
        """Provides the validated AI API Key from the execution substrate."""
        return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# The Global Portability Matrix Interface
provider = ConfigurationProvider()
config = provider.schema
paths = provider # Path resolution interface

class HadronEvent(BaseModel):
    """The Atomic Unit of Systemic Logic and Inter-Module Communication."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sector: str
    type: str
    payload: Dict[str, Any]
    radiance: float = 100.0
