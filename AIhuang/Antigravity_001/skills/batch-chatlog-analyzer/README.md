# Batch Chatlog Analyzer

A production-grade Claude Code Skill for batch analysis of group chat conversations.

## Features

✨ **Batch Processing**: Analyze multiple chats in one command  
🤖 **Zero-Interruption**: Fully automatic execution (no confirmations)  
📊 **Intelligent Analysis**: Topic extraction with weighted ranking  
🎨 **Modern Reports**: Beautiful, responsive HTML output  
🛡️ **Robust**: Log & Continue error handling strategy  

## Quick Start

### 1. Trigger the Skill

Use the `/chatlog` slash command:

```
/chatlog
```

### 2. First Run

If `群聊清单.md` doesn't exist, a template will be created automatically:

```markdown
# 群聊清单

- 群聊名称: 技术讨论组
  日期: 昨天
  格式: HTML

- 群聊名称: 产品团队
  日期: 2025-12-11
  格式: HTML
```

### 3. Fill the Checklist

Edit `群聊清单.md` with your chat names and dates, then re-run `/chatlog`.

### 4. View Reports

Reports are generated in `chatlog_reports_YYYYMMDD/` directory. Open the HTML files in your browser.

## How It Works

### Workflow

1. **Read Checklist** → Parse chat names and dates
2. **Query MCP** → Fetch messages for each chat
3. **Analyze Topics** → Group messages into 30-min windows, rank by importance
4. **Generate Reports** → Create modern HTML with inline CSS
5. **Output Summary** → Log results and skip counts

### Topic Ranking Algorithm

Topics are scored using a weighted formula:
- **Message Count (40%)**: More messages = higher importance
- **Total Length (30%)**: Longer discussions = more substance  
- **Participant Count (30%)**: More participants = broader interest

Top 3 topics are selected for each chat.

## File Structure

```
skills/batch-chatlog-analyzer/
├── SKILL.md                      # Skill definition (triggers, instructions)
├── batch_chatlog_analyzer.py     # Python implementation
└── README.md                     # This file

.agent/workflows/
└── chatlog.md                    # Workflow for /chatlog command
```

## Configuration

### Date Formats Supported

- **Relative**: `昨天` (yesterday), `今天` (today), `前天` (day before yesterday)
- **Absolute**: `YYYY-MM-DD` (e.g., `2025-12-11`)
- **Default**: If missing, defaults to `昨天`

### Custom Checklist Path

You can use a custom checklist file:

```bash
python skills/batch-chatlog-analyzer/batch_chatlog_analyzer.py path/to/custom.md
```

## Error Handling

### Strategy: Log & Continue

The skill uses a **Log & Continue** strategy:
- ✅ Errors are logged to console
- ✅ Processing continues with remaining chats
- ✅ Partial success is acceptable
- ❌ No interruptions or confirmation prompts

### Common Scenarios

| Scenario | Behavior |
|----------|----------|
| Chat name not found | Skip → Log warning → Continue |
| No messages for date | Skip → Log info → Continue |
| MCP query timeout | Retry once → Skip if fails → Continue |
| HTML generation error | Skip → Log error → Continue |

## Output Format

### HTML Report Features

- 📱 **Responsive Design**: Works on desktop, tablet, mobile
- 🎨 **Modern Aesthetics**: Gradient backgrounds, card layouts, smooth animations
- 🔍 **Rich Metadata**: Message counts, participant counts, timestamps
- 🏷️ **Keyword Tags**: Visual keyword badges for each topic
- 📦 **Self-Contained**: All CSS inline (no external dependencies)

### Report Structure

```
Header Card
├── Chat name
├── Date
├── Message count
├── Participant count
└── Topic count

Topic Cards (Top 3)
├── Title
├── Timestamp
├── Summary
├── Message count
├── Participant count
└── Keywords (tags)

Footer
└── Generation timestamp
```

## Requirements

- Python 3.7+
- MCP (Model Context Protocol) server running
- Access to chat data via MCP

## Troubleshooting

### No Reports Generated?

1. Check MCP server is running
2. Verify chat names match MCP exactly (case-sensitive)
3. Check console logs for specific errors

### Some Chats Skipped?

This is normal if:
- No messages exist for the specified date
- Chat name doesn't exist in MCP
- MCP query times out

Check the logs for details.

### Template Not Created?

Ensure you have write permissions in the current directory.

## Examples

### Example Checklist

```markdown
# 群聊清单

- 群聊名称: 技术讨论组
  日期: 昨天
  格式: HTML

- 群聊名称: 产品团队
  日期: 2025-12-11
  格式: HTML

- 群聊名称: 设计组
  日期: 今天
  格式: HTML
```

### Example Output

```
🚀 Starting Batch Chatlog Analyzer...
📋 Parsed 3 chat(s) from checklist
📁 Output directory: chatlog_reports_20251212

📊 Processing: 技术讨论组 (2025-12-11)
🔍 Querying MCP for '技术讨论组' on 2025-12-11...
📊 Extracted 5 topics, selected top 3
✅ Generated report: 技术讨论组_20251211.html

📊 Processing: 产品团队 (2025-12-11)
🔍 Querying MCP for '产品团队' on 2025-12-11...
⚠️ No messages found for '产品团队' on 2025-12-11, skipping...

📊 Processing: 设计组 (2025-12-12)
🔍 Querying MCP for '设计组' on 2025-12-12...
📊 Extracted 3 topics, selected top 3
✅ Generated report: 设计组_20251212.html

============================================================
✅ Generated 2 report(s) in chatlog_reports_20251212/
⚠️ Skipped 1 chat(s) (see logs above)
🎉 Batch analysis complete!
```

## Technical Details

### Module Architecture

```python
ChecklistParser    # Parse MD file + normalize dates
MCPClient          # Query chat data via MCP
TopicAnalyzer      # Group messages + rank topics
HTMLGenerator      # Render beautiful reports
BatchChatlogAnalyzer  # Main orchestrator
```

### Time Window Strategy

Messages are grouped into **30-minute windows** to identify distinct conversation topics. This balances:
- **Granularity**: Not too short (fragmented topics)
- **Coherence**: Not too long (mixed topics)

### HTML Generation

All reports are **fully self-contained** with inline CSS:
- ✅ No broken links or missing stylesheets
- ✅ Easy sharing and archiving
- ✅ Consistent rendering across environments

## Version History

- **v1.0.0** (2025-12-12): Initial release
  - Batch processing support
  - MCP integration
  - Intelligent topic extraction
  - Modern HTML reports
  - Zero-interruption execution

## License

MIT License - Free to use, modify, and distribute.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review console logs for specific errors
3. Verify MCP server connectivity

---

**Built with ❤️ by Claude Skills Architect**
