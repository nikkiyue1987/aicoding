#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 获取所有群聊
response = requests.get('http://127.0.0.1:5030/api/v1/chatroom', params={'format':'json'})
chatrooms = response.json().get('items', [])

print(f"在所有 {len(chatrooms)} 个群聊中搜索包含 '一人公司' 或 '孵化器' 的消息...\n")

keywords = ["一人公司", "孵化器", "启动"]
found_chats = []

for i, chat in enumerate(chatrooms):
    chat_id = chat.get('name', '')
    
    try:
        # 获取最近7天的消息
        msg_response = requests.get(
            'http://127.0.0.1:5030/api/v1/chatlog',
            params={
                'talker': chat_id,
                'time': '2025-12-06~2025-12-12',
                'format': 'json'
            },
            timeout=2
        )
        
        if msg_response.status_code == 200:
            messages = msg_response.json()
            if isinstance(messages, list) and len(messages) > 0:
                # 检查是否包含关键词
                for msg in messages:
                    content = msg.get('content', '')
                    if any(kw in content for kw in keywords):
                        found_chats.append({
                            'id': chat_id,
                            'count': len(messages),
                            'sample': content[:100]
                        })
                        print(f"✅ 找到匹配: {chat_id}")
                        print(f"   消息数: {len(messages)}")
                        print(f"   示例: {content[:80]}...")
                        print()
                        break
        
        if i % 10 == 0:
            print(f"进度: {i}/{len(chatrooms)}", end='\r')
    except:
        continue

print(f"\n\n共找到 {len(found_chats)} 个匹配的群聊")
