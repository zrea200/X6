import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
try:
    from pymilvus import (
        connections,
        Collection,
        CollectionSchema,
        FieldSchema,
        DataType,
        utility
    )
    MILVUS_AVAILABLE = True
except ImportError as e:
    print(f"Milvus import failed: {e}")
    MILVUS_AVAILABLE = False
    # 创建占位符类
    class connections:
        @staticmethod
        def connect(*args, **kwargs):
            pass
        @staticmethod
        def disconnect(*args, **kwargs):
            pass

    class Collection:
        def __init__(self, *args, **kwargs):
            pass
        def insert(self, *args, **kwargs):
            return None
        def flush(self):
            pass
        def load(self):
            pass
        def search(self, *args, **kwargs):
            return []
        def delete(self, *args, **kwargs):
            pass
        def create_index(self, *args, **kwargs):
            pass
        @property
        def num_entities(self):
            return 0

    class CollectionSchema:
        def __init__(self, *args, **kwargs):
            pass

    class FieldSchema:
        def __init__(self, *args, **kwargs):
            pass

    class DataType:
        INT64 = "INT64"
        VARCHAR = "VARCHAR"
        FLOAT_VECTOR = "FLOAT_VECTOR"

    class utility:
        @staticmethod
        def has_collection(*args, **kwargs):
            return False

from app.core.config import settings

logger = logging.getLogger(__name__)

class MilvusService:
    """Milvus向量数据库服务"""
    
    def __init__(self):
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.collection = None
        self._connected = False
        
    def connect(self) -> bool:
        """连接到Milvus数据库"""
        try:
            if not self._connected:
                connections.connect(
                    alias="default",
                    host=settings.MILVUS_HOST,
                    port=settings.MILVUS_PORT
                )
                self._connected = True
                logger.info(f"Connected to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            return False
    
    def disconnect(self):
        """断开Milvus连接"""
        try:
            if self._connected:
                connections.disconnect("default")
                self._connected = False
                logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {e}")
    
    def create_collection(self, dimension: int = 384) -> bool:
        """创建文档向量集合"""
        try:
            if not self.connect():
                return False
            
            # 检查集合是否已存在
            if utility.has_collection(self.collection_name):
                logger.info(f"Collection {self.collection_name} already exists")
                self.collection = Collection(self.collection_name)
                return True
            
            # 定义字段
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="document_id", dtype=DataType.INT64),
                FieldSchema(name="chunk_id", dtype=DataType.INT64),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2000),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
                FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=1000)
            ]
            
            # 创建集合schema
            schema = CollectionSchema(
                fields=fields,
                description="Document chunks with embeddings"
            )
            
            # 创建集合
            self.collection = Collection(
                name=self.collection_name,
                schema=schema
            )
            
            # 创建索引
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            
            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            
            logger.info(f"Created collection {self.collection_name} with dimension {dimension}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def insert_vectors(self, 
                      document_id: int,
                      chunks: List[str], 
                      embeddings: List[List[float]],
                      metadata: Optional[List[str]] = None) -> bool:
        """插入向量数据"""
        try:
            if not self.connect():
                return False
            
            if not self.collection:
                self.collection = Collection(self.collection_name)
            
            # 准备数据
            chunk_count = len(chunks)
            data = [
                [document_id] * chunk_count,  # document_id
                list(range(chunk_count)),     # chunk_id
                chunks,                       # content
                embeddings,                   # embedding
                metadata or [""] * chunk_count  # metadata
            ]
            
            # 插入数据
            mr = self.collection.insert(data)
            self.collection.flush()
            
            logger.info(f"Inserted {chunk_count} vectors for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert vectors: {e}")
            return False
    
    def search_similar(self, 
                      query_embedding: List[float], 
                      limit: int = 10,
                      score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """搜索相似向量"""
        try:
            if not self.connect():
                return []
            
            if not self.collection:
                self.collection = Collection(self.collection_name)
            
            # 加载集合到内存
            self.collection.load()
            
            # 搜索参数
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # 执行搜索
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                output_fields=["document_id", "chunk_id", "content", "metadata"]
            )
            
            # 处理结果
            similar_docs = []
            for hits in results:
                for hit in hits:
                    if hit.score >= score_threshold:
                        similar_docs.append({
                            "id": hit.id,
                            "document_id": hit.entity.get("document_id"),
                            "chunk_id": hit.entity.get("chunk_id"),
                            "content": hit.entity.get("content"),
                            "metadata": hit.entity.get("metadata"),
                            "score": hit.score
                        })
            
            logger.info(f"Found {len(similar_docs)} similar documents")
            return similar_docs
            
        except Exception as e:
            logger.error(f"Failed to search similar vectors: {e}")
            return []
    
    def delete_document_vectors(self, document_id: int) -> bool:
        """删除指定文档的所有向量"""
        try:
            if not self.connect():
                return False
            
            if not self.collection:
                self.collection = Collection(self.collection_name)
            
            # 删除条件
            expr = f"document_id == {document_id}"
            self.collection.delete(expr)
            self.collection.flush()
            
            logger.info(f"Deleted vectors for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document vectors: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            if not self.connect():
                return {}
            
            if not self.collection:
                self.collection = Collection(self.collection_name)
            
            stats = self.collection.num_entities
            return {
                "total_vectors": stats,
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}

# 全局Milvus服务实例
milvus_service = MilvusService()
