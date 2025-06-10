from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageBase(BaseModel):
    """消息基础模式"""
    content: str
    role: str  # user, assistant, system

class MessageCreate(MessageBase):
    """创建消息模式"""
    chat_id: int

class Message(MessageBase):
    """消息响应模式"""
    id: int
    chat_id: int
    msg_metadata: Optional[str] = None
    token_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    """聊天基础模式"""
    title: str
    description: Optional[str] = None

class ChatCreate(ChatBase):
    """创建聊天模式"""
    pass

class Chat(ChatBase):
    """聊天响应模式"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[Message] = []
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """聊天请求模式"""
    message: str
    chat_id: Optional[int] = None
    use_documents: bool = False  # 默认不使用文档
    document_ids: Optional[List[int]] = None  # 指定要使用的文档ID列表

class DocumentSource(BaseModel):
    """文档来源信息"""
    document_id: int
    title: str
    filename: str
    content_snippet: str

class ChatResponse(BaseModel):
    """聊天响应模式"""
    message: str
    chat_id: int
    sources: Optional[List[DocumentSource]] = None
