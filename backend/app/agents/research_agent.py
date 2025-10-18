from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.services.llm_service import LLMService
from app.tools.web_search import WebSearchTool
from app.models.schemas import AgentResponse, AgentType, TaskStatus
from typing import Dict, Any
import time
import logging

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Agent responsible for gathering information through web searches"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.web_search = WebSearchTool()
        self.agent_type = AgentType.RESEARCH
        
        # Define the agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Research Agent specialized in gathering comprehensive information.
Your role is to:
1. Search for relevant, up-to-date information on the web
2. Gather data from multiple sources
3. Focus on factual, credible information
4. Organize findings clearly

When researching:
- Perform multiple searches if needed to cover different aspects
- Look for recent data and statistics
- Identify key trends and patterns
- Note credible sources

Always be thorough and analytical in your research."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create tools
        self.tools = [
            self.web_search.as_langchain_tool()
        ]
    
    async def execute(self, query: str) -> AgentResponse:
        """Execute the research agent"""
        start_time = time.time()
        
        try:
            logger.info(f"Research Agent executing query: {query}")
            
            # Create the agent
            agent = create_openai_functions_agent(
                llm=self.llm_service.llm,
                tools=self.tools,
                prompt=self.prompt
            )
            
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=5
            )
            
            # Execute the agent
            result = await agent_executor.ainvoke({"input": query})
            
            execution_time = time.time() - start_time
            
            return AgentResponse(
                agent_type=self.agent_type,
                content=result["output"],
                status=TaskStatus.COMPLETED,
                execution_time=execution_time,
                metadata={"iterations": result.get("iterations", 0)}
            )
            
        except Exception as e:
            logger.error(f"Research Agent error: {str(e)}")
            execution_time = time.time() - start_time
            
            return AgentResponse(
                agent_type=self.agent_type,
                content=f"Error during research: {str(e)}",
                status=TaskStatus.FAILED,
                execution_time=execution_time
            )


class AnalysisAgent:
    """Agent responsible for analyzing gathered information"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.agent_type = AgentType.ANALYSIS
    
    async def execute(
        self, 
        query: str, 
        research_data: str,
        context: str = ""
    ) -> AgentResponse:
        """Execute the analysis agent"""
        start_time = time.time()
        
        try:
            logger.info("Analysis Agent executing")
            
            system_message = """You are an Analysis Agent specialized in deep analytical thinking.
Your role is to:
1. Analyze the research data provided
2. Identify key insights and patterns
3. Draw meaningful conclusions
4. Provide data-driven recommendations

Focus on:
- Critical analysis of information
- Comparing different perspectives
- Identifying opportunities and risks
- Quantitative and qualitative insights"""

            prompt = f"""Research Data:
{research_data}

Additional Context:
{context}

Query: {query}

Provide a comprehensive analysis based on the research data."""
            
            response = await self.llm_service.generate_response(
                prompt=prompt,
                system_message=system_message
            )
            
            execution_time = time.time() - start_time
            
            return AgentResponse(
                agent_type=self.agent_type,
                content=response,
                status=TaskStatus.COMPLETED,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Analysis Agent error: {str(e)}")
            execution_time = time.time() - start_time
            
            return AgentResponse(
                agent_type=self.agent_type,
                content=f"Error during analysis: {str(e)}",
                status=TaskStatus.FAILED,
                execution_time=execution_time
            )