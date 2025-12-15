import requests
import json
import sys

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 获取所有群聊
response = requests.get('http://127.0.0.1:5030/api/v1/chatroom', params={'format':'json'})
chatrooms = response.json().get('items', [])

# 保存到文件（UTF-8编码）
with open('群聊列表.txt', 'w', encoding='utf-8') as f:
    f.write(f"找到 {len(chatrooms)} 个群聊:\n\n")
    
    for i, chat in enumerate(chatrooms, 1):
        name = chat.get('remark') or chat.get('nickName') or '未命名'
        chat_id = chat.get('name', '')
        f.write(f"{i}. {name}\n")
        f.write(f"   ID: {chat_id}\n\n")

print(f"Chatroom list saved to: 群聊列表.txt")
print(f"Total: {len(chatrooms)} chatrooms")
