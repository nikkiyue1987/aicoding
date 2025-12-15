# -*- coding: utf-8 -*-
"""
诊断工具：检查 Chatlog 数据库状态
"""

import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = 'http://127.0.0.1:5030'

print("=" * 70)
print("Chatlog 数据库诊断")
print("=" * 70)
print()

# 1. 检查最近会话
print("1. 检查最近会话...")
try:
    response = requests.get(f'{base_url}/api/v1/session', params={'format': 'json'}, timeout=10)
    if response.status_code == 200:
        data = response.json()
        sessions = data.get('items', [])
        print(f"   ✓ 找到 {len(sessions)} 个最近会话")
        if sessions:
            print(f"   最近的会话:")
            for i, session in enumerate(sessions[:5], 1):
                name = session.get('nickName') or session.get('userName') or '未知'
                msg_count = session.get('messageCount', 0)
                print(f"     {i}. {name} (消息数: {msg_count})")
    else:
        print(f"   ✗ 获取失败: HTTP {response.status_code}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

print()

# 2. 检查群聊
print("2. 检查群聊...")
try:
    response = requests.get(f'{base_url}/api/v1/chatroom', params={'format': 'json'}, timeout=10)
    if response.status_code == 200:
        data = response.json()
        chatrooms = data.get('items', [])
        print(f"   ✓ 找到 {len(chatrooms)} 个群聊")
        
        # 统计有名称的群聊
        with_name = sum(1 for r in chatrooms if r.get('nickName') or r.get('remark'))
        print(f"   其中 {with_name} 个有昵称/备注")
        
        if chatrooms:
            print(f"   前 5 个群聊示例:")
            for i, room in enumerate(chatrooms[:5], 1):
                room_id = room.get('name', '')
                nick = room.get('nickName', '')
                remark = room.get('remark', '')
                display = nick or remark or '(无名称)'
                print(f"     {i}. {display}")
                print(f"        ID: {room_id}")
    else:
        print(f"   ✗ 获取失败: HTTP {response.status_code}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

print()

# 3. 检查联系人
print("3. 检查联系人...")
try:
    response = requests.get(f'{base_url}/api/v1/contact', params={'format': 'json'}, timeout=10)
    if response.status_code == 200:
        data = response.json()
        contacts = data.get('items', [])
        print(f"   ✓ 找到 {len(contacts)} 个联系人")
    else:
        print(f"   ✗ 获取失败: HTTP {response.status_code}")
except Exception as e:
    print(f"   ✗ 错误: {e}")

print()

# 4. 测试查询聊天记录
print("4. 测试查询聊天记录...")
try:
    # 使用今天的日期
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 尝试查询任意对象的消息
    response = requests.get(
        f'{base_url}/api/v1/chatlog',
        params={
            'time_range': f'{today},{today}',
            'format': 'json'
        },
        timeout=10
    )
    
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict):
                msg_data = data.get('data', data.get('messages', data.get('items', [])))
            else:
                msg_data = data
            
            if msg_data:
                print(f"   ✓ 今天有 {len(msg_data) if isinstance(msg_data, list) else '一些'} 条消息")
            else:
                print(f"   ⚠ 今天没有消息记录")
        except:
            print(f"   ⚠ 响应格式: {response.headers.get('Content-Type')}")
    else:
        print(f"   ⚠ 查询失败: HTTP {response.status_code}")
        
except Exception as e:
    print(f"   ✗ 错误: {e}")

print()
print("=" * 70)
print("诊断完成")
print("=" * 70)
print()
print("建议:")
print("1. 如果群聊数量为 0，可能是:")
print("   - Chatlog 还没有导入微信聊天数据")
print("   - 数据库路径配置不正确")
print("   - 需要先运行 Chatlog 的数据导入功能")
print()
print("2. 如果有群聊但找不到你想要的:")
print("   - 检查群聊名称是否完全匹配")
print("   - 尝试使用群聊 ID (数字@chatroom 格式)")
print()
print("3. 访问 http://127.0.0.1:5030 查看 Web 界面")
print("   在那里可以直接浏览和搜索群聊")
