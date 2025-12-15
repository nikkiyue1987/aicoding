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

# 查看第一个群聊的完整数据结构
if 'items' in data and len(data['items']) > 0:
    print("=== 第一个群聊的数据结构 ===\n")
    first_chat = data['items'][0]
    print(json.dumps(first_chat, indent=2, ensure_ascii=False))
    
    print("\n=== 所有可用字段 ===")
    for key in first_chat.keys():
        value = first_chat[key]
        print(f"  {key}: {type(value).__name__} = {value}")
    
    # 查找包含 "Coze" 的群聊
    print("\n=== 查找包含 'Coze' 的群聊 ===")
    for chat in data['items']:
        chat_id = chat.get('name', '')
        nick = chat.get('nickName', '')
        remark = chat.get('remark', '')
        
        if 'Coze' in str(nick) or 'Coze' in str(remark) or 'coze' in str(nick).lower() or 'coze' in str(remark).lower():
            print(f"\n找到匹配:")
            print(f"  ID: {chat_id}")
            print(f"  nickName: {nick}")
            print(f"  remark: {remark}")
