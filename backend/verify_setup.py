#!/usr/bin/env python3
"""
验证Milvus向量搜索功能设置
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from app.services.vector_service import milvus_service
from app.services.embedding_service import embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖包"""
    try:
        import pymilvus
        import sentence_transformers
        import torch
        import numpy as np
        logger.info("✅ 所有依赖包已安装")
        return True
    except ImportError as e:
        logger.error(f"❌ 缺少依赖包: {e}")
        return False

def check_milvus_connection():
    """检查Milvus连接"""
    try:
        if milvus_service.connect():
            logger.info("✅ Milvus连接成功")
            milvus_service.disconnect()
            return True
        else:
            logger.error("❌ Milvus连接失败")
            return False
    except Exception as e:
        logger.error(f"❌ Milvus连接错误: {e}")
        return False

def check_embedding_models():
    """检查嵌入模型"""
    try:
        # 测试嵌入模型
        if embedding_service.load_embedding_model():
            logger.info("✅ 嵌入模型加载成功")
        else:
            logger.error("❌ 嵌入模型加载失败")
            return False
        
        # 测试重排序模型
        if embedding_service.load_rerank_model():
            logger.info("✅ 重排序模型加载成功")
        else:
            logger.warning("⚠️ 重排序模型加载失败（可选功能）")
        
        return True
    except Exception as e:
        logger.error(f"❌ 模型加载错误: {e}")
        return False

def check_vector_operations():
    """检查向量操作"""
    try:
        # 测试文本编码
        test_text = "这是一个测试文本"
        embedding = embedding_service.encode_text(test_text)
        
        if len(embedding) > 0:
            logger.info(f"✅ 文本编码成功，向量维度: {len(embedding)}")
        else:
            logger.error("❌ 文本编码失败")
            return False
        
        # 测试文本分块
        long_text = "这是一个很长的测试文本。" * 50
        chunks = embedding_service.chunk_text(long_text)
        
        if len(chunks) > 1:
            logger.info(f"✅ 文本分块成功，分块数量: {len(chunks)}")
        else:
            logger.error("❌ 文本分块失败")
            return False
        
        return True
    except Exception as e:
        logger.error(f"❌ 向量操作错误: {e}")
        return False

def check_collection_creation():
    """检查集合创建"""
    try:
        if not milvus_service.connect():
            return False
        
        dimension = embedding_service.get_embedding_dimension()
        if milvus_service.create_collection(dimension):
            logger.info("✅ Milvus集合创建/连接成功")
            
            # 获取统计信息
            stats = milvus_service.get_collection_stats()
            logger.info(f"✅ 集合统计: {stats}")
            
            milvus_service.disconnect()
            return True
        else:
            logger.error("❌ Milvus集合创建失败")
            return False
    except Exception as e:
        logger.error(f"❌ 集合创建错误: {e}")
        return False

def main():
    """主验证函数"""
    logger.info("🔍 开始验证Milvus向量搜索功能设置...")
    logger.info("=" * 60)
    
    checks = [
        ("依赖包检查", check_dependencies),
        ("Milvus连接检查", check_milvus_connection),
        ("嵌入模型检查", check_embedding_models),
        ("向量操作检查", check_vector_operations),
        ("集合创建检查", check_collection_creation),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        logger.info(f"\n📋 {name}...")
        try:
            if check_func():
                passed += 1
            else:
                logger.error(f"❌ {name}失败")
        except Exception as e:
            logger.error(f"❌ {name}异常: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"验证结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        logger.info("🎉 所有检查通过！Milvus向量搜索功能已就绪")
        logger.info("\n📝 接下来您可以:")
        logger.info("1. 启动应用: ./start.sh 或 start.bat")
        logger.info("2. 上传文档进行测试")
        logger.info("3. 使用聊天功能体验智能问答")
        return True
    else:
        logger.error("❌ 部分检查失败，请检查配置和依赖")
        logger.info("\n🔧 故障排除建议:")
        logger.info("1. 确保Docker服务正在运行")
        logger.info("2. 检查Milvus容器状态: docker ps | grep milvus")
        logger.info("3. 重启服务: docker-compose restart milvus")
        logger.info("4. 检查网络连接（首次运行需下载模型）")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
