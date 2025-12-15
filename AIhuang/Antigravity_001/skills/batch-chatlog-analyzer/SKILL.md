---
name: batch-chatlog-analyzer
description: "Batch analysis tool for multiple group chat logs. Automatically reads chat data from MCP, performs intelligent topic extraction and ranking, and generates modern HTML reports. Use when Claude needs to: (1) Analyze multiple group chats in batch, (2) Generate chat analysis reports, (3) Extract and rank conversation topics, (4) Create HTML summaries of chat activity. Triggers on /chatlog command or requests for batch chat analysis."
license: MIT
---

# Batch Chatlog Analyzer

## 🔇 EXECUTION PROTOCOL (CRITICAL)

**QUIET MODE - READ THIS FIRST:**

- **Execute the entire workflow without asking for confirmation**
- **Generate the full output in one complete pass**
- **If data is missing, use the defined defaults below**
- **Log errors but continue processing remaining items**
- **Do not stop to ask "Should I continue?" or "Do you want to proceed?"**
- **Do not ask for clarification on edge cases - use the default handling strategies**
- **Partial success is acceptable - skip failed items and continue**

This skill MUST run atomically from start to finish. Any interruption breaks the automation contract.

---

## Overview

This skill enables batch analysis of multiple group chat conversations. It reads a markdown checklist, queries chat data via MCP (Model Context Protocol), performs intelligent topic extraction, and generates beautiful HTML reports for each chat.

**Keywords**: batch processing, chat analysis, MCP, topic extraction, HTML reports, conversation analysis, group chat, automated reporting

---

## Workflow Decision Tree

### When to Use This Skill
- User invokes `/chatlog` command
- User requests "批量分析群聊" or "batch chat analysis"
- User wants to generate reports for multiple chats

### When NOT to Use This Skill
- Single chat analysis (use standard MCP queries)
- Real-time chat monitoring
- Chat data export without analysis

---

## Input/Output Contract

### Input
**Primary**: Markdown checklist file (default: `群聊清单.md`)

**Format**:
```markdown
- 群聊名称: 技术讨论组
  日期: 昨天
  格式: HTML

- 群聊名称: 产品团队
  日期: 2025-12-11
  格式: HTML
```

**Optional**: Custom checklist file path via command argument

### Output
**Directory**: `chatlog_reports_YYYYMMDD/` (created automatically)

**Files**: One HTML file per chat: `{群聊名称}_YYYYMMDD.html`

**Console Summary**: Brief completion message (e.g., "✅ Generated 3 reports in chatlog_reports_20251211/")

---

## Default Handling Strategies (Zero-Interruption Protocol)

### Automatic Defaults

| Scenario | Default Behavior |
|----------|-----------------|
| Checklist file missing | Create template file → Log instruction → Exit gracefully |
| Chat name not found in MCP | Skip chat → Log warning → Continue with next |
| No messages for specified date | Skip chat → Log info → Continue with next |
| Date field missing | Use "昨天" (yesterday) |
| Format field missing | Default to "HTML" |
| Topics < 3 found | Output actual count (1-2 is OK) |
| MCP query timeout | Retry once → Skip if fails → Continue |
| HTML generation error | Log error → Skip chat → Continue |
| Output file exists | Overwrite silently |

### Date Format Support
- **Relative**: "昨天" (yesterday), "今天" (today), "前天" (day before yesterday)
- **Absolute**: "YYYY-MM-DD" (e.g., "2025-12-11")
- **Missing**: Defaults to "昨天"

### Error Handling Philosophy
**Strategy**: Log & Continue (NOT Stop & Ask)

All errors are logged to console but do NOT interrupt the workflow. Partial success is acceptable and expected.

---

## Execution Steps

### Phase 1: Initialization
1. Parse command arguments (optional: custom checklist path)
2. Check if checklist file exists
   - **If NO**: Create template → Exit with instructions
   - **If YES**: Parse all entries

### Phase 2: Data Collection
3. For each chat in checklist:
   - Parse date (handle relative/absolute formats)
   - Query MCP for messages on specified date
   - **If no data**: Log + Skip
   - **If success**: Store messages

### Phase 3: Intelligent Analysis
4. For each chat with data:
   - Group messages into 30-minute time windows
   - Extract topics from each window
   - Calculate topic scores:
     - Score = (message_count × 0.4) + (total_length × 0.3) + (participant_count × 0.3)
   - Rank topics by score
   - Select top 3 (or fewer if < 3 exist)
   - Generate: topic title, summary, keywords, timestamp

### Phase 4: Report Generation
5. Create output directory: `chatlog_reports_YYYYMMDD/`
6. For each analyzed chat:
   - Generate modern HTML report (responsive design)
   - Embed all CSS inline (no external dependencies)
   - Save to: `{群聊名称}_YYYYMMDD.html`

### Phase 5: Completion
7. Log summary: "✅ Generated N reports in chatlog_reports_YYYYMMDD/"
8. Exit cleanly

---

## HTML Design Specification

