from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.conversation import MessageRole


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    document_id: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse]


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: List[str]
