import os
import uuid
import logging
from typing import Optional, List
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.document import Document
from app.schemas.document import DocumentUpdate, DocumentSearchRequest, DocumentSearchResult
from app.core.config import settings
from app.utils.file_processor import FileProcessor
from app.services.vector_service import milvus_service
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

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
        """处理文档（提取文本内容并向量化）"""
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

            # 向量化处理
            success = self._vectorize_document(document, content)

            if success:
                document.status = "completed"
                document.is_vectorized = True
            else:
                document.status = "completed"  # 文本提取成功，但向量化失败
                document.is_vectorized = False
                logger.warning(f"Document {document_id} processed but vectorization failed")

            self.db.commit()
            return True

        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)
            self.db.commit()
            logger.error(f"Failed to process document {document_id}: {e}")
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
        
        # 删除向量数据
        try:
            milvus_service.delete_document_vectors(document_id)
        except Exception as e:
            logger.warning(f"Failed to delete vectors for document {document_id}: {e}")

        # 删除数据库记录
        self.db.delete(document)
        self.db.commit()
        return True

    def _vectorize_document(self, document: Document, content: str) -> bool:
        """将文档内容向量化并存储到Milvus"""
        try:
            # 确保Milvus集合存在
            dimension = embedding_service.get_embedding_dimension()
            if not milvus_service.create_collection(dimension):
                logger.error("Failed to create Milvus collection")
                return False

            # 文本分块
            chunks = embedding_service.chunk_text(content)
            if not chunks:
                logger.warning(f"No chunks generated for document {document.id}")
                return False

            # 生成嵌入向量
            embeddings = embedding_service.encode_documents(chunks)
            if not embeddings:
                logger.error(f"Failed to generate embeddings for document {document.id}")
                return False

            # 准备元数据
            metadata = [f"doc_{document.id}_chunk_{i}" for i in range(len(chunks))]

            # 存储到Milvus
            success = milvus_service.insert_vectors(
                document_id=document.id,
                chunks=chunks,
                embeddings=embeddings,
                metadata=metadata
            )

            if success:
                # 更新向量数量
                document.vector_count = len(chunks)
                logger.info(f"Successfully vectorized document {document.id} with {len(chunks)} chunks")

            return success

        except Exception as e:
            logger.error(f"Failed to vectorize document {document.id}: {e}")
            return False

    def search_documents(self, search_request: DocumentSearchRequest, user_id: int = None) -> List[DocumentSearchResult]:
        """搜索文档"""
        try:
            # 生成查询向量
            query_embedding = embedding_service.encode_query(search_request.query)

            # 在Milvus中搜索
            similar_chunks = milvus_service.search_similar(
                query_embedding=query_embedding,
                limit=search_request.limit * 2,  # 获取更多结果用于重排序
                score_threshold=search_request.threshold
            )

            if not similar_chunks:
                return []

            # 按文档ID分组
            doc_chunks = {}
            for chunk in similar_chunks:
                doc_id = chunk["document_id"]
                if doc_id not in doc_chunks:
                    doc_chunks[doc_id] = []
                doc_chunks[doc_id].append(chunk)

            # 构建搜索结果
            results = []
            for doc_id, chunks in doc_chunks.items():
                # 获取文档信息
                document = self.get_document(doc_id)
                if not document:
                    continue

                # 检查权限
                if user_id and document.owner_id != user_id:
                    continue

                # 合并相关文本块
                combined_content = "\n\n".join([chunk["content"] for chunk in chunks])
                avg_score = sum([chunk["score"] for chunk in chunks]) / len(chunks)

                results.append(DocumentSearchResult(
                    document_id=doc_id,
                    title=document.title,
                    content=combined_content[:500] + "..." if len(combined_content) > 500 else combined_content,
                    score=avg_score,
                    metadata={"chunk_count": len(chunks)}
                ))

            # 按分数排序
            results.sort(key=lambda x: x.score, reverse=True)

            # 限制结果数量
            return results[:search_request.limit]

        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []

    def reprocess_document_vectors(self, document_id: int) -> bool:
        """重新处理文档向量"""
        try:
            document = self.get_document(document_id)
            if not document or not document.content:
                return False

            # 删除旧的向量
            milvus_service.delete_document_vectors(document_id)

            # 重新向量化
            success = self._vectorize_document(document, document.content)

            if success:
                document.is_vectorized = True
                self.db.commit()
                logger.info(f"Successfully reprocessed vectors for document {document_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to reprocess document vectors {document_id}: {e}")
            return False
