# -*- coding: utf-8 -*-
"""
测试特定群聊 ID 的消息
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

# 要测试的群聊 ID
chatroom_ids = [
    "48478008143@chatroom",
    "57775213384@chatroom"
]

print("=" * 70)
print("测试群聊消息")
print("=" * 70)
print()

for room_id in chatroom_ids:
    print(f"群聊: {room_id}")
    print("-" * 70)
    
    # 测试最近 60 天
    today = datetime.now()
    found = False
    
    for days_ago in range(60):
        test_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        try:
            response = requests.get(
                f'{base_url}/api/v1/chatlog',
                params={
                    'time_range': f'{test_date},{test_date}',
                    'chat_object': room_id,
                    'format': 'json'
                },
                timeout=5
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
                        
                        # 显示第一条和最后一条消息
                        if isinstance(messages[0], dict):
                            first = messages[0]
                            print(f"     第一条: {first.get('content', first.get('text', ''))[:50]}...")
                        
                        if not found:
                            print()
                            print(f"  建议更新清单为:")
                            print(f"  - 群聊名称: {room_id}")
                            print(f"    日期: {test_date}")
                            print(f"    格式: HTML")
                            print()
                            found = True
                        
                except Exception as e:
                    pass
            elif response.status_code == 400:
                # 400 错误可能是参数问题，尝试不同的格式
                pass
                
        except Exception as e:
            pass
    
    if not found:
        print(f"  ✗ 最近 60 天没有找到消息")
        print(f"  可能原因:")
        print(f"  1. 这个群聊 ID 不正确")
        print(f"  2. 这个群聊没有聊天记录")
        print(f"  3. 聊天记录的时间超过 60 天前")
    
    print()

print("=" * 70)
