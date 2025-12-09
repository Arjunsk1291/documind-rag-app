from app.services.rag_service import get_rag_service
import logging

logging.basicConfig(level=logging.INFO)

rag = get_rag_service()

query = "What is this document about?"
result = rag.query(query)

print("\n=== RESULT ===")
print(f"Response: {result['response']}")
print(f"Has mindmap: {result['has_mindmap']}")
print(f"Sources: {result['sources']}")
