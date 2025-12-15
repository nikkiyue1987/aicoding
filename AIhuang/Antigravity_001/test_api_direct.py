# -*- coding: utf-8 -*-
import requests
import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'http://127.0.0.1:5030'

# 测试参数
chatroom_id = "48478008143@chatroom"
time_range = "2025-12-01,2025-12-12"

print("=" * 70)
print("直接测试 Chatlog API")
print("=" * 70)
print()
print(f"群聊 ID: {chatroom_id}")
print(f"时间范围: {time_range}")
print()

try:
    url = f'{base_url}/api/v1/chatlog'
    params = {
        'time_range': time_range,
        'chat_object': chatroom_id,
        'format': 'json'
    }
    
    print(f"请求 URL: {url}")
    print(f"参数: {params}")
    print()
    
    response = requests.get(url, params=params, timeout=10)
    
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print()
    
    if response.status_code == 400:
        print("响应内容:")
        try:
            error_data = response.json()
            print(json.dumps(error_data, ensure_ascii=False, indent=2))
        except:
            print(response.text[:500])
    elif response.status_code == 200:
        try:
            data = response.json()
            print(f"成功！数据类型: {type(data)}")
            if isinstance(data, dict):
                print(f"字段: {list(data.keys())}")
            elif isinstance(data, list):
                print(f"消息数量: {len(data)}")
        except:
            print(response.text[:500])
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("尝试不同的参数格式...")
print("=" * 70)
print()

# 尝试不同的参数组合
test_cases = [
    {'time_range': time_range, 'chat_object': chatroom_id},
    {'time_range': time_range, 'chatroom': chatroom_id},
    {'start_date': '2025-12-01', 'end_date': '2025-12-12', 'chat_object': chatroom_id},
    {'date': '2025-12-01', 'chat_object': chatroom_id},
]

for i, params in enumerate(test_cases, 1):
    print(f"{i}. 测试参数: {params}")
    try:
        response = requests.get(f'{base_url}/api/v1/chatlog', params=params, timeout=5)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ 成功!")
            break
    except Exception as e:
        print(f"   ✗ 错误: {e}")
    print()
