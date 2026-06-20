from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from jay.config import get_settings

settings = get_settings()

qdrant_client = QdrantClient(url="http://localhost:6333", check_compatibility=False)

KNOWLEDGE_COLLECTION = "knowledge_graph"

def init_qdrant():
    """Ensure the collection exists for MiniLM embeddings (384 dims)."""
    try:
        collections = qdrant_client.get_collections().collections
        exists = any(c.name == KNOWLEDGE_COLLECTION for c in collections)
        if not exists:
            qdrant_client.create_collection(
                collection_name=KNOWLEDGE_COLLECTION,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            print(f"Created Qdrant collection: {KNOWLEDGE_COLLECTION}")
    except Exception as e:
        print(f"Failed to initialize Qdrant: {e}")

init_qdrant()
