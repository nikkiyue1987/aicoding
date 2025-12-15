# -*- coding: utf-8 -*-
"""
测试查询第一个群聊的消息
"""

import requests
import json
import sys
import io
from datetime import datetime, timedelta

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'http://127.0.0.1:5030'

print("=" * 70)
print("测试群聊消息查询")
print("=" * 70)
print()

# 获取第一个群聊 ID
try:
    response = requests.get(f'{base_url}/api/v1/chatroom', params={'format': 'json'}, timeout=10)
    data = response.json()
    chatrooms = data.get('items', [])
    
    if not chatrooms:
        print("❌ 没有找到群聊")
        sys.exit(1)
    
    # 测试前 3 个群聊
    test_chatrooms = chatrooms[:3]
    
    print(f"将测试前 {len(test_chatrooms)} 个群聊")
    print()
    
    # 测试最近 7 天
    today = datetime.now()
    
    for i, room in enumerate(test_chatrooms, 1):
        room_id = room.get('name', '')
        print(f"{i}. 测试群聊: {room_id}")
        print("-" * 70)
        
        # 尝试查询最近 7 天的消息
        for days_ago in range(7):
            test_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            try:
                response = requests.get(
                    f'{base_url}/api/v1/chatlog',
                    params={
                        'time_range': f'{test_date},{test_date}',
                        'chat_object': room_id,
                        'format': 'json'
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # 提取消息
                        if isinstance(data, list):
                            messages = data
                        elif isinstance(data, dict):
                            messages = data.get('data', data.get('messages', data.get('items', [])))
                        else:
                            messages = []
                        
                        if messages and len(messages) > 0:
                            print(f"  ✓ {test_date}: 找到 {len(messages)} 条消息")
                            
                            # 显示第一条消息示例
                            if isinstance(messages[0], dict):
                                first_msg = messages[0]
                                sender = first_msg.get('sender', first_msg.get('from', first_msg.get('userName', '未知')))
                                content = first_msg.get('content', first_msg.get('text', first_msg.get('message', '')))
                                print(f"     示例: {sender}: {content[:50]}...")
                            
                            # 找到消息后，更新清单示例
                            print()
                            print("=" * 70)
                            print("✅ 成功！你可以这样更新 群聊清单.md:")
                            print("=" * 70)
                            print()
                            print(f"- 群聊名称: {room_id}")
                            print(f"  日期: {test_date}")
                            print(f"  格式: HTML")
                            print()
                            print("然后运行: /chatlog")
                            print("=" * 70)
                            sys.exit(0)
                            
                    except Exception as e:
                        pass
                        
            except Exception as e:
                pass
        
        print(f"  ✗ 最近 7 天没有消息")
        print()
    
    print("=" * 70)
    print("⚠️ 前 3 个群聊在最近 7 天都没有消息")
    print()
    print("建议:")
    print("1. 访问 http://127.0.0.1:5030 的 Web 界面")
    print("2. 在那里浏览群聊列表，找到有最近消息的群聊")
    print("3. 复制该群聊的 ID")
    print("4. 更新 群聊清单.md")
    
except Exception as e:
    print(f"❌ 错误: {e}")
