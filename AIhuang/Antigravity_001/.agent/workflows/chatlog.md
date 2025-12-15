---
description: Batch analyze multiple group chats and generate HTML reports
---

# Batch Chatlog Analysis Workflow

This workflow automates the batch analysis of multiple group chat conversations.

## Prerequisites

- MCP (Model Context Protocol) server must be running and accessible
- Python 3.7+ installed

## Workflow Steps

// turbo-all

1. **Check for checklist file**
   - If `群聊清单.md` doesn't exist, the script will create a template
   - Fill in the template with chat names and dates, then re-run

2. **Run the batch analyzer**
   ```bash
   python skills/batch-chatlog-analyzer/batch_chatlog_analyzer.py
   ```
   
   Or with a custom checklist file:
   ```bash
   python skills/batch-chatlog-analyzer/batch_chatlog_analyzer.py path/to/custom_checklist.md
   ```

3. **Review the output**
   - Reports are generated in `chatlog_reports_YYYYMMDD/` directory
   - Each chat gets its own HTML file: `{群聊名称}_YYYYMMDD.html`
   - Open the HTML files in a browser to view the analysis

## Expected Behavior

The script will:
- ✅ Read the checklist file
- ✅ Query MCP for each chat's messages
- ✅ Analyze and extract top 3 topics per chat
- ✅ Generate modern HTML reports
- ✅ Skip chats with no data (with warnings)
- ✅ Continue processing even if some chats fail

## Troubleshooting

**No reports generated?**
- Check that MCP server is running
- Verify chat names in checklist match MCP exactly
- Check the console logs for specific errors

**Some chats skipped?**
- Normal behavior if no messages exist for the specified date
- Check logs for details

## Notes

- This workflow runs fully automatically (no confirmations needed)
- Partial success is acceptable (some chats may be skipped)
- All errors are logged but don't stop the workflow
