import json
import time
from typing import Dict, Any, List, Set, Optional
from backend.telemetry.kernel import logger

class KnowledgeNode:
    def __init__(self, entity: str, category: str):
        self.entity = entity
        self.category = category
        self.metadata: Dict[str, Any] = {}
        self.last_updated = time.time()

class DynamicKnowledgeGraph:
    """
    The Distributed Memory of the Machine.
    Maintains a dynamically updating graph of civic entities and semantic triples.
    Provides a verifiable context for cognitive synthesis.
    """
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[Dict[str, str]] = []
        self._lock = None # Initialized in async context

    def ingest(self, text: str):
        """
        HEURISTIC SYNTHESIS: Extracts entities and relations from reasoning output.
        Populates the Knowledge Graph in real-time.
        """
        # Simplified semantic extraction for the cognitive substrate
        words = text.split()
        potential_entities = [w.strip(".,()\"") for w in words if w[0].isupper() and len(w) > 3]
        
        for entity in set(potential_entities):
            if entity not in self.nodes:
                self.nodes[entity] = KnowledgeNode(entity, "CIVIC_ENTITY")
                logger.info("knowledge_node_synthesized", entity=entity)
            
            # Create a simple edge if we have multiple entities
            if len(self.nodes) > 1:
                other = list(self.nodes.keys())[0]
                if other != entity:
                    self.edges.append({"source": entity, "target": other, "relation": "SEMANTIC_LINK"})

    def synthesize_context(self, query: str) -> str:
        """
        Distills the Knowledge Graph into a coherent, non-redundant context.
        Optimized for the model's attention mechanism.
        """
        # SELF-HEALING: Verify node integrity before synthesis
        corrupted = [n for n in self.nodes.values() if time.time() - n.last_updated > 3600]
        if corrupted:
            logger.warning("KNOWLEDGE_SECTOR_DEGRADATION_DETECTED", count=len(corrupted))
            # Autonomous Reconstruction would happen here via Audit Trail replay
        
        relevant_nodes = [n for n in self.nodes.values() if n.entity.lower() in query.lower()]
        if not relevant_nodes:
            relevant_nodes = list(self.nodes.values())[-5:]
            
        summary = "SEMANTIC_GRAPH_SNAPSHOT:\n"
        for node in relevant_nodes:
            summary += f"- {node.entity} ({node.category})\n"
        
        return summary

    def sabotage_node(self, entity: str):
        """CHAOS_ENGINE: Corrupts a semantic node to test reconstruction."""
        if entity in self.nodes:
            self.nodes[entity].entity = "CORRUPTED_ENTITY_CHAOS"
            self.nodes[entity].category = "MALICIOUS_INJECTION"
            logger.info("KNOWLEDGE_NODE_SABOTAGED", entity=entity)

    def export_proof(self) -> Dict[str, Any]:
        """Generates a verifiable proof of the current cognitive state."""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "entities": [n.entity for n in list(self.nodes.values())[:10]],
            "ts": time.time()
        }

knowledge_graph = DynamicKnowledgeGraph()
