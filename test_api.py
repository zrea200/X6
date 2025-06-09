#!/usr/bin/env python3
"""
API测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_login():
    """测试登录"""
    try:
        data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=data)
        print(f"登录测试: {response.status_code}")
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"获取到token: {token[:20]}...")
            return token
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录测试失败: {e}")
        return None

def test_user_info(token):
    """测试获取用户信息"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"用户信息: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"用户: {user['username']} ({user['email']})")
            return True
        else:
            print(f"获取用户信息失败: {response.text}")
            return False
    except Exception as e:
        print(f"用户信息测试失败: {e}")
        return False

def test_documents(token):
    """测试文档API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/documents/", headers=headers)
        print(f"文档列表: {response.status_code}")
        if response.status_code == 200:
            docs = response.json()
            print(f"文档数量: {len(docs)}")
            return True
        else:
            print(f"获取文档列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"文档测试失败: {e}")
        return False

def test_chat(token):
    """测试聊天API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建聊天
        chat_data = {"title": "测试对话"}
        response = requests.post(f"{BASE_URL}/chat/", json=chat_data, headers=headers)
        print(f"创建聊天: {response.status_code}")
        
        if response.status_code == 200:
            chat = response.json()
            chat_id = chat["id"]
            print(f"聊天ID: {chat_id}")
            
            # 发送消息
            message_data = {
                "message": "你好，这是一个测试消息",
                "chat_id": chat_id
            }
            response = requests.post(f"{BASE_URL}/chat/message", json=message_data, headers=headers)
            print(f"发送消息: {response.status_code}")
            
            if response.status_code == 200:
                reply = response.json()
                print(f"AI回复: {reply['message'][:50]}...")
                return True
        
        return False
    except Exception as e:
        print(f"聊天测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始API测试...")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health():
        print("后端服务未启动，请先启动后端服务")
        return
    
    # 测试登录
    token = test_login()
    if not token:
        print("登录失败，请检查用户名密码或创建超级用户")
        return
    
    # 测试用户信息
    test_user_info(token)
    
    # 测试文档API
    test_documents(token)
    
    # 测试聊天API
    test_chat(token)
    
    print("=" * 50)
    print("API测试完成！")

if __name__ == "__main__":
    main()
