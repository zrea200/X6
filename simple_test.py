#!/usr/bin/env python3
"""
简单的功能验证测试
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """测试导入"""
    try:
        from app.services.vector_service import milvus_service
        from app.services.embedding_service import embedding_service
        from app.services.document_service import DocumentService
        from app.services.chat_service import ChatService
        print("✅ 所有服务导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_embedding_service():
    """测试嵌入服务"""
    try:
        from app.services.embedding_service import embedding_service
        
        # 测试文本编码
        text = "这是一个测试"
        embedding = embedding_service.encode_text(text)
        print(f"✅ 文本编码成功，维度: {len(embedding)}")
        
        # 测试模型信息
        info = embedding_service.get_model_info()
        print(f"✅ 模型信息: {info['embedding_model']}")
        
        return True
    except Exception as e:
        print(f"❌ 嵌入服务测试失败: {e}")
        return False

def test_database():
    """测试数据库连接"""
    try:
        from app.core.database import engine, SessionLocal
        from app.models.user import User
        from app.models.document import Document
        from app.models.chat import Chat, Message
        
        # 测试数据库连接
        with SessionLocal() as db:
            # 简单查询测试
            users = db.query(User).limit(1).all()
            print(f"✅ 数据库连接成功，用户数: {len(users)}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始简单功能验证...")
    print("=" * 50)
    
    tests = [
        ("导入测试", test_imports),
        ("嵌入服务测试", test_embedding_service),
        ("数据库测试", test_database),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 {name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {name}失败")
        except Exception as e:
            print(f"❌ {name}异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有基础功能正常！")
        print("\n📝 功能状态:")
        print("- ✅ 向量嵌入服务正常")
        print("- ✅ 数据库连接正常")
        print("- ✅ 服务模块导入正常")
        print("\n🚀 系统已准备就绪！")
        print("您可以:")
        print("1. 手动启动后端: cd backend && uvicorn app.main:app --reload")
        print("2. 启动前端: cd frontend && npm run dev")
        print("3. 访问 http://localhost:5173 使用完整功能")
        return True
    else:
        print("❌ 部分功能异常，请检查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
