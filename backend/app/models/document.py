from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Document(Base):
    """文档模型"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger)  # 文件大小（字节）
    file_type = Column(String(50))  # 文件类型
    mime_type = Column(String(100))
    
    # 文档内容
    content = Column(Text)  # 提取的文本内容
    summary = Column(Text)  # 文档摘要
    
    # 处理状态
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)  # 错误信息
    
    # 向量化信息
    is_vectorized = Column(Boolean, default=False)
    vector_count = Column(Integer, default=0)  # 向量数量
    
    # 元数据
    doc_metadata = Column(Text)  # JSON格式的元数据
    tags = Column(String(500))  # 标签，逗号分隔
    
    # 关联用户
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))  # 处理完成时间
    
    # 关系
    owner = relationship("User", back_populates="documents")
    chats = relationship("Chat", secondary="chat_documents", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', status='{self.status}')>"
