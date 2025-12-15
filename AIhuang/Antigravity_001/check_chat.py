#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 检查这个群聊
chat_id = "47913990058@chatroom"

response = requests.get(
    'http://127.0.0.1:5030/api/v1/chatlog',
    params={
        'talker': chat_id,
        'time': '2025-12-10~2025-12-10',
        'format': 'json'
    }
)

if response.status_code == 200:
    messages = response.json()
    print(f"群聊 ID: {chat_id}")
    print(f"消息数: {len(messages)}\n")
    print("前10条消息内容:\n")
    
    for i, msg in enumerate(messages[:10], 1):
        content = msg.get('content', '')
        sender = msg.get('sender', 'Unknown')
        print(f"{i}. [{sender}] {content[:100]}")
        print()
