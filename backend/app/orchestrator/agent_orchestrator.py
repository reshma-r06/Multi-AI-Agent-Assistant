from app.agents.research_agent import ResearchAgent, AnalysisAgent
from app.agents.summary_agent import SummaryAgent, ReportAgent
from app.services.vector_store import VectorStoreService
from app.models.schemas import (
    TaskResponse, 
    AgentResponse, 
    ChatMessage, 
    MessageRole,
    TaskStatus
)
from typing import List, Optional
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple agents to complete complex tasks"""
    
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.analysis_agent = AnalysisAgent()
        self.summary_agent = SummaryAgent()
        self.report_agent = ReportAgent()
        self.vector_store = VectorStoreService()
    
    async def execute_task(
        self,
        query: str,
        use_web_search: bool = True,
        use_uploaded_docs: bool = False,
        generate_report: bool = False
    ) -> TaskResponse:
        """Execute a complete multi-agent task"""
        
        task_id = str(uuid.uuid4())
        messages: List[ChatMessage] = []
        agent_responses: List[AgentResponse] = []
        
        logger.info(f"Starting task {task_id} for query: {query}")
        
        try:
            # Step 1: Get context from uploaded documents if requested
            context = ""
            if use_uploaded_docs:
                logger.info("Retrieving context from uploaded documents")
                context = await self.vector_store.get_relevant_context(query)
                
                if context:
                    messages.append(ChatMessage(
                        role=MessageRole.SYSTEM,
                        content=f"Retrieved context from documents:\n{context[:500]}..."
                    ))
            
            # Step 2: Research Phase
            research_response = None
            if use_web_search:
                logger.info("Executing Research Agent")
                research_response = await self.research_agent.execute(query)
                agent_responses.append(research_response)
                
                messages.append(ChatMessage(
                    role=MessageRole.AGENT,
                    content=f"Research completed: {research_response.content[:200]}...",
                    agent_type=research_response.agent_type
                ))
            
            # Step 3: Analysis Phase
            logger.info("Executing Analysis Agent")
            research_data = research_response.content if research_response else "No web research performed"
            analysis_response = await self.analysis_agent.execute(
                query=query,
                research_data=research_data,
                context=context
            )
            agent_responses.append(analysis_response)
            
            messages.append(ChatMessage(
                role=MessageRole.AGENT,
                content=f"Analysis completed: {analysis_response.content[:200]}...",
                agent_type=analysis_response.agent_type
            ))
            
            # Step 4: Summary Phase
            logger.info("Executing Summary Agent")
            summary_response = await self.summary_agent.execute(
                query=query,
                research_data=research_data,
                analysis_data=analysis_response.content
            )
            agent_responses.append(summary_response)
            
            messages.append(ChatMessage(
                role=MessageRole.AGENT,
                content=summary_response.content,
                agent_type=summary_response.agent_type
            ))
            
            # Step 5: Report Generation (if requested)
            report_response = None
            if generate_report:
                logger.info("Executing Report Agent")
                report_response = await self.report_agent.execute(
                    query=query,
                    research_data=research_data,
                    analysis_data=analysis_response.content,
                    summary_data=summary_response.content
                )
                agent_responses.append(report_response)
                
                messages.append(ChatMessage(
                    role=MessageRole.AGENT,
                    content="Report generated successfully",
                    agent_type=report_response.agent_type
                ))
            
            # Prepare final response
            final_answer = summary_response.content
            
            # Add final message
            messages.append(ChatMessage(
                role=MessageRole.ASSISTANT,
                content=final_answer
            ))
            
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                messages=messages,
                agent_responses=agent_responses,
                final_answer=final_answer,
                report_url=f"/api/reports/{task_id}" if generate_report else None,
                completed_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error in task execution: {str(e)}")
            
            messages.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content=f"Error occurred: {str(e)}"
            ))
            
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                messages=messages,
                agent_responses=agent_responses,
                final_answer=f"Task failed: {str(e)}",
                completed_at=datetime.utcnow()
            )
    
    async def stream_task_execution(self, query: str, **kwargs):
        """Stream task execution updates (for WebSocket)"""
        # This can be implemented for real-time updates
        pass