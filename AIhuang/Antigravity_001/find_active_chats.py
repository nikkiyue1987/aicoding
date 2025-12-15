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

print(f"检查 2025-12-10 有消息的群聊...\n")

active_chats = []

for i, chat in enumerate(chatrooms):
    chat_id = chat.get('name', '')
    
    try:
        msg_response = requests.get(
            'http://127.0.0.1:5030/api/v1/chatlog',
            params={
                'talker': chat_id,
                'time': '2025-12-10~2025-12-10',
                'format': 'json'
            },
            timeout=2
        )
        
        if msg_response.status_code == 200:
            messages = msg_response.json()
            if isinstance(messages, list) and len(messages) > 0:
                # 获取第一条消息的内容作为线索
                first_msg = messages[0].get('content', '')[:80]
                active_chats.append({
                    'id': chat_id,
                    'count': len(messages),
                    'preview': first_msg
                })
                
        print(f"进度: {i+1}/{len(chatrooms)}", end='\r')
    except:
        continue

print("\n" + "="*80)
print(f"\n找到 {len(active_chats)} 个有消息的群聊:\n")

for i, chat in enumerate(active_chats, 1):
    print(f"{i}. ID: {chat['id']}")
    print(f"   消息数: {chat['count']}")
    print(f"   预览: {chat['preview']}")
    print()
