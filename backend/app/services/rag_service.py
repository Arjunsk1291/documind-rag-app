from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core.node_parser import SentenceSplitter
from pinecone import Pinecone, ServerlessSpec
import logging
from typing import List, Optional
from app.core.config import get_settings
import time
import re

logger = logging.getLogger(__name__)
settings = get_settings()

class RAGService:
    """Service for RAG operations using LlamaIndex and Pinecone"""
    
    def __init__(self):
        self.settings = settings
        self.pc = None
        self.pinecone_index = None
        self.vector_store = None
        self.storage_context = None
        self.llm = None
        self.embed_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone, embeddings, and LLM"""
        try:
            logger.info("Initializing RAG Service...")
            logger.info(f"Using LLM Model: {self.settings.LLM_MODEL}")
            logger.info(f"Using Embedding Model: {self.settings.EMBEDDING_MODEL}")
            
            self.pc = Pinecone(api_key=self.settings.PINECONE_API_KEY)
            index_name = self.settings.PINECONE_INDEX_NAME
            
            try:
                existing_indexes = self.pc.list_indexes()
                if hasattr(existing_indexes, 'indexes'):
                    index_names = [idx.name for idx in existing_indexes.indexes]
                else:
                    index_names = [idx['name'] for idx in existing_indexes]
            except Exception as e:
                logger.warning(f"Error listing indexes: {e}")
                index_names = []
            
            if index_name not in index_names:
                logger.info(f"Creating Pinecone index: {index_name}")
                self.pc.create_index(
                    name=index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info("Waiting for index to be ready...")
                time.sleep(10)
            
            self.pinecone_index = self.pc.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
            
            self.vector_store = PineconeVectorStore(
                pinecone_index=self.pinecone_index
            )
            
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            
            self.embed_model = GeminiEmbedding(
                model_name=self.settings.EMBEDDING_MODEL,
                api_key=self.settings.GOOGLE_API_KEY
            )
            
            self.llm = Gemini(
                model_name=self.settings.LLM_MODEL,
                api_key=self.settings.GOOGLE_API_KEY,
                temperature=0.7
            )
            
            Settings.embed_model = self.embed_model
            Settings.llm = self.llm
            Settings.chunk_size = self.settings.CHUNK_SIZE
            Settings.chunk_overlap = self.settings.CHUNK_OVERLAP
            
            logger.info("RAG Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG Service: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    def index_documents(self, documents: List, doc_id: str) -> bool:
        """Index documents into Pinecone"""
        try:
            logger.info(f"Starting indexing for doc_id: {doc_id}")
            logger.info(f"Number of documents to index: {len(documents)}")
            
            for doc in documents:
                if not hasattr(doc, 'metadata') or doc.metadata is None:
                    doc.metadata = {}
                doc.metadata["doc_id"] = doc_id
                logger.info(f"Document text length: {len(doc.text)}")
            
            node_parser = SentenceSplitter(
                chunk_size=self.settings.CHUNK_SIZE,
                chunk_overlap=self.settings.CHUNK_OVERLAP
            )
            
            nodes = node_parser.get_nodes_from_documents(documents)
            
            logger.info(f"Created {len(nodes)} nodes from documents")
            
            if len(nodes) == 0:
                logger.error("No nodes created from documents!")
                raise ValueError("Failed to create nodes from documents")
            
            logger.info("Creating VectorStoreIndex...")
            index = VectorStoreIndex(
                nodes,
                storage_context=self.storage_context,
                show_progress=True
            )
            
            logger.info(f"Successfully indexed document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    def _clean_mermaid_code(self, text: str) -> Optional[str]:
        """Extract and clean Mermaid code from response"""
        try:
            if "MERMAID_START" in text and "MERMAID_END" in text:
                parts = text.split("MERMAID_START")
                if len(parts) > 1:
                    mermaid_part = parts[1].split("MERMAID_END")[0]
                    code = mermaid_part.strip()
                    
                    code = re.sub(r'```mermaid\n?', '', code)
                    code = re.sub(r'```\n?', '', code)
                    code = code.strip()
                    
                    if not code.startswith(('graph', 'flowchart')):
                        code = 'graph TD\n' + code
                    
                    code = code.replace('"', "'")
                    
                    logger.info(f"Cleaned Mermaid code:\n{code}")
                    return code
            
            return None
        except Exception as e:
            logger.error(f"Error cleaning Mermaid code: {e}")
            return None
    
    def query(
        self, 
        query_text: str, 
        doc_ids: Optional[List[str]] = None,
        return_mindmap: bool = False
    ) -> dict:
        """Query the RAG system"""
        try:
            logger.info(f"Querying: {query_text}")
            logger.info(f"Document IDs for filtering: {doc_ids}")
            
            # Create index from vector store
            index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store
            )
            
            should_mindmap = return_mindmap or self._should_generate_mindmap(query_text)
            
            # Build query engine WITHOUT filters (filters causing issues)
            query_engine = index.as_query_engine(
                similarity_top_k=self.settings.TOP_K,
                response_mode="compact"
            )
            
            logger.info(f"Query engine created with TOP_K={self.settings.TOP_K}")
            
            if should_mindmap:
                mindmap_query = f"""Create a Mermaid.js mind map diagram about: {query_text}

