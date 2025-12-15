# MCP Integration Guide

## Current Status

⚠️ **MCP Client is partially implemented** - The code structure is ready, but actual MCP SDK integration needs to be completed.

## What's Implemented

✅ MCP server availability check  
✅ Error handling and logging  
✅ Graceful fallback when MCP unavailable  
✅ Clear error messages for troubleshooting  

## What's Needed

### 1. Start MCP Server

Ensure your chatlog MCP server is running on `http://127.0.0.1:5030/sse`

**Check if server is running:**
```powershell
# Check if port 5030 is listening
netstat -an | findstr 5030

# Test connection
curl http://127.0.0.1:5030/sse
```

### 2. Install MCP SDK (if needed)

```bash
pip install mcp-sdk
# or
pip install anthropic-mcp
```

### 3. Complete MCP Integration

Update the `MCPClient.query_messages()` method in `batch_chatlog_analyzer.py`:

```python
def query_messages(self, chat_name: str, date: str) -> Optional[List[Dict]]:
    """Query messages for a specific chat and date."""
    try:
        logger.info(f"🔍 Querying MCP for '{chat_name}' on {date}...")
        
        # Import MCP SDK
        from mcp import Client  # Adjust import based on actual SDK
        
        # Create client
        client = Client('http://127.0.0.1:5030/sse')
        
        # Query messages
        # Adjust method name and parameters based on your MCP server's API
        messages = client.get_chat_messages(
            chat_name=chat_name,
            date=date
        )
        
        # Expected message format:
        # [
        #     {
        #         'timestamp': '2025-12-12T10:30:00',
        #         'sender': 'User Name',
        #         'content': 'Message content'
        #     },
        #     ...
        # ]
        
        return messages
        
    except Exception as e:
        logger.error(f"❌ MCP query failed for '{chat_name}': {e}")
        return None
```

## MCP Server API Requirements

Your MCP server should provide an endpoint to query chat messages with:

**Input:**
- `chat_name`: String - Name of the chat/group
- `date`: String - Date in YYYY-MM-DD format

**Output:**
- List of message objects with:
  - `timestamp`: ISO format datetime string
  - `sender`: String - Name of message sender
  - `content`: String - Message text content

## Testing

### 1. Test MCP Server Connection

```python
# Test script
import urllib.request

try:
    req = urllib.request.Request(
        'http://127.0.0.1:5030/sse',
        headers={'Accept': 'text/event-stream'}
    )
    with urllib.request.urlopen(req, timeout=2) as response:
        print(f"✅ MCP server is running: {response.status}")
except Exception as e:
    print(f"❌ MCP server not available: {e}")
```

### 2. Test Message Query

Once MCP integration is complete, test with:

```bash
python skills/batch-chatlog-analyzer/batch_chatlog_analyzer.py
```

## Troubleshooting

### Error: "MCP server not available"

**Causes:**
1. MCP server not running
2. Server on different port
3. Firewall blocking connection

**Solutions:**
1. Start MCP server
2. Update URL in code if using different port
3. Check firewall settings

### Error: "MCP integration not yet implemented"

**Cause:** SDK integration incomplete

**Solution:** Follow step 3 above to complete integration

### Error: "No messages found"

**Causes:**
1. Chat name doesn't match exactly
2. No messages on specified date
3. MCP server query failed

**Solutions:**
1. Verify chat name (case-sensitive)
2. Try different date
3. Check MCP server logs

## Alternative: Mock Data for Testing

If you want to test the analyzer without MCP, you can create mock data:

```python
def query_messages(self, chat_name: str, date: str) -> Optional[List[Dict]]:
    """Mock implementation for testing."""
    # Return mock data
    return [
        {
            'timestamp': f'{date}T10:00:00',
            'sender': 'Alice',
            'content': '大家好，今天讨论一下项目进度'
        },
        {
            'timestamp': f'{date}T10:05:00',
            'sender': 'Bob',
            'content': '好的，我这边已经完成了前端开发'
        },
        {
            'timestamp': f'{date}T10:10:00',
            'sender': 'Charlie',
            'content': '后端API也已经部署到测试环境了'
        },
        # Add more mock messages...
    ]
```

## Next Steps

1. ✅ MCP configuration file created (`.mcp/config.json`)
2. ⏳ Start MCP server
3. ⏳ Complete SDK integration
4. ⏳ Test with real data
5. ⏳ Run `/chatlog` command

---

**Need help?** Check the MCP server documentation or contact your MCP server administrator.
