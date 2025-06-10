#!/usr/bin/env python3
"""
测试前端登录请求
"""
import requests
import json

def test_frontend_login():
    """模拟前端登录请求"""
    url = 'http://127.0.0.1:8000/api/v1/auth/login'
    
    # 模拟前端FormData请求
    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    headers = {
        'Origin': 'http://localhost:5174',
        'Referer': 'http://localhost:5174/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print("测试登录API...")
        response = requests.post(url, data=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f"Token获取成功: {token[:20]}...")
            
            # 测试获取用户信息
            print("\n测试获取用户信息...")
            user_url = 'http://127.0.0.1:8000/api/v1/users/me'
            auth_headers = {
                'Authorization': f'Bearer {token}',
                'Origin': 'http://localhost:5173',
                'Referer': 'http://localhost:5173/',
            }

            user_response = requests.get(user_url, headers=auth_headers)
            print(f"用户信息状态码: {user_response.status_code}")
            print(f"用户信息响应头: {dict(user_response.headers)}")
            print(f"用户信息: {user_response.text}")

            if user_response.status_code != 200:
                print("获取用户信息失败，这可能是导致前端登录失败的原因！")
            
        else:
            print("登录失败")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_frontend_login()