IMPORTANT FORMATTING RULES:
1. Use ONLY simple node labels without special characters
2. Use single quotes for labels, never double quotes
3. Keep labels short (max 4-5 words)
4. Use simple arrows: -->
5. Start with 'graph TD'

Format your response EXACTLY like this:

[2-3 sentence explanation]

MERMAID_START
graph TD
    A[Main Topic] --> B[Subtopic 1]
    A --> C[Subtopic 2]
    B --> D[Detail 1]
    C --> E[Detail 2]
MERMAID_END

Base the diagram ONLY on the provided context."""
                response = query_engine.query(mindmap_query)
            else:
                # Simple, direct prompt
                full_query = f"""Based on the context provided, answer this question:

{query_text}

Provide a clear, detailed answer using only the information in the context."""
                
                logger.info(f"Sending query to LLM: {full_query[:100]}...")
                response = query_engine.query(full_query)
            
            response_text = str(response)
            logger.info(f"Raw response from LLM (first 200 chars): {response_text[:200]}")
            
            mermaid_code = self._clean_mermaid_code(response_text)
            
            if mermaid_code:
                response_text = response_text.split("MERMAID_START")[0].strip()
            
            # Extract sources
            sources = []
            if hasattr(response, 'source_nodes'):
                logger.info(f"Retrieved {len(response.source_nodes)} source nodes")
                for node in response.source_nodes:
                    logger.info(f"Source node metadata: {node.metadata}")
                    logger.info(f"Source node text preview: {node.text[:100]}...")
                sources = [
                    node.metadata.get('file_name', 'Unknown')
                    for node in response.source_nodes
                ]
            
            logger.info(f"Query completed. Response length: {len(response_text)}, Has mindmap: {mermaid_code is not None}")
            
            # If response is too short, it might be an error
            if len(response_text) < 20 and not mermaid_code:
                logger.warning(f"Response too short ({len(response_text)} chars): {response_text}")
                response_text = "I apologize, but I couldn't generate a proper response. This might be due to API quota limits or the query not matching the document content. Please try rephrasing your question."
            
            return {
                "response": response_text,
                "has_mindmap": mermaid_code is not None,
                "mermaid_code": mermaid_code,
                "sources": list(set(sources))
            }
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            logger.exception("Full traceback:")
            
            # Return a friendly error message
            return {
                "response": f"I encountered an error processing your query: {str(e)}. Please try again or rephrase your question.",
                "has_mindmap": False,
                "mermaid_code": None,
                "sources": []
            }
    
    def _should_generate_mindmap(self, query: str) -> bool:
        """Determine if query is asking for a mind map"""
        mindmap_keywords = [
            'mind map', 'mindmap', 'diagram', 'structure', 
            'visualize', 'visualization', 'chart', 'graph',
            'relationship', 'overview', 'summary diagram', 'flow'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in mindmap_keywords)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from vector store"""
        try:
            logger.info(f"Deleting document: {doc_id}")
            self.pinecone_index.delete(filter={"doc_id": {"$eq": doc_id}})
            logger.info(f"Successfully deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document from vector store: {str(e)}")
            return False

rag_service = None

def get_rag_service():
    global rag_service
    if rag_service is None:
        logger.info("Creating RAG service instance...")
        rag_service = RAGService()
    return rag_service
