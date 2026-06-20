import uuid
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

from jay.db_vector import qdrant_client, KNOWLEDGE_COLLECTION
from jay.engines.memory.schemas import NormalizedKnowledge

class MemoryEngine:
    def __init__(self):
        # all-MiniLM-L6-v2 is fast, lightweight, and creates 384-dim vectors
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_and_store(self, knowledge: NormalizedKnowledge) -> str:
        """Embeds the normalized knowledge and stores it in Qdrant with metadata."""
        vector = self.encoder.encode(knowledge.normalized_text).tolist()
        point_id = str(uuid.uuid4())
        
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "text": knowledge.normalized_text,
                "memory_type": knowledge.memory_type.value,
                "importance": knowledge.importance,
                "confidence": knowledge.confidence,
                "mission_relevance": knowledge.mission_relevance
            }
        )
        
        qdrant_client.upsert(
            collection_name=KNOWLEDGE_COLLECTION,
            points=[point]
        )
        
        return point_id

    def semantic_search(self, query: str, memory_type: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches Qdrant for semantically similar knowledge, optionally filtering by type."""
        query_vector = self.encoder.encode(query).tolist()
        
        query_filter = None
        if memory_type:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="memory_type",
                        match=MatchValue(value=memory_type)
                    )
                ]
            )
            
        search_result = qdrant_client.query_points(
            collection_name=KNOWLEDGE_COLLECTION,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k
        )
        
        results = []
        for hit in search_result.points:
            results.append({
                "score": hit.score,
                "text": hit.payload.get("text"),
                "memory_type": hit.payload.get("memory_type"),
                "importance": hit.payload.get("importance"),
                "mission_relevance": hit.payload.get("mission_relevance")
            })
            
        return results
