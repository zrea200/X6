import logging
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from app.core.config import settings
import torch

logger = logging.getLogger(__name__)

class EmbeddingService:
    """文本嵌入服务"""
    
    def __init__(self):
        self.embedding_model = None
        self.rerank_model = None
        self._embedding_model_loaded = False
        self._rerank_model_loaded = False
        
    def load_embedding_model(self) -> bool:
        """加载嵌入模型"""
        try:
            if not self._embedding_model_loaded:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
                self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
                self._embedding_model_loaded = True
                logger.info("Embedding model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            return False
    
    def load_rerank_model(self) -> bool:
        """加载重排序模型"""
        try:
            if not self._rerank_model_loaded:
                logger.info(f"Loading rerank model: {settings.RERANK_MODEL}")
                self.rerank_model = CrossEncoder(settings.RERANK_MODEL)
                self._rerank_model_loaded = True
                logger.info("Rerank model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load rerank model: {e}")
            return False
    
    def get_embedding_dimension(self) -> int:
        """获取嵌入向量维度"""
        if not self.load_embedding_model():
            return 384  # 默认维度
        return self.embedding_model.get_sentence_embedding_dimension()
    
    def encode_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """将文本编码为向量"""
        try:
            if not self.load_embedding_model():
                raise Exception("Failed to load embedding model")
            
            # 处理单个文本或文本列表
            if isinstance(text, str):
                embedding = self.embedding_model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            else:
                embeddings = self.embedding_model.encode(text, convert_to_tensor=False)
                return embeddings.tolist()
                
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            if isinstance(text, str):
                return [0.0] * self.get_embedding_dimension()
            else:
                return [[0.0] * self.get_embedding_dimension()] * len(text)
    
    def encode_query(self, query: str) -> List[float]:
        """编码查询文本"""
        return self.encode_text(query)
    
    def encode_documents(self, documents: List[str]) -> List[List[float]]:
        """批量编码文档"""
        return self.encode_text(documents)
    
    def rerank_results(self, query: str, documents: List[str], scores: List[float] = None) -> List[dict]:
        """使用重排序模型对搜索结果重新排序"""
        try:
            if not self.load_rerank_model():
                logger.warning("Rerank model not available, returning original order")
                return [{"text": doc, "score": score or 0.0, "index": i} 
                       for i, (doc, score) in enumerate(zip(documents, scores or [0.0] * len(documents)))]
            
            # 准备查询-文档对
            query_doc_pairs = [(query, doc) for doc in documents]
            
            # 计算重排序分数
            rerank_scores = self.rerank_model.predict(query_doc_pairs)
            
            # 组合结果并排序
            results = []
            for i, (doc, original_score, rerank_score) in enumerate(zip(documents, scores or [0.0] * len(documents), rerank_scores)):
                results.append({
                    "text": doc,
                    "original_score": original_score,
                    "rerank_score": float(rerank_score),
                    "index": i
                })
            
            # 按重排序分数降序排列
            results.sort(key=lambda x: x["rerank_score"], reverse=True)
            
            logger.info(f"Reranked {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to rerank results: {e}")
            # 返回原始顺序
            return [{"text": doc, "score": score or 0.0, "index": i} 
                   for i, (doc, score) in enumerate(zip(documents, scores or [0.0] * len(documents)))]
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """将长文本分块"""
        chunk_size = chunk_size or settings.CHUNK_SIZE
        overlap = overlap or settings.CHUNK_OVERLAP
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 如果不是最后一块，尝试在句号、换行符或空格处分割
            if end < len(text):
                # 向后查找合适的分割点
                for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                    if text[i] in '.。\n ':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 下一块的起始位置考虑重叠
            start = end - overlap if end < len(text) else end
            
            # 避免无限循环
            if start >= end:
                break
        
        return chunks
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # 计算余弦相似度
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "embedding_model": settings.EMBEDDING_MODEL,
            "rerank_model": settings.RERANK_MODEL,
            "embedding_dimension": self.get_embedding_dimension(),
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "embedding_model_loaded": self._embedding_model_loaded,
            "rerank_model_loaded": self._rerank_model_loaded
        }

# 全局嵌入服务实例
embedding_service = EmbeddingService()
