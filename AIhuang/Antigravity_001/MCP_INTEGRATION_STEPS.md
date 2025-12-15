# MCP 集成完整指南

## ✅ 第 1 步：确认服务器运行 - 已完成！

你的 MCP 服务器正在运行：
- 地址: `http://127.0.0.1:5030/sse`
- 状态: 200 OK
- 类型: Server-Sent Events (SSE)

## 📝 第 2 步：了解你的 MCP 服务器 API

你的 chatlog MCP 服务器需要提供以下功能：

### 需要的 API 方法

1. **获取群聊列表** (可选)
2. **查询指定群聊的消息** (必需)
   - 输入: 群聊名称、日期
   - 输出: 消息列表

### 消息格式要求

每条消息应该包含：
```python
{
    'timestamp': '2025-12-12T10:30:00',  # ISO 格式时间
    'sender': 'User Name',                # 发送者名称
    'content': 'Message content'          # 消息内容
}
```

## 🔧 第 3 步：实现 MCP 集成

### 方案 A: 使用 MCP SDK (推荐)

如果你的 MCP 服务器提供了 Python SDK：

```python
# 1. 安装 SDK
pip install <your-mcp-sdk-name>

# 2. 在 batch_chatlog_analyzer.py 中修改 MCPClient
from your_mcp_sdk import Client  # 替换为实际的 SDK

class MCPClient:
    def __init__(self):
        self.client = Client('http://127.0.0.1:5030/sse')
    
    def query_messages(self, chat_name: str, date: str):
        try:
            # 使用 SDK 提供的方法
            messages = self.client.get_messages(
                chat_name=chat_name,
                date=date
            )
            return messages
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None
```

### 方案 B: 使用 HTTP 请求 (通用)

如果没有 SDK，可以直接使用 HTTP 请求：

```python
import requests
import json

class MCPClient:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:5030'
    
    def query_messages(self, chat_name: str, date: str):
        try:
            # 根据你的 MCP 服务器 API 调整
            response = requests.post(
                f'{self.base_url}/query',  # 替换为实际的端点
                json={
                    'chat_name': chat_name,
                    'date': date
                },
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Query failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None
```

### 方案 C: 使用 SSE 客户端

如果你的 MCP 服务器使用 SSE 协议：

```python
import sseclient
import requests

class MCPClient:
    def __init__(self):
        self.url = 'http://127.0.0.1:5030/sse'
    
    def query_messages(self, chat_name: str, date: str):
        try:
            # 发送查询请求
            response = requests.get(
                self.url,
                stream=True,
                headers={'Accept': 'text/event-stream'},
                params={'chat': chat_name, 'date': date}
            )
            
            # 解析 SSE 流
            client = sseclient.SSEClient(response)
            messages = []
            
            for event in client.events():
                if event.data:
                    msg = json.loads(event.data)
                    messages.append(msg)
            
            return messages
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None
```

## 🎯 第 4 步：我需要你提供的信息

为了帮你完成集成，我需要知道：

### 问题 1: MCP SDK
你的 chatlog MCP 服务器有提供 Python SDK 吗？
- 如果有，包名是什么？
- 如果没有，我们使用 HTTP 请求方式

### 问题 2: API 端点
查询消息的 API 端点是什么？
- 例如: `/api/messages`, `/query`, `/chat/history` 等

### 问题 3: 请求格式
查询消息时需要什么参数？
- 群聊名称的参数名: `chat_name`, `group_name`, `chat_id` ?
- 日期的参数名: `date`, `day`, `timestamp` ?
- 请求方法: GET, POST ?

### 问题 4: 响应格式
服务器返回的消息格式是什么？
- 直接返回消息数组？
- 还是包装在某个字段中，如 `{data: [...]}` ?

## 🚀 第 5 步：快速测试方案

如果你不确定 API 细节，我可以帮你：

1. **创建测试脚本** - 探测 MCP 服务器的 API
2. **使用模拟数据** - 先测试整个流程
3. **查看 MCP 文档** - 如果你有文档链接

## 💡 临时解决方案：使用模拟数据

如果你现在想先看到效果，我可以立即为你添加模拟数据，这样你可以：
- 看到完整的 HTML 报告效果
- 测试话题提取算法
- 验证整个流程

等你准备好真实 MCP 集成后，再替换回来。

---

**你想选择哪个方案？或者告诉我上面问题 1-4 的答案，我会帮你完成集成！** 🤔
