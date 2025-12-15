# -*- coding: utf-8 -*-
"""
搜索特定的群聊
"""

import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'http://127.0.0.1:5030'

# 要搜索的群聊名称
search_names = [
    "一人公司启动孵化器",
    "三人行必有吾师（艺考基础）"
]

print("正在搜索群聊...")
print("=" * 70)
print()

try:
    # 获取所有群聊
    response = requests.get(
        f'{base_url}/api/v1/chatroom',
        params={'format': 'json'},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        chatrooms = data.get('items', [])
        
        print(f"总共有 {len(chatrooms)} 个群聊")
        print()
        
        for search_name in search_names:
            print("=" * 70)
            print(f"搜索: {search_name}")
            print("=" * 70)
            
            found = False
            
            # 搜索匹配的群聊
            for room in chatrooms:
                room_id = room.get('name', '')
                nick_name = room.get('nickName', '')
                remark = room.get('remark', '')
                
                # 检查是否匹配
                if (search_name in nick_name or 
                    search_name in remark or 
                    nick_name == search_name or 
                    remark == search_name):
                    
                    found = True
                    print(f"✓ 找到匹配!")
                    print(f"  群聊 ID: {room_id}")
                    if nick_name:
                        print(f"  昵称: {nick_name}")
                    if remark:
                        print(f"  备注: {remark}")
                    print()
            
            if not found:
                print(f"✗ 未找到匹配的群聊")
                print(f"  建议:")
                print(f"  1. 检查群聊名称是否正确")
                print(f"  2. 尝试搜索部分关键词")
                print(f"  3. 运行 'python list_chatrooms.py' 查看所有群聊")
                print()
        
        print("=" * 70)
        print()
        print("如果找到了群聊 ID，请更新 群聊清单.md:")
        print("将 '群聊名称: 显示名称' 改为 '群聊名称: ID@chatroom'")
        print()
        print("或者保持原样，程序会自动解析（如果名称匹配）")
        
    else:
        print(f"请求失败: {response.status_code}")
        
except Exception as e:
    print(f"错误: {e}")
