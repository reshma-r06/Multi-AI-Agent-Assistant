from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.models.schemas import (
    QueryRequest,
    TaskResponse,
    FileUploadResponse,
    ReportRequest,
    HealthResponse
)
from app.orchestrator.agent_orchestrator import AgentOrchestrator
from app.services.vector_store import VectorStoreService
from app.services.report_generator import ReportGenerator
from app.config import settings
import aiofiles
import os
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# Initialize services
orchestrator = AgentOrchestrator()
vector_store = VectorStoreService()
report_generator = ReportGenerator()

# In-memory storage for tasks (use Redis/DB in production)
tasks_storage = {}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION
    )


@router.post("/query", response_model=TaskResponse)
async def process_query(request: QueryRequest):
    """Process a user query through the multi-agent system"""
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Execute the multi-agent task
        task_response = await orchestrator.execute_task(
            query=request.query,
            use_web_search=request.include_web_search,
            use_uploaded_docs=request.use_uploaded_docs,
            generate_report=request.generate_report
        )
        
        # Store task response
        tasks_storage[task_response.task_id] = task_response
        
        return task_response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task status and results"""
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks_storage[task_id]


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload a document for RAG"""
    try:
        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        # Process file in background
        chunks_created = None
        try:
            chunks_created = await vector_store.add_documents(
                file_path=file_path,
                metadata={
                    "file_id": file_id,
                    "filename": file.filename,
                    "upload_time": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
        
        return FileUploadResponse(
            filename=file.filename,
            file_id=file_id,
            size=file_size,
            content_type=file.content_type or "application/octet-stream",
            processed=chunks_created is not None,
            chunks_created=chunks_created
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate")
async def generate_report(request: ReportRequest):
    """Generate a downloadable report"""
    try:
        if request.task_id not in tasks_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = tasks_storage[request.task_id]
        
        # Generate report
        report_path = await report_generator.generate(
            task=task,
            format=request.format,
            include_sources=request.include_sources
        )
        
        return {
            "report_url": f"/api/reports/download/{request.task_id}",
            "format": request.format
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/clear")
async def clear_documents():
    """Clear all uploaded documents from vector store"""
    try:
        vector_store.clear_vectorstore()
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))