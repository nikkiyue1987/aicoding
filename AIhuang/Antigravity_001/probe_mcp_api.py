# -*- coding: utf-8 -*-
"""
MCP API 探测工具
帮助找出 chatlog MCP 服务器的正确 API 格式
"""

import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'http://127.0.0.1:5030'

print("=" * 60)
print("MCP API 探测工具")
print("=" * 60)
print()

# 测试的端点列表
endpoints = [
    ('GET', '/'),
    ('GET', '/api'),
    ('GET', '/chats'),
    ('GET', '/messages'),
    ('GET', '/query'),
    ('POST', '/query'),
    ('GET', '/api/chats'),
    ('GET', '/api/messages'),
    ('GET', '/list'),
    ('GET', '/help'),
    ('GET', '/docs'),
]

print("正在探测可用的 API 端点...")
print()

available_endpoints = []

for method, endpoint in endpoints:
    try:
        if method == 'GET':
            response = requests.get(
                f'{base_url}{endpoint}',
                headers={'Accept': 'application/json'},
                timeout=3
            )
        else:  # POST
            response = requests.post(
                f'{base_url}{endpoint}',
                json={},
                headers={'Accept': 'application/json'},
                timeout=3
            )
        
        if response.status_code < 500:  # 不是服务器错误
            available_endpoints.append((method, endpoint, response.status_code))
            print(f"✓ {method:4} {endpoint:20} -> {response.status_code}")
            
            # 尝试解析响应
            try:
                data = response.json()
                print(f"  响应示例: {str(data)[:100]}...")
            except:
                print(f"  响应类型: {response.headers.get('Content-Type', 'unknown')}")
    except Exception as e:
        pass

print()
print("=" * 60)
print(f"找到 {len(available_endpoints)} 个可用端点")
print("=" * 60)
print()

if available_endpoints:
    print("建议的下一步:")
    print()
    print("1. 查看 MCP 服务器文档,了解正确的 API 格式")
    print("2. 或者尝试以下端点:")
    for method, endpoint, status in available_endpoints:
        print(f"   - {method} {base_url}{endpoint}")
    print()
    print("3. 测试查询消息的 API:")
    print("   例如: GET /messages?chat=群聊名称&date=2025-12-12")
    print("   或者: POST /query {\"chat_name\": \"群聊名称\", \"date\": \"2025-12-12\"}")
else:
    print("未找到可用的 API 端点")
    print()
    print("可能的原因:")
    print("1. MCP 服务器使用非标准端点")
    print("2. 需要身份验证")
    print("3. 使用 SSE 协议而不是 REST API")
    print()
    print("建议:")
    print("- 查看 MCP 服务器文档")
    print("- 检查服务器日志")
    print("- 联系服务器管理员")

print()
print("=" * 60)
