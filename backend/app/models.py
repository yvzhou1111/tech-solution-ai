from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field

class ModelType(str, Enum):
    DEFAULT = "default"
    LITE = "lite"
    PRO = "pro"
    READER = "reader"

class ProjectStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProjectRequest(BaseModel):
    title: str
    topic: str
    description: Optional[str] = None
    model_type: ModelType = ModelType.DEFAULT
    max_papers: int = Field(default=5, ge=1, le=10)
    custom_keywords: Optional[List[str]] = None
    params: Dict[str, Any] = {}

class PaperInfo(BaseModel):
    id: str
    title: str
    authors: List[str]
    summary: str
    published: str
    pdf_url: str
    local_path: Optional[str] = None
    content_extracted: bool = False

class ProjectResult(BaseModel):
    technical_proposal: str
    architecture_diagram: Optional[str] = None
    implementation_steps: List[Dict[str, str]] = []
    resources_needed: List[Dict[str, str]] = []
    references: List[PaperInfo] = []
    translated_topic: Optional[str] = None

class Project(BaseModel):
    id: str
    title: str
    topic: str
    description: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    status: ProjectStatus
    params: Dict[str, Any] = {}
    result: Optional[ProjectResult] = None

class StreamingResponse(BaseModel):
    event: str
    data: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None

class FileUploadResponse(BaseModel):
    file_id: str
    file_name: str
    file_size: int
    file_type: str
    project_id: Optional[str] = None 