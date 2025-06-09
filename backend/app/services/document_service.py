import os
import uuid
from typing import Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.document import Document
from app.schemas.document import DocumentUpdate
from app.core.config import settings
from app.utils.file_processor import FileProcessor

class DocumentService:
    """文档服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.file_processor = FileProcessor()
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """根据ID获取文档"""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_documents_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
        """获取用户的文档列表"""
        return (
            self.db.query(Document)
            .filter(Document.owner_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_documents(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """获取所有文档列表"""
        return self.db.query(Document).offset(skip).limit(limit).all()
    
    async def upload_document(
        self, 
        file: UploadFile, 
        user_id: int,
        title: Optional[str] = None
    ) -> Document:
        """上传文档"""
        # 验证文件类型
        file_extension = Path(file.filename).suffix.lower().lstrip('.')
        if file_extension not in settings.allowed_extensions_list:
            raise ValueError(f"File type {file_extension} not allowed")
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = Path(settings.UPLOAD_DIR) / unique_filename
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 创建文档记录
        document = Document(
            title=title or file.filename,
            filename=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            file_type=file_extension,
            mime_type=file.content_type,
            owner_id=user_id,
            status="pending"
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        # 自动开始处理文档
        try:
            self.process_document(document.id)
        except Exception as e:
            print(f"自动处理文档失败: {e}")

        return document
    
    def process_document(self, document_id: int) -> bool:
        """处理文档（提取文本内容）"""
        document = self.get_document(document_id)
        if not document:
            return False
        
        try:
            # 更新状态为处理中
            document.status = "processing"
            self.db.commit()
            
            # 提取文本内容
            content = self.file_processor.extract_text(document.file_path)
            
            # 更新文档内容
            document.content = content
            document.status = "completed"
            
            self.db.commit()
            return True
            
        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)
            self.db.commit()
            return False
    
    def update_document(self, document_id: int, document_update: DocumentUpdate) -> Optional[Document]:
        """更新文档"""
        document = self.get_document(document_id)
        if not document:
            return None
        
        update_data = document_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def delete_document(self, document_id: int) -> bool:
        """删除文档"""
        document = self.get_document(document_id)
        if not document:
            return False
        
        # 删除文件
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception:
            pass  # 忽略文件删除错误
        
        # 删除数据库记录
        self.db.delete(document)
        self.db.commit()
        return True
