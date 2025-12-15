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

# 搜索关键词
search_keyword = "一人公司"

print(f"搜索包含 '{search_keyword}' 的群聊...\n")

found = False
for chat in chatrooms:
    chat_id = chat.get('name', '')
    
    # 尝试从 Chatlog 获取一条消息来查看群聊名称
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
                # 检查消息内容中是否包含关键词
                for msg in messages[:5]:  # 只看前5条
                    content = msg.get('content', '')
                    if search_keyword in content:
                        print(f"✅ 找到匹配的群聊!")
                        print(f"   ID: {chat_id}")
                        print(f"   消息数: {len(messages)}")
                        print(f"   示例消息: {content[:100]}...")
                        print()
                        found = True
                        break
                
                if found:
                    break
    except:
        continue

if not found:
    print(f"❌ 未找到包含 '{search_keyword}' 的群聊")
    print("\n提示: 可能需要检查更多日期或使用其他关键词")
