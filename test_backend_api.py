#!/usr/bin/env python3
"""
测试后端API是否正常工作
"""
import requests
import time

def test_backend_health():
    """测试后端健康状态"""
    try:
        print("🔍 测试后端API连接...")
        
        # 测试不同端口
        ports = [8001, 8000, 8002]
        
        for port in ports:
            try:
                url = f"http://127.0.0.1:{port}/health"
                print(f"   尝试连接: {url}")
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ 后端服务运行正常 - 端口 {port}")
                    print(f"   响应: {response.json()}")
                    return port
                else:
                    print(f"   端口 {port} 响应状态: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"   端口 {port} 连接失败")
            except Exception as e:
                print(f"   端口 {port} 错误: {e}")
        
        print("❌ 所有端口都无法连接")
        return None
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

def test_api_endpoints(port):
    """测试API端点"""
    try:
        base_url = f"http://127.0.0.1:{port}"
        
        # 测试API文档
        print(f"\n📚 测试API文档...")
        try:
            response = requests.get(f"{base_url}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API文档可访问")
            else:
                print(f"   API文档状态: {response.status_code}")
        except Exception as e:
            print(f"   API文档错误: {e}")
        
        # 测试OpenAPI规范
        print(f"\n📋 测试OpenAPI规范...")
        try:
            response = requests.get(f"{base_url}/openapi.json", timeout=5)
            if response.status_code == 200:
                print("✅ OpenAPI规范可访问")
                openapi_data = response.json()
                print(f"   API版本: {openapi_data.get('info', {}).get('version', 'N/A')}")
                print(f"   API标题: {openapi_data.get('info', {}).get('title', 'N/A')}")
            else:
                print(f"   OpenAPI规范状态: {response.status_code}")
        except Exception as e:
            print(f"   OpenAPI规范错误: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试后端API...")
    print("=" * 50)
    
    # 测试后端健康状态
    port = test_backend_health()
    
    if port:
        # 测试API端点
        test_api_endpoints(port)
        
        print("\n" + "=" * 50)
        print("✅ 后端API测试完成！")
        print(f"\n📝 后端服务信息:")
        print(f"- 运行端口: {port}")
        print(f"- API文档: http://127.0.0.1:{port}/docs")
        print(f"- 健康检查: http://127.0.0.1:{port}/health")
        
        print(f"\n🎯 前端配置建议:")
        print(f"- 更新前端API_URL为: http://127.0.0.1:{port}/api/v1")
        print(f"- 或设置环境变量: VITE_API_URL=http://127.0.0.1:{port}/api/v1")
        
        print(f"\n🔧 前端启动建议:")
        print("1. 以管理员身份运行PowerShell")
        print("2. 或者使用: npm run dev -- --host 0.0.0.0 --port 3003")
        print("3. 或者修改vite.config.ts中的host设置")
        
    else:
        print("\n" + "=" * 50)
        print("❌ 后端服务未运行")
        print("\n🔧 启动后端服务:")
        print("cd backend")
        print("uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")

if __name__ == "__main__":
    main()
