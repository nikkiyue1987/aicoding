#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import sys
import io
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 使用关键词搜索
keyword = "一人公司启动孵化器"

response = requests.get(
    'http://localhost:5030/api/v1/chatroom',
    params={'keyword': keyword}
)

print(f"搜索关键词: {keyword}\n")
print(f"状态码: {response.status_code}\n")
print(f"响应内容: {response.text}\n")

if response.status_code == 200 and response.text:
    try:
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            print(f"找到 {len(data['items'])} 个匹配的群聊:\n")
            
            for i, chat in enumerate(data['items'], 1):
                print(f"{i}. 群聊信息:")
                print(f"   ID: {chat.get('name', 'N/A')}")
                print(f"   nickName: {chat.get('nickName', 'N/A')}")
                print(f"   remark: {chat.get('remark', 'N/A')}")
                print()
        else:
            print("未找到匹配的群聊")
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except json.JSONDecodeError:
        print("响应不是有效的 JSON 格式")
else:
    print(f"请求失败或响应为空")
