from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SUMMARY = "summary"
    REPORT = "report"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    agent_type: Optional[AgentType] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    include_web_search: bool = True
    use_uploaded_docs: bool = False
    generate_report: bool = False


class AgentResponse(BaseModel):
    agent_type: AgentType
    content: str
    status: TaskStatus
    execution_time: float
    sources: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    messages: List[ChatMessage]
    agent_responses: List[AgentResponse]
    final_answer: Optional[str] = None
    report_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class FileUploadResponse(BaseModel):
    filename: str
    file_id: str
    size: int
    content_type: str
    processed: bool
    chunks_created: Optional[int] = None


class ReportRequest(BaseModel):
    task_id: str
    format: str = "pdf"  # pdf, markdown, html
    include_sources: bool = True


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)