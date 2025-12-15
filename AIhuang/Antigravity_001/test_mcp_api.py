# -*- coding: utf-8 -*-
"""
MCP API 测试工具 - 确认正确的 API 格式
"""

import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'http://127.0.0.1:5030'

print("=" * 70)
print("MCP API 格式确认工具")
print("=" * 70)
print()

# 测试群聊名称
test_chats = [
    "一人公司启动孵化器",
    "三人行必有吾师（艺考基础）"
]
test_date = "2025-12-12"

print(f"测试群聊: {test_chats}")
print(f"测试日期: {test_date}")
print()

# 1. 尝试获取群聊列表
print("=" * 70)
print("步骤 1: 尝试获取群聊列表")
print("=" * 70)

endpoints_for_list = ['/chats', '/list', '/api/chats', '/groups']

for endpoint in endpoints_for_list:
    try:
        print(f"\n尝试: GET {endpoint}")
        response = requests.get(f'{base_url}{endpoint}', timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"响应 (JSON): {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
            except:
                text = response.text[:500]
                print(f"响应 (文本): {text}")
    except Exception as e:
        print(f"错误: {e}")

# 2. 尝试查询消息
print("\n" + "=" * 70)
print("步骤 2: 尝试查询消息")
print("=" * 70)

chat_name = test_chats[0]

# 测试不同的 API 格式
test_cases = [
    {
        'name': 'POST /query with JSON',
        'method': 'POST',
        'url': f'{base_url}/query',
        'kwargs': {
            'json': {'chat_name': chat_name, 'date': test_date},
            'headers': {'Content-Type': 'application/json'}
        }
    },
    {
        'name': 'POST /query with different field names',
        'method': 'POST',
        'url': f'{base_url}/query',
        'kwargs': {
            'json': {'chat': chat_name, 'date': test_date},
            'headers': {'Content-Type': 'application/json'}
        }
    },
    {
        'name': 'GET /messages with query params',
        'method': 'GET',
        'url': f'{base_url}/messages',
        'kwargs': {
            'params': {'chat': chat_name, 'date': test_date}
        }
    },
    {
        'name': 'GET /messages with chat_name param',
        'method': 'GET',
        'url': f'{base_url}/messages',
        'kwargs': {
            'params': {'chat_name': chat_name, 'date': test_date}
        }
    },
    {
        'name': 'GET /chat/{name}/{date}',
        'method': 'GET',
        'url': f'{base_url}/chat/{chat_name}/{test_date}',
        'kwargs': {}
    },
    {
        'name': 'GET /api/messages',
        'method': 'GET',
        'url': f'{base_url}/api/messages',
        'kwargs': {
            'params': {'chat': chat_name, 'date': test_date}
        }
    },
]

successful_methods = []

for test_case in test_cases:
    print(f"\n{'=' * 70}")
    print(f"测试: {test_case['name']}")
    print(f"{'=' * 70}")
    
    try:
        if test_case['method'] == 'POST':
            response = requests.post(test_case['url'], timeout=5, **test_case['kwargs'])
        else:
            response = requests.get(test_case['url'], timeout=5, **test_case['kwargs'])
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ 成功! 返回 JSON 数据")
                print(f"数据类型: {type(data)}")
                
                if isinstance(data, list):
                    print(f"消息数量: {len(data)}")
                    if len(data) > 0:
                        print(f"第一条消息示例:")
                        print(json.dumps(data[0], ensure_ascii=False, indent=2))
                        successful_methods.append(test_case['name'])
                elif isinstance(data, dict):
                    print(f"字段: {list(data.keys())}")
                    print(f"数据示例: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                    if 'messages' in data or 'data' in data:
                        successful_methods.append(test_case['name'])
            except:
                text = response.text[:300]
                print(f"响应 (文本): {text}")
        else:
            print(f"❌ 失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

# 总结
print("\n" + "=" * 70)
print("总结")
print("=" * 70)

if successful_methods:
    print(f"\n✅ 找到 {len(successful_methods)} 个可用的 API 方法:")
    for method in successful_methods:
        print(f"  - {method}")
    print("\n建议: 使用第一个成功的方法更新 batch_chatlog_analyzer.py")
else:
    print("\n❌ 未找到可用的 API 方法")
    print("\n可能的原因:")
    print("1. MCP 服务器需要身份验证")
    print("2. 使用了不同的参数名称")
    print("3. 需要特殊的请求头")
    print("4. 使用 SSE 协议而不是 REST API")
    print("\n建议:")
    print("- 查看 MCP 服务器日志")
    print("- 访问 http://127.0.0.1:5030/help 查看文档")
    print("- 访问 http://127.0.0.1:5030/docs 查看 API 文档")

print("\n" + "=" * 70)
