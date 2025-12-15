# -*- coding: utf-8 -*-
import requests
import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'http://127.0.0.1:5030'

# 查询群聊
response = requests.get(f'{base_url}/api/v1/chatroom', params={'format': 'json'}, timeout=10)
data = response.json()

# 保存到文件以便查看
with open('chatrooms_raw.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已保存到 chatrooms_raw.json")
print()

# 尝试提取群聊
if isinstance(data, list):
    print(f"数据是列表，包含 {len(data)} 项")
    if len(data) > 0:
        print("第一项的键:", list(data[0].keys()) if isinstance(data[0], dict) else "不是字典")
elif isinstance(data, dict):
    print(f"数据是字典，键: {list(data.keys())}")
    if 'data' in data:
        print(f"data 字段类型: {type(data['data'])}")
        if isinstance(data['data'], list):
            print(f"data 包含 {len(data['data'])} 项")
            if len(data['data']) > 0:
                first = data['data'][0]
                print(f"第一项: {json.dumps(first, ensure_ascii=False, indent=2)[:500]}")
