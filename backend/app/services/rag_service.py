from llama_index.core import VectorStoreIndex, StorageContext, Settings, Document
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.core.node_parser import SentenceSplitter
from pinecone import Pinecone, ServerlessSpec
import logging
from typing import List, Optional, Dict
from app.core.config import get_settings
import time
import re

logger = logging.getLogger(__name__)
settings = get_settings()

class RAGService:
    """Service for RAG operations using LlamaIndex and Pinecone with CAD integration"""
    
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
                temperature=0.8
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
    
    def index_cad_analysis(self, doc_id: str, analysis_results: Dict, doc_name: str) -> bool:
        """
        Index CAD vision analysis results into the unified RAG system
        
        Args:
            doc_id: Document ID
            analysis_results: Results from comprehensive_analysis()
            doc_name: Original document name
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"🔧 Indexing CAD analysis for {doc_name} (doc_id: {doc_id})")
            
            # Create Document objects for each stage
            stage_documents = []
            
            # Stage 1: Document Identification
            if 'stage_1_identification' in analysis_results:
                doc1 = Document(
                    text=f"CAD DOCUMENT IDENTIFICATION - {doc_name}\n\n{analysis_results['stage_1_identification']}",
                    metadata={
                        'doc_id': doc_id,
                        'file_name': doc_name,
                        'file_type': 'cad',
                        'source_type': 'cad_analysis',
                        'analysis_stage': 'identification',
                        'model_used': analysis_results.get('model_used', 'unknown')
                    }
                )
                stage_documents.append(doc1)
            
            # Stage 2: System Overview
            if 'stage_2_system_overview' in analysis_results:
                doc2 = Document(
                    text=f"CAD SYSTEM OVERVIEW - {doc_name}\n\n{analysis_results['stage_2_system_overview']}",
                    metadata={
                        'doc_id': doc_id,
                        'file_name': doc_name,
                        'file_type': 'cad',
                        'source_type': 'cad_analysis',
                        'analysis_stage': 'system_overview',
                        'model_used': analysis_results.get('model_used', 'unknown')
                    }
                )
                stage_documents.append(doc2)
            
            # Stage 3: Components
            if 'stage_3_components' in analysis_results:
                doc3 = Document(
                    text=f"CAD COMPONENT BREAKDOWN - {doc_name}\n\n{analysis_results['stage_3_components']}",
                    metadata={
                        'doc_id': doc_id,
                        'file_name': doc_name,
                        'file_type': 'cad',
                        'source_type': 'cad_analysis',
                        'analysis_stage': 'components',
                        'model_used': analysis_results.get('model_used', 'unknown')
                    }
                )
                stage_documents.append(doc3)
            
            # Stage 4: Technical Characteristics
            if 'stage_4_technical' in analysis_results:
                doc4 = Document(
                    text=f"CAD TECHNICAL CHARACTERISTICS - {doc_name}\n\n{analysis_results['stage_4_technical']}",
                    metadata={
                        'doc_id': doc_id,
                        'file_name': doc_name,
                        'file_type': 'cad',
                        'source_type': 'cad_analysis',
                        'analysis_stage': 'technical',
                        'model_used': analysis_results.get('model_used', 'unknown')
                    }
                )
                stage_documents.append(doc4)
            
            # Stage 5: Quality Assessment
            if 'stage_5_quality' in analysis_results:
                doc5 = Document(
                    text=f"CAD QUALITY & USABILITY - {doc_name}\n\n{analysis_results['stage_5_quality']}",
                    metadata={
                        'doc_id': doc_id,
                        'file_name': doc_name,
                        'file_type': 'cad',
                        'source_type': 'cad_analysis',
                        'analysis_stage': 'quality',
                        'model_used': analysis_results.get('model_used', 'unknown')
                    }
                )
                stage_documents.append(doc5)
            
            # Create complete analysis summary document
            summary_text = f"""CAD COMPLETE ANALYSIS - {doc_name}

Model Used: {analysis_results.get('model_used', 'Unknown')}
Provider: {analysis_results.get('provider_used', 'Unknown')}

IDENTIFICATION:
{analysis_results.get('stage_1_identification', 'N/A')}

SYSTEM OVERVIEW:
{analysis_results.get('stage_2_system_overview', 'N/A')}

COMPONENTS:
{analysis_results.get('stage_3_components', 'N/A')}

TECHNICAL:
{analysis_results.get('stage_4_technical', 'N/A')}

QUALITY:
{analysis_results.get('stage_5_quality', 'N/A')}
"""
            
            doc_summary = Document(
                text=summary_text,
                metadata={
                    'doc_id': doc_id,
                    'file_name': doc_name,
                    'file_type': 'cad',
                    'source_type': 'cad_analysis_summary',
                    'analysis_stage': 'complete',
                    'model_used': analysis_results.get('model_used', 'unknown')
                }
            )
            stage_documents.append(doc_summary)
            
            # Index all stage documents
            logger.info(f"Indexing {len(stage_documents)} CAD analysis documents...")
            success = self.index_documents(stage_documents, f"{doc_id}_cad_analysis")
            
            if success:
                logger.info(f"✅ CAD analysis indexed successfully for {doc_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error indexing CAD analysis: {str(e)}")
            logger.exception("Full traceback:")
            return False
    
    def query(self, query_text: str, doc_ids: List[str] = None, return_mindmap: bool = False) -> dict:
        """Query the RAG system with optional document filtering"""
        try:
            logger.info(f"Query: {query_text}")
            logger.info(f"Filtering by doc_ids: {doc_ids}")
            
            # Create query engine with filtering
            if doc_ids and len(doc_ids) > 0:
                from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
                
                filters = MetadataFilters(
                    filters=[
                        MetadataFilter(
                            key="doc_id",
                            value=doc_ids,
                            operator=FilterOperator.IN
                        )
                    ]
                )
                
                index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=self.storage_context
                )
                
                query_engine = index.as_query_engine(
                    similarity_top_k=self.settings.TOP_K,
                    filters=filters
                )
            else:
                index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=self.storage_context
                )
                query_engine = index.as_query_engine(
                    similarity_top_k=self.settings.TOP_K
                )
            
            # Execute query
            response = query_engine.query(query_text)
            
            # Extract sources
            sources = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    source_info = {
                        'text': node.node.text[:200] + "..." if len(node.node.text) > 200 else node.node.text,
                        'score': float(node.score) if hasattr(node, 'score') else 0.0,
                        'metadata': node.node.metadata if hasattr(node.node, 'metadata') else {}
                    }
                    sources.append(source_info)
            
            # Check if mind map requested
            has_mindmap = False
            mermaid_code = None
            
            if return_mindmap:
                has_mindmap, mermaid_code = self._extract_mindmap(str(response))
            else:
                has_mindmap, mermaid_code = self._check_for_mindmap(query_text, str(response))
            
            return {
                "response": str(response),
                "sources": sources,
                "has_mindmap": has_mindmap,
                "mermaid_code": mermaid_code
            }
            
        except Exception as e:
            logger.error(f"Error in query: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    def _check_for_mindmap(self, query: str, response: str) -> tuple:
        """Check if response contains or should contain a mind map"""
        mindmap_keywords = ['mind map', 'mindmap', 'diagram', 'visualize', 'flowchart', 'structure']
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in mindmap_keywords):
            has_mindmap, code = self._extract_mindmap(response)
            return has_mindmap, code
        
        return False, None
    
    def _extract_mindmap(self, response: str) -> tuple:
        """Extract Mermaid code from response"""
        import re
        
        patterns = [
            r'```mermaid\n(.*?)\n```',
            r'```\n(graph .*?)\n```',
            r'(graph (?:TB|TD|LR|RL)\n.*?)(?:\n\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                return True, match.group(1).strip()
        
        return False, None

_rag_service_instance = None

def get_rag_service() -> RAGService:
    """Get singleton RAG service instance"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