### Style Requirements
- **Layout**: Responsive grid (mobile-first, works on all devices)
- **Color Scheme**: Modern gradient background (purple-blue spectrum)
- **Typography**: Clean sans-serif (system fonts for reliability)
- **Components**:
  - Header card: Chat name, date, message count, participant count
  - Topic cards: Title, summary, keywords, timestamp, message count
  - Footer: Generation timestamp
- **Interactions**: Smooth hover effects on cards
- **Self-Contained**: All CSS/JS inline (zero external dependencies)

### Visual Hierarchy
1. **Header**: Chat metadata with gradient background
2. **Topics**: Card-based layout with shadows and hover effects
3. **Keywords**: Tag-style badges with accent colors
4. **Footer**: Subtle timestamp for reference

---

## Implementation Reference

### Module Structure
```
batch_chatlog_analyzer.py
├── ChecklistParser    # Parse MD file + normalize dates
├── MCPClient          # Query chat data via MCP
├── TopicAnalyzer      # Group messages + rank topics
├── HTMLGenerator      # Render beautiful reports
└── main()             # Orchestrate workflow
```

### Key Dependencies
- `mcp` - Model Context Protocol client
- `datetime` - Date parsing and formatting
- `pathlib` - File operations
- `json` - Data handling
- `re` - Regex for parsing

---

## Examples

### ✅ Good Example: Successful Batch Analysis

**User Input**:
```
/chatlog
```

**Skill Behavior**:
1. Reads `群聊清单.md`
2. Queries MCP for each chat
3. Analyzes topics automatically
4. Generates 3 HTML reports
5. Outputs: "✅ Generated 3 reports in chatlog_reports_20251211/"

**NO interruptions, NO confirmations, NO questions**

---

### ✅ Good Example: Handling Missing Data

**Scenario**: One chat has no messages for the specified date

**Skill Behavior**:
1. Processes first chat → Success
2. Processes second chat → No data found
   - Logs: "⚠️ No messages found for '产品团队' on 2025-12-11, skipping..."
3. Processes third chat → Success
4. Outputs: "✅ Generated 2 reports in chatlog_reports_20251211/"

**Continues automatically, no user intervention required**

---

### ❌ Anti-Pattern: DO NOT DO THIS

**BAD Behavior** (violates Quiet Mode):
```
User: /chatlog
Skill: I found the checklist. Should I proceed with analyzing 3 chats?
User: [has to respond]
Skill: Chat "技术讨论组" has no data for yesterday. Should I skip it?
User: [has to respond again]
```

**CORRECT Behavior**:
```
User: /chatlog
Skill: [Executes entire workflow]
       ✅ Generated 2 reports in chatlog_reports_20251211/
       ⚠️ Skipped 1 chat (no data available)
```

---

## Validation Matrix

| Test Case | Expected Behavior |
|-----------|------------------|
| Normal: 3 valid chats | Generate 3 HTML files, no interruptions |
| Edge: Chat name typo | Skip invalid chat, process others, log warning |
| Edge: Date = "昨天" | Parse correctly to YYYY-MM-DD format |
| Edge: Only 1 topic found | Generate report with 1 topic (not 3) |
| Edge: Empty chat (no messages) | Skip chat, no HTML generated, log info |
| Edge: Checklist missing | Create template, exit with instructions |
| Interference: "/chatlog" in conversation | No trigger (requires explicit command context) |

---

## Limitations

### What This Skill CANNOT Do
- Real-time chat monitoring (batch only)
- Analysis of non-MCP chat sources
- Custom analysis algorithms (uses fixed 30-min windows)
- Multi-language keyword extraction (Chinese-optimized)
- Chat data modification (read-only)

### Performance Considerations
- Large chats (1000+ messages) may take 10-30 seconds per chat
- MCP query rate limits may affect very large batches (10+ chats)
- HTML files are self-contained (larger file sizes)

---

## Troubleshooting

### Common Issues

**Issue**: "Checklist file not found"
- **Solution**: Skill auto-creates template, fill it and re-run

**Issue**: "No reports generated"
- **Solution**: Check logs for MCP connection errors or invalid chat names

**Issue**: "Some chats skipped"
- **Solution**: Normal behavior - check logs for specific reasons (no data, invalid date, etc.)

---

## Technical Notes

### Topic Ranking Algorithm
Topics are scored using a weighted formula:
- **Message Count (40%)**: More messages = higher importance
- **Total Length (30%)**: Longer discussions = more substance
- **Participant Count (30%)**: More participants = broader interest

### Time Window Strategy
Messages are grouped into 30-minute windows to identify distinct conversation topics. This balances granularity (too short = fragmented topics) with coherence (too long = mixed topics).

### HTML Generation
All reports are fully self-contained with inline CSS. This ensures:
- No broken links or missing stylesheets
- Easy sharing and archiving
- Consistent rendering across environments

---

## Version History

- **v1.0.0** (2025-12-12): Initial release
  - Batch processing support
  - MCP integration
  - Intelligent topic extraction
  - Modern HTML reports
  - Zero-interruption execution

---

## License

MIT License - Free to use, modify, and distribute.
