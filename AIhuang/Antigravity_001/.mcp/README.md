# MCP 配置说明

## Chatlog MCP 服务器配置

本项目已配置 chatlog MCP 服务器，用于查询群聊消息数据。

### 配置文件位置

- **项目配置**: `.mcp/config.json`
- **全局配置**: 根据你的 Claude Code 安装位置可能在：
  - `%APPDATA%\Claude\claude_desktop_config.json`
  - `%USERPROFILE%\.claude\config.json`
  - `%USERPROFILE%\.config\claude\config.json`

### 当前配置

```json
{
  "mcpServers": {
    "chatlog": {
      "url": "http://127.0.0.1:5030/sse"
    }
  }
}
```

### 配置说明

- **服务器名称**: `chatlog`
- **连接地址**: `http://127.0.0.1:5030/sse`
- **协议**: SSE (Server-Sent Events)

### 使用前提

1. **启动 MCP 服务器**
   
   确保 chatlog MCP 服务器正在运行并监听 `127.0.0.1:5030`

2. **验证连接**
   
   你可以通过以下方式验证 MCP 服务器是否正常运行：
   ```powershell
   # 测试连接
   curl http://127.0.0.1:5030/sse
   ```

3. **重启 Claude Code**
   
   修改 MCP 配置后，需要重启 Claude Code 使配置生效

### 在 Batch Chatlog Analyzer 中的使用

配置完成后，`batch_chatlog_analyzer.py` 中的 `MCPClient` 类会自动连接到这个服务器：

```python
class MCPClient:
    def query_messages(self, chat_name: str, date: str):
        # 通过 MCP 查询指定群聊在指定日期的消息
        # 实际实现会使用 MCP SDK 连接到 http://127.0.0.1:5030/sse
        pass
```

### 故障排查

**问题 1: 无法连接到 MCP 服务器**
- 检查服务器是否启动: `netstat -an | findstr 5030`
- 检查防火墙设置
- 确认端口 5030 未被其他程序占用

**问题 2: 查询返回空数据**
- 验证群聊名称是否正确（区分大小写）
- 检查指定日期是否有消息
- 查看 MCP 服务器日志

**问题 3: 配置未生效**
- 重启 Claude Code
- 检查 JSON 格式是否正确
- 确认配置文件路径正确

### 下一步

1. ✅ MCP 配置文件已创建
2. ⏳ 启动 chatlog MCP 服务器
3. ⏳ 重启 Claude Code（如果需要）
4. ⏳ 运行 `/chatlog` 测试连接

---

**注意**: 如果你使用的是 Claude Desktop 而不是 Claude Code，配置文件位置可能不同。请参考 Claude 官方文档。
