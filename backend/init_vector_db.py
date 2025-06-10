#!/usr/bin/env python3
"""
初始化向量数据库脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.vector_service import milvus_service
from app.services.embedding_service import embedding_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_vector_database():
    """初始化向量数据库"""
    try:
        logger.info("开始初始化向量数据库...")
        
        # 连接到Milvus
        if not milvus_service.connect():
            logger.error("无法连接到Milvus数据库")
            return False
        
        # 获取嵌入向量维度
        dimension = embedding_service.get_embedding_dimension()
        logger.info(f"嵌入向量维度: {dimension}")
        
        # 创建集合
        if milvus_service.create_collection(dimension):
            logger.info("向量数据库集合创建成功")
        else:
            logger.error("向量数据库集合创建失败")
            return False
        
        # 获取集合统计信息
        stats = milvus_service.get_collection_stats()
        logger.info(f"集合统计信息: {stats}")
        
        # 测试嵌入服务
        test_text = "这是一个测试文本"
        test_embedding = embedding_service.encode_text(test_text)
        logger.info(f"测试嵌入成功，向量长度: {len(test_embedding)}")
        
        logger.info("向量数据库初始化完成！")
        return True
        
    except Exception as e:
        logger.error(f"初始化向量数据库失败: {e}")
        return False
    finally:
        milvus_service.disconnect()

if __name__ == "__main__":
    success = init_vector_database()
    if success:
        print("✅ 向量数据库初始化成功")
    else:
        print("❌ 向量数据库初始化失败")
        sys.exit(1)
