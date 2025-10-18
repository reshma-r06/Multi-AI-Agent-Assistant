from app.services.llm_service import LLMService
from app.models.schemas import AgentResponse, AgentType, TaskStatus
import time
import logging

logger = logging.getLogger(__name__)


class SummaryAgent:
    """Agent responsible for creating concise summaries"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.agent_type = AgentType.SUMMARY
    
    async def execute(
        self, 
        query: str,
        research_data: str,
        analysis_data: str
    ) -> AgentResponse:
        """Execute the summary agent"""
        start_time = time.time()
        
        try:
            logger.info("Summary Agent executing")
            
            system_message = """You are a Summary Agent specialized in creating clear, concise summaries.
Your role is to:
1. Distill complex information into key points
2. Highlight the most important findings
3. Create actionable takeaways
4. Use clear, accessible language

Create summaries that are:
- Concise yet comprehensive
- Well-structured with bullet points
- Focused on actionable insights
- Easy to understand for non-technical audiences"""

            prompt = f"""Original Query: {query}

Research Findings:
{research_data}

Analysis:
{analysis_data}

Create a concise summary that captures the key findings, insights, and actionable recommendations."""
            
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
            logger.error(f"Summary Agent error: {str(e)}")
            execution_time = time.time() - start_time
            
            return AgentResponse(
                agent_type=self.agent_type,
                content=f"Error creating summary: {str(e)}",
                status=TaskStatus.FAILED,
                execution_time=execution_time
            )


class ReportAgent:
    """Agent responsible for generating formatted reports"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.agent_type = AgentType.REPORT
    
    async def execute(
        self,
        query: str,
        research_data: str,
        analysis_data: str,
        summary_data: str
    ) -> AgentResponse:
        """Execute the report agent"""
        start_time = time.time()
        
        try:
            logger.info("Report Agent executing")
            
            system_message = """You are a Report Agent specialized in creating professional, structured reports.
Your role is to:
1. Organize information in a clear structure
2. Create professional documentation
3. Include executive summaries
4. Provide comprehensive yet readable reports

Report Structure:
- Executive Summary
- Key Findings
- Detailed Analysis
- Recommendations
- Conclusion

Use markdown formatting for clarity."""

            prompt = f"""Create a comprehensive report for the following query:

Query: {query}

Research Data:
{research_data}

Analysis:
{analysis_data}

Summary:
{summary_data}

Generate a well-structured, professional report in markdown format."""
            
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
            logger.error(f"Report Agent error: {str(e)}")
            execution_time = time.time() - start_time
            
            return AgentResponse(
                agent_type=self.agent_type,
                content=f"Error generating report: {str(e)}",
                status=TaskStatus.FAILED,
                execution_time=execution_time
            )