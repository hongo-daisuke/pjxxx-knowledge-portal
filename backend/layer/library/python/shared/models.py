from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Visibility(str, Enum):
    PUBLIC = "public"
    DEPARTMENT = "department"
    PRIVATE = "private"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DELETED = "deleted"


class Role(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"


# --- DynamoDB アイテムモデル ---

class DocumentMeta(BaseModel):
    doc_id: str
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    department: str = ""
    visibility: Visibility = Visibility.PUBLIC
    owner_id: str
    latest_version: int = 0
    s3_key: str = ""
    file_type: str = ""
    size: int = 0
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: str = ""
    updated_at: str = ""


class DocumentVersion(BaseModel):
    doc_id: str
    version: int
    s3_key: str
    uploaded_by: str
    uploaded_at: str
    note: str = ""
    size: int = 0


class Tag(BaseModel):
    tag_name: str
    count: int = 0


class ChatHistory(BaseModel):
    user_id: str
    timestamp: str
    question: str
    answer: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    latency_ms: int = 0


# --- API リクエスト/レスポンスモデル ---

class CreateDocumentRequest(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    department: str = ""
    visibility: Visibility = Visibility.PUBLIC
    file_name: str
    content_type: str
    size: int
    idempotency_key: str = ""


class CompleteUploadRequest(BaseModel):
    version: int = 1
    note: str = ""


class UpdateDocumentRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    department: str | None = None
    visibility: Visibility | None = None


class ChatRequest(BaseModel):
    question: str
    session_id: str = ""


class Citation(BaseModel):
    doc_id: str
    title: str
    score: float = 0.0
    s3_uri: str = ""


class ChatResponse(BaseModel):
    answer: str | None
    citations: list[Citation] = Field(default_factory=list)
    no_hit: bool = False


class UserClaims(BaseModel):
    sub: str
    email: str = ""
    department: str = ""
    role: Role = Role.VIEWER
    groups: list[str] = Field(default_factory=list)


class IngestionJobStatus(BaseModel):
    job_id: str
    status: str
    created_at: str = ""
    updated_at: str = ""
    statistics: dict[str, int] = Field(default_factory=dict)
