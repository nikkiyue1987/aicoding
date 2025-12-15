# -*- coding: utf-8 -*-
"""
创建一个可用的群聊清单示例
从 Chatlog 中找到有消息的群聊
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
print("查找有消息的群聊")
print("=" * 70)
print()

try:
    # 获取所有群聊
    response = requests.get(f'{base_url}/api/v1/chatroom', params={'format': 'json'}, timeout=10)
    data = response.json()
    chatrooms = data.get('items', [])
    
    print(f"总共 {len(chatrooms)} 个群聊，正在查找有消息的群聊...")
    print()
    
    # 测试日期范围（最近30天）
    today = datetime.now()
    date_ranges = []
    for days_ago in [0, 7, 14, 30]:
        test_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        date_ranges.append(test_date)
    
    found_chatrooms = []
    
    # 测试每个群聊
    for i, room in enumerate(chatrooms[:20], 1):  # 只测试前20个以节省时间
        room_id = room.get('name', '')
        
        print(f"\r测试 {i}/20: {room_id[:30]}...", end='', flush=True)
        
        # 尝试不同的日期
        for test_date in date_ranges:
            try:
                response = requests.get(
                    f'{base_url}/api/v1/chatlog',
                    params={
                        'time_range': f'{test_date},{test_date}',
                        'chat_object': room_id,
                        'format': 'json',
                        'limit': 1  # 只需要知道有没有消息
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 提取消息
                    if isinstance(data, list):
                        messages = data
                    elif isinstance(data, dict):
                        messages = data.get('data', data.get('messages', data.get('items', [])))
                    else:
                        messages = []
                    
                    if messages and len(messages) > 0:
                        found_chatrooms.append({
                            'id': room_id,
                            'date': test_date,
                            'message_count': len(messages)
                        })
                        break  # 找到消息就跳出日期循环
                        
            except:
                pass
        
        if len(found_chatrooms) >= 3:  # 找到3个就够了
            break
    
    print("\r" + " " * 70 + "\r", end='')  # 清除进度显示
    
    if found_chatrooms:
        print(f"✓ 找到 {len(found_chatrooms)} 个有消息的群聊!")
        print()
        print("=" * 70)
        print("可以使用的群聊清单示例:")
        print("=" * 70)
        print()
        
        for i, chat in enumerate(found_chatrooms, 1):
            print(f"- 群聊名称: {chat['id']}")
            print(f"  日期: {chat['date']}")
            print(f"  格式: HTML")
            print()
        
        print("=" * 70)
        print()
        print("复制上面的内容到 群聊清单.md，然后运行 /chatlog")
        print()
        
        # 保存到文件
        with open('群聊清单_示例.md', 'w', encoding='utf-8') as f:
            f.write("# 群聊清单\n\n")
            f.write("## 分析清单\n\n")
            for chat in found_chatrooms:
                f.write(f"- 群聊名称: {chat['id']}\n")
                f.write(f"  日期: {chat['date']}\n")
                f.write(f"  格式: HTML\n\n")
        
        print("✓ 已保存到 群聊清单_示例.md")
        
    else:
        print("✗ 前20个群聊在最近30天都没有消息")
        print()
        print("建议:")
        print("1. 访问 http://127.0.0.1:5030 查看 Web 界面")
        print("2. 在'最近会话'中找到有消息的群聊")
        print("3. 手动复制群聊 ID 到清单中")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
