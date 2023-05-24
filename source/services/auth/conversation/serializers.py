from datetime import datetime
from typing import Optional, Dict, List

from pydantic import BaseModel

from services.auth.util.settings import settings


class EmbeddingsRes(BaseModel):
    created_at: datetime
    updated_at: datetime
    open_id: str
    message_id: str
    model: str
    input: str
    embedding: str


class CompletionSimpleRes(BaseModel):
    created_at: datetime
    updated_at: datetime
    open_id: str
    message_id: str
    model: str
    prompt: str
    content: str


class CompletionDetailRes(BaseModel):
    created_at: datetime
    updated_at: datetime
    open_id: str
    message_id: str
    model: str
    prompt: str
    content: Optional[str]
    max_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
    stop: Optional[str]
    stream: Optional[bool]
    logprobs: Optional[int]


class ConversationListRes(BaseModel):
    conversation_id: Optional[str]
    open_id: Optional[str]
    title: Optional[str]
    created_at: datetime
    updated_at: datetime


class ChatCompletionRes(BaseModel):
    created_at: datetime
    message_id: str
    model: str
    role: str
    content: str
    name: Optional[str]
    parent: Optional[str]
    children: Optional[List]
    top_p: float
    temperature: float
    stream: bool


class ConversationDetailRes(BaseModel):
    title: str
    created_at: datetime
    updated_at: datetime
    conversation_id: str
    open_id: str
    mapping: Dict[str, ChatCompletionRes]

