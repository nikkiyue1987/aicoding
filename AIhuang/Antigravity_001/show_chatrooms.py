#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 获取所有群聊
response = requests.get('http://127.0.0.1:5030/api/v1/chatroom', params={'format':'json'})
data = response.json()

if 'items' in data:
    print(f"共找到 {len(data['items'])} 个群聊\n")
    
    # 只看前3个
    for i, chat in enumerate(data['items'][:3], 1):
        print(f"=== 群聊 {i} ===")
        for key, value in chat.items():
            if value:  # 只显示非空字段
                print(f"  {key}: {value}")
        print()
