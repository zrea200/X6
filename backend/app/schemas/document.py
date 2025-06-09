from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentBase(BaseModel):
    """文档基础模式"""
    title: str
    tags: Optional[str] = None

class DocumentCreate(DocumentBase):
    """创建文档模式"""
    pass

class DocumentUpdate(BaseModel):
    """更新文档模式"""
    title: Optional[str] = None
    tags: Optional[str] = None
    summary: Optional[str] = None

class DocumentInDB(DocumentBase):
    """数据库中的文档模式"""
    id: int
    filename: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    is_vectorized: bool
    vector_count: int
    metadata: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Document(DocumentInDB):
    """文档响应模式"""
    pass

class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    message: str
    document_id: int
    filename: str
    status: str

class DocumentSearchRequest(BaseModel):
    """文档搜索请求"""
    query: str
    limit: int = 10
    threshold: float = 0.7

class DocumentSearchResult(BaseModel):
    """文档搜索结果"""
    document_id: int
    title: str
    content: str
    score: float
    metadata: Optional[dict] = None
