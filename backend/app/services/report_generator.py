from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from app.models.schemas import TaskResponse
from datetime import datetime
import markdown
import os
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating downloadable reports"""
    
    def __init__(self):
        self.reports_dir = "data/reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def generate(
        self,
        task: TaskResponse,
        format: str = "pdf",
        include_sources: bool = True
    ) -> str:
        """Generate a report in specified format"""
        
        if format == "pdf":
            return await self.generate_pdf(task, include_sources)
        elif format == "markdown":
            return await self.generate_markdown(task, include_sources)
        elif format == "html":
            return await self.generate_html(task, include_sources)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def generate_pdf(
        self,
        task: TaskResponse,
        include_sources: bool
    ) -> str:
        """Generate PDF report"""
        try:
            filename = f"{task.task_id}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='darkblue',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("Multi-Agent AI Assistant Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Metadata
            meta_style = styles['Normal']
            story.append(Paragraph(f"<b>Task ID:</b> {task.task_id}", meta_style))
            story.append(Paragraph(
                f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                meta_style
            ))
            story.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            heading_style = styles['Heading2']
            story.append(Paragraph("Executive Summary", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            if task.final_answer:
                body_style = ParagraphStyle(
                    'Justify',
                    parent=styles['BodyText'],
                    alignment=TA_JUSTIFY
                )
                story.append(Paragraph(task.final_answer, body_style))
                story.append(Spacer(1, 0.2*inch))
            
            # Agent Responses
            story.append(PageBreak())
            story.append(Paragraph("Detailed Analysis", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            for i, agent_response in enumerate(task.agent_responses, 1):
                agent_heading = ParagraphStyle(
                    'AgentHeading',
                    parent=styles['Heading3'],
                    fontSize=14,
                    textColor='darkgreen'
                )
                story.append(Paragraph(
                    f"{i}. {agent_response.agent_type.value.title()} Agent",
                    agent_heading
                ))
                story.append(Spacer(1, 0.1*inch))
                
                # Agent content
                story.append(Paragraph(agent_response.content, body_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Metadata
                story.append(Paragraph(
                    f"<i>Execution Time: {agent_response.execution_time:.2f}s | "
                    f"Status: {agent_response.status.value}</i>",
                    styles['Italic']
                ))
                story.append(Spacer(1, 0.3*inch))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {filepath}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    async def generate_markdown(
        self,
        task: TaskResponse,
        include_sources: bool
    ) -> str:
        """Generate Markdown report"""
        try:
            filename = f"{task.task_id}.md"
            filepath = os.path.join(self.reports_dir, filename)
            
            content = []
            content.append("# Multi-Agent AI Assistant Report\n")
            content.append(f"**Task ID:** {task.task_id}\n")
            content.append(f"**Generated:** {datetime.utcnow().isoformat()}\n")
            content.append("\n---\n")
            
            content.append("\n## Executive Summary\n")
            content.append(f"{task.final_answer}\n")
            
            content.append("\n## Detailed Analysis\n")
            for i, agent_response in enumerate(task.agent_responses, 1):
                content.append(f"\n### {i}. {agent_response.agent_type.value.title()} Agent\n")
                content.append(f"{agent_response.content}\n")
                content.append(f"\n*Execution Time: {agent_response.execution_time:.2f}s*\n")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            logger.info(f"Markdown report generated: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating Markdown: {str(e)}")
            raise
    
    async def generate_html(
        self,
        task: TaskResponse,
        include_sources: bool
    ) -> str:
        """Generate HTML report"""
        try:
            # First generate markdown
            md_path = await self.generate_markdown(task, include_sources)
            
            # Convert to HTML
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = markdown.markdown(md_content)
            
            # Wrap in HTML structure
            full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Assistant Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; }}
        h2 {{ color: #555; margin-top: 30px; }}
        h3 {{ color: #666; }}
        code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
            
            filename = f"{task.task_id}.html"
            filepath = os.path.join(self.reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            logger.info(f"HTML report generated: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating HTML: {str(e)}")
            raise