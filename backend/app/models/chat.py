from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

# 聊天会话与文档的关联表
chat_documents = Table(
    'chat_documents',
    Base.metadata,
    Column('chat_id', Integer, ForeignKey('chats.id'), primary_key=True),
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True)
)

class Chat(Base):
    """聊天会话模型"""
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 会话状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    documents = relationship("Document", secondary=chat_documents, back_populates="chats")
    
    def __repr__(self):
        return f"<Chat(id={self.id}, title='{self.title}')>"

class Message(Base):
    """消息模型"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    
    # 关联聊天
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    
    # 消息元数据
    msg_metadata = Column(Text)  # JSON格式，包含引用的文档等信息
    token_count = Column(Integer)  # 令牌数量
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    chat = relationship("Chat", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', chat_id={self.chat_id})>"
