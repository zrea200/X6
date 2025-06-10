from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.chat import DocumentSource


class DocumentSearchService:
    """文档搜索服务 - 简化版本"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_documents_by_user(
        self, 
        user_id: int, 
        query: str = "", 
        document_ids: Optional[List[int]] = None,
        limit: int = 5
    ) -> List[DocumentSource]:
        """
        搜索用户的文档
        简化版本：返回用户所有已处理完成的文档内容
        """
        # 构建查询
        query_builder = self.db.query(Document).filter(
            Document.owner_id == user_id,
            Document.status == "completed",
            Document.content.isnot(None)
        )
        
        # 如果指定了文档ID，只搜索这些文档
        if document_ids:
            query_builder = query_builder.filter(Document.id.in_(document_ids))
        
        # 如果有查询关键词，进行简单的文本匹配
        if query.strip():
            query_builder = query_builder.filter(
                Document.content.contains(query)
            )
        
        documents = query_builder.limit(limit).all()
        
        # 转换为DocumentSource格式
        sources = []
        for doc in documents:
            # 获取内容片段（前500个字符）
            content_snippet = doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
            
            source = DocumentSource(
                document_id=doc.id,
                title=doc.title,
                filename=doc.filename,
                content_snippet=content_snippet
            )
            sources.append(source)
        
        return sources
    
    def get_documents_content_for_context(
        self, 
        user_id: int, 
        document_ids: Optional[List[int]] = None,
        max_content_length: int = 3000
    ) -> str:
        """
        获取文档内容作为上下文
        返回合并后的文档内容，用于传递给AI
        """
        # 构建查询
        query_builder = self.db.query(Document).filter(
            Document.owner_id == user_id,
            Document.status == "completed",
            Document.content.isnot(None)
        )
        
        # 如果指定了文档ID，只获取这些文档
        if document_ids:
            query_builder = query_builder.filter(Document.id.in_(document_ids))
        
        documents = query_builder.all()
        
        if not documents:
            return ""
        
        # 合并文档内容
        context_parts = []
        current_length = 0
        
        for doc in documents:
            doc_header = f"\n\n=== 文档：{doc.title} ===\n"
            doc_content = doc.content
            
            # 检查是否会超出长度限制
            if current_length + len(doc_header) + len(doc_content) > max_content_length:
                # 截取部分内容
                remaining_length = max_content_length - current_length - len(doc_header)
                if remaining_length > 100:  # 至少保留100个字符
                    doc_content = doc_content[:remaining_length] + "..."
                    context_parts.append(doc_header + doc_content)
                break
            
            context_parts.append(doc_header + doc_content)
            current_length += len(doc_header) + len(doc_content)
        
        return "\n".join(context_parts)
    
    def get_user_documents_summary(self, user_id: int) -> List[dict]:
        """获取用户文档摘要信息"""
        documents = self.db.query(Document).filter(
            Document.owner_id == user_id,
            Document.status == "completed"
        ).all()
        
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "filename": doc.filename,
                "status": doc.status,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in documents
        ]
