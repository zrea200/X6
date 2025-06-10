#!/usr/bin/env python3
"""
测试向量搜索功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_service import milvus_service
from app.services.embedding_service import embedding_service
from app.schemas.document import DocumentSearchRequest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vector_search():
    """测试向量搜索功能"""
    try:
        logger.info("开始测试向量搜索功能...")
        
        # 连接到Milvus
        if not milvus_service.connect():
            logger.error("无法连接到Milvus数据库")
            return False
        
        # 测试文档
        test_documents = [
            "Python是一种高级编程语言，具有简洁的语法和强大的功能。",
            "机器学习是人工智能的一个重要分支，通过算法让计算机从数据中学习。",
            "FastAPI是一个现代、快速的Web框架，用于构建API。",
            "向量数据库可以高效地存储和搜索高维向量数据。",
            "自然语言处理技术可以帮助计算机理解和处理人类语言。"
        ]
        
        # 生成嵌入向量
        logger.info("生成测试文档的嵌入向量...")
        embeddings = embedding_service.encode_documents(test_documents)
        
        # 插入测试数据
        logger.info("插入测试数据到Milvus...")
        success = milvus_service.insert_vectors(
            document_id=999,  # 测试文档ID
            chunks=test_documents,
            embeddings=embeddings,
            metadata=[f"test_chunk_{i}" for i in range(len(test_documents))]
        )
        
        if not success:
            logger.error("插入测试数据失败")
            return False
        
        # 测试搜索
        test_queries = [
            "什么是Python编程语言？",
            "机器学习的应用",
            "如何构建API？",
            "向量搜索技术"
        ]
        
        for query in test_queries:
            logger.info(f"\n测试查询: {query}")
            
            # 生成查询向量
            query_embedding = embedding_service.encode_query(query)
            
            # 搜索相似文档
            results = milvus_service.search_similar(
                query_embedding=query_embedding,
                limit=3,
                score_threshold=0.3
            )
            
            logger.info(f"找到 {len(results)} 个相关结果:")
            for i, result in enumerate(results, 1):
                logger.info(f"  {i}. 分数: {result['score']:.3f} - {result['content'][:50]}...")
        
        # 测试重排序
        logger.info("\n测试重排序功能...")
        query = "Python编程"
        rerank_results = embedding_service.rerank_results(
            query=query,
            documents=test_documents[:3],
            scores=[0.8, 0.6, 0.7]
        )
        
        logger.info("重排序结果:")
        for i, result in enumerate(rerank_results, 1):
            logger.info(f"  {i}. 重排序分数: {result['rerank_score']:.3f} - {result['text'][:50]}...")
        
        # 清理测试数据
        logger.info("\n清理测试数据...")
        milvus_service.delete_document_vectors(999)
        
        logger.info("向量搜索功能测试完成！")
        return True
        
    except Exception as e:
        logger.error(f"测试向量搜索功能失败: {e}")
        return False
    finally:
        milvus_service.disconnect()

def test_embedding_service():
    """测试嵌入服务"""
    try:
        logger.info("\n测试嵌入服务...")
        
        # 测试单个文本编码
        text = "这是一个测试文本"
        embedding = embedding_service.encode_text(text)
        logger.info(f"单个文本嵌入维度: {len(embedding)}")
        
        # 测试批量文本编码
        texts = ["文本1", "文本2", "文本3"]
        embeddings = embedding_service.encode_documents(texts)
        logger.info(f"批量文本嵌入数量: {len(embeddings)}, 每个维度: {len(embeddings[0])}")
        
        # 测试文本分块
        long_text = "这是一个很长的文本。" * 100
        chunks = embedding_service.chunk_text(long_text, chunk_size=100, overlap=20)
        logger.info(f"文本分块数量: {len(chunks)}")
        
        # 测试相似度计算
        emb1 = embedding_service.encode_text("Python编程语言")
        emb2 = embedding_service.encode_text("Python开发")
        similarity = embedding_service.calculate_similarity(emb1, emb2)
        logger.info(f"相似度计算结果: {similarity:.3f}")
        
        # 获取模型信息
        model_info = embedding_service.get_model_info()
        logger.info(f"模型信息: {model_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"测试嵌入服务失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试向量搜索功能...")
    
    # 测试嵌入服务
    if not test_embedding_service():
        print("❌ 嵌入服务测试失败")
        sys.exit(1)
    
    # 测试向量搜索
    if test_vector_search():
        print("✅ 向量搜索功能测试成功")
    else:
        print("❌ 向量搜索功能测试失败")
        sys.exit(1)
