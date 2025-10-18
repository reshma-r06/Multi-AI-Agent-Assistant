from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.config import settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for managing LLM interactions"""
    
    def __init__(self, model_name: Optional[str] = None, use_anthropic: bool = False):
        self.model_name = model_name or settings.DEFAULT_LLM_MODEL
        self.use_anthropic = use_anthropic
        
        if use_anthropic and settings.ANTHROPIC_API_KEY:
            self.llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                temperature=settings.DEFAULT_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
        else:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=settings.DEFAULT_TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                openai_api_key=settings.OPENAI_API_KEY
            )
        
        # Embeddings for RAG
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """Generate a response from the LLM"""
        try:
            messages = []
            
            if system_message:
                messages.append(SystemMessage(content=system_message))
            
            if context:
                prompt = f"Context:\n{context}\n\nQuery: {prompt}"
            
            messages.append(HumanMessage(content=prompt))
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    async def generate_with_template(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> str:
        """Generate response using a prompt template"""
        try:
            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | self.llm
            response = await chain.ainvoke(variables)
            return response.content
        except Exception as e:
            logger.error(f"Error with template generation: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        try:
            embeddings = await self.embeddings.aembed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            embedding = await self.embeddings.aembed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def get_token_count(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: ~4 characters per token
        return len(text) // 4