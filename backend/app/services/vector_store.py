from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader
)
from app.config import settings
from app.services.llm_service import LLMService
from typing import List, Optional
import os
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing document embeddings and retrieval"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Create vector store directory if it doesn't exist
        os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
        
        # Initialize Chroma
        self.vectorstore = Chroma(
            persist_directory=settings.VECTOR_STORE_DIR,
            embedding_function=self.llm_service.embeddings
        )
    
    async def load_document(self, file_path: str) -> List[Document]:
        """Load document based on file type"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension == '.txt':
                loader = TextLoader(file_path)
            elif file_extension == '.docx':
                loader = Docx2txtLoader(file_path)
            elif file_extension == '.csv':
                loader = CSVLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document: {str(e)}")
            raise
    
    async def add_documents(
        self, 
        file_path: str, 
        metadata: Optional[dict] = None
    ) -> int:
        """Add documents to vector store"""
        try:
            # Load documents
            documents = await self.load_document(file_path)
            
            # Add metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vectorstore.add_documents(chunks)
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        filter_metadata: Optional[dict] = None
    ) -> List[Document]:
        """Search for similar documents"""
        try:
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter=filter_metadata
            )
            return results
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    async def get_relevant_context(
        self, 
        query: str, 
        max_chunks: int = 4
    ) -> str:
        """Get relevant context for a query"""
        try:
            documents = await self.similarity_search(query, k=max_chunks)
            
            if not documents:
                return ""
            
            context_parts = []
            for i, doc in enumerate(documents, 1):
                context_parts.append(
                    f"[Source {i}]\n{doc.page_content}\n"
                )
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return ""
    
    def clear_vectorstore(self):
        """Clear all documents from vector store"""
        try:
            self.vectorstore.delete_collection()
            self.vectorstore = Chroma(
                persist_directory=settings.VECTOR_STORE_DIR,
                embedding_function=self.llm_service.embeddings
            )
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise