from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    id: str
    original_name: str
    file_size: int
    mime_type: str
    status: DocumentStatus
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
