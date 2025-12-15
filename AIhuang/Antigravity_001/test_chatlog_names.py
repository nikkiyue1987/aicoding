#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import sys
import io
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 测试一个已知的群聊ID
test_chat_id = "48478008143@chatroom"
test_date = "2025-12-10"  # 我们知道这天有消息

# 调用 Chatlog API
response = requests.get(
    'http://127.0.0.1:5030/api/v1/chatlog',
    params={
        'talker': test_chat_id,
        'time': f"{test_date}~{test_date}",
        'format': 'json'
    }
)

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()
    
    if isinstance(data, list) and len(data) > 0:
        first_msg = data[0]
        print(f"共 {len(data)} 条消息\n")
        print("=== 第一条消息的所有字段 ===")
        for key in sorted(first_msg.keys()):
            value = first_msg[key]
            # 只显示字符串和数字类型的值
            if isinstance(value, (str, int, float, bool)):
                print(f"  {key}: {value}")
    else:
        print("没有消息数据")
        print(f"返回类型: {type(data)}")
        print(f"内容: {data}")
else:
    print(f"错误: {response.text}")
