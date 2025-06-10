#!/usr/bin/env python3
"""
测试嵌入功能（不需要Milvus）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.embedding_service import embedding_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_embedding_functionality():
    """测试嵌入功能"""
    try:
        logger.info("🧪 开始测试嵌入功能...")
        
        # 测试单个文本编码
        logger.info("\n📝 测试单个文本编码...")
        text = "Python是一种高级编程语言，具有简洁的语法和强大的功能。"
        embedding = embedding_service.encode_text(text)
        logger.info(f"✅ 文本: {text[:30]}...")
        logger.info(f"✅ 嵌入向量维度: {len(embedding)}")
        logger.info(f"✅ 向量前5个值: {embedding[:5]}")
        
        # 测试批量文本编码
        logger.info("\n📚 测试批量文本编码...")
        texts = [
            "机器学习是人工智能的一个重要分支。",
            "FastAPI是一个现代、快速的Web框架。",
            "向量数据库可以高效地存储和搜索高维向量数据。"
        ]
        embeddings = embedding_service.encode_documents(texts)
        logger.info(f"✅ 批量编码文本数量: {len(texts)}")
        logger.info(f"✅ 生成嵌入向量数量: {len(embeddings)}")
        logger.info(f"✅ 每个向量维度: {len(embeddings[0])}")
        
        # 测试文本分块
        logger.info("\n✂️ 测试文本分块...")
        long_text = """
        人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它企图了解智能的实质，
        并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、
        语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，
        应用领域也不断扩大，可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。
        
        机器学习是人工智能的核心，是使计算机具有智能的根本途径，其应用遍及人工智能的各个领域，
        它主要使用归纳、综合而不是演绎。深度学习是机器学习的一个分支，它基于人工神经网络，
        特别是利用多层次的神经网络来进行学习和模式识别。
        """
        
        chunks = embedding_service.chunk_text(long_text, chunk_size=100, overlap=20)
        logger.info(f"✅ 原文长度: {len(long_text)} 字符")
        logger.info(f"✅ 分块数量: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            logger.info(f"   块 {i+1}: {chunk[:50]}... (长度: {len(chunk)})")
        
        # 测试相似度计算
        logger.info("\n🔍 测试相似度计算...")
        text1 = "Python编程语言"
        text2 = "Python开发"
        text3 = "Java编程"
        
        emb1 = embedding_service.encode_text(text1)
        emb2 = embedding_service.encode_text(text2)
        emb3 = embedding_service.encode_text(text3)
        
        sim_12 = embedding_service.calculate_similarity(emb1, emb2)
        sim_13 = embedding_service.calculate_similarity(emb1, emb3)
        
        logger.info(f"✅ '{text1}' vs '{text2}' 相似度: {sim_12:.3f}")
        logger.info(f"✅ '{text1}' vs '{text3}' 相似度: {sim_13:.3f}")
        
        # 测试重排序功能
        logger.info("\n🎯 测试重排序功能...")
        query = "Python编程"
        documents = [
            "Python是一种高级编程语言",
            "Java是面向对象的编程语言", 
            "Python具有简洁的语法",
            "机器学习算法很复杂"
        ]
        scores = [0.8, 0.6, 0.9, 0.4]
        
        rerank_results = embedding_service.rerank_results(query, documents, scores)
        logger.info(f"✅ 查询: {query}")
        logger.info("✅ 重排序结果:")
        for i, result in enumerate(rerank_results):
            logger.info(f"   {i+1}. 文档: {result['text'][:30]}...")
            logger.info(f"      原始分数: {result.get('original_score', 0):.3f}, 重排序分数: {result['rerank_score']:.3f}")
        
        # 获取模型信息
        logger.info("\n📊 模型信息...")
        model_info = embedding_service.get_model_info()
        for key, value in model_info.items():
            logger.info(f"✅ {key}: {value}")
        
        logger.info("\n🎉 所有嵌入功能测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 嵌入功能测试失败: {e}")
        return False

def test_search_simulation():
    """模拟搜索功能测试"""
    try:
        logger.info("\n🔍 模拟搜索功能测试...")
        
        # 模拟文档库
        documents = [
            "Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。",
            "机器学习是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、算法复杂度理论等多门学科。",
            "FastAPI是一个用于构建API的现代、快速（高性能）的web框架，使用Python 3.6+并基于标准的Python类型提示。",
            "向量数据库是专门用于存储和查询向量数据的数据库系统，特别适合处理高维数据和相似性搜索。",
            "自然语言处理（NLP）是计算机科学领域与人工智能领域中的一个重要方向。"
        ]
        
        # 生成文档嵌入
        logger.info("📚 生成文档嵌入向量...")
        doc_embeddings = embedding_service.encode_documents(documents)
        
        # 测试查询
        queries = [
            "什么是Python？",
            "机器学习相关内容",
            "如何构建API？",
            "向量搜索技术"
        ]
        
        for query in queries:
            logger.info(f"\n🔎 查询: {query}")
            
            # 生成查询嵌入
            query_embedding = embedding_service.encode_text(query)
            
            # 计算相似度
            similarities = []
            for i, doc_emb in enumerate(doc_embeddings):
                similarity = embedding_service.calculate_similarity(query_embedding, doc_emb)
                similarities.append((i, similarity, documents[i]))
            
            # 排序并显示结果
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            logger.info("📋 搜索结果:")
            for rank, (doc_idx, sim, doc) in enumerate(similarities[:3], 1):
                logger.info(f"   {rank}. 相似度: {sim:.3f} - {doc[:50]}...")
        
        logger.info("\n🎉 搜索模拟测试完成！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 搜索模拟测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试嵌入和搜索功能...")
    
    # 测试嵌入功能
    if not test_embedding_functionality():
        print("❌ 嵌入功能测试失败")
        sys.exit(1)
    
    # 测试搜索模拟
    if not test_search_simulation():
        print("❌ 搜索模拟测试失败")
        sys.exit(1)
    
    print("\n✅ 所有测试通过！")
    print("\n📝 总结:")
    print("- ✅ 嵌入模型加载成功")
    print("- ✅ 文本向量化功能正常")
    print("- ✅ 文本分块功能正常")
    print("- ✅ 相似度计算功能正常")
    print("- ✅ 重排序功能正常")
    print("- ✅ 搜索模拟功能正常")
    print("\n🎯 接下来可以:")
    print("1. 启动Milvus服务进行完整测试")
    print("2. 启动后端API服务")
    print("3. 测试文档上传和搜索功能")
