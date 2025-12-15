# 批量群聊分析工具 - 使用指南

## 概述

这是一个功能强大的批量群聊分析工具，可以自动分析多个群聊的聊天记录，提取有价值的话题，并生成美观的HTML报告。

## 主要功能

### 📊 智能话题分析
- **时间分组**: 按30分钟时间窗口自动分组消息为话题
- **价值评分**: 基于消息数量、长度、参与者数量和关键词计算话题价值
- **自动筛选**: 从所有话题中选出最有价值的3个话题
- **摘要生成**: 自动生成话题摘要和关键词提取

### 📝 报告内容
每个群聊的HTML报告包含：
- 群聊基本信息
- 消息统计（总消息数、话题数、精选话题数）
- 话题详情（排名、价值分数、摘要、关键词）
- 消息详情（时间、发送者、内容）

### 🎨 报告样式
- 现代化渐变背景设计
- 响应式布局，支持移动端
- 卡片式设计，层次分明
- 动画效果，用户体验友好

## 使用方式

### 命令行使用

```bash
# 基本使用（使用默认的"群聊清单.md"文件）
python run_chatlog.py

# 指定配置文件
python run_chatlog.py /path/to/custom_list.md

# 指定输出目录
python run_chatlog.py -o /path/to/output

# 查看帮助
python run_chatlog.py -h
```

### Claude Code 斜杠命令

```
/chatlog
```

## 配置文件格式

创建 `群聊清单.md` 文件，内容格式如下：

```markdown
# 团队协作群
- 日期: 昨天
- 格式: HTML

# 产品讨论群
- 日期: 2024-12-08
- 格式: HTML

# 技术交流群
- 日期: 今天
- 格式: HTML
```

### 支持的日期格式

- `昨天` - 昨天
- `今天` - 今天
- `本月` - 当前月份的第一天
- `YYYY-MM-DD` - 具体日期（如 `2024-12-09`）

### 支持的格式

- `HTML` - HTML格式（默认）
- `JSON` - JSON格式
- `TEXT` - 纯文本格式

## 输出文件

执行完成后会生成以下文件：

1. **各群聊报告**: `{群聊名}_report.html`
2. **汇总报告**: `summary.html`
3. **输出目录**: 默认命名为 `chatlog_reports_{时间戳}`

## 技术架构

### 模块化设计

工具采用模块化设计，包含以下组件：

1. **MarkdownParser** (`skills/chatlog_analyzer/md_parser.py`)
   - 解析群聊清单markdown文件
   - 支持多种格式的日期和配置

2. **ChatlogAPIHandler** (`skills/chatlog_analyzer/api_handler.py`)
   - 与chatlog MCP通信
   - 获取群聊消息数据
   - 健康检查和错误处理

3. **ChatAnalyzer** (`skills/chatlog_analyzer/analyzer.py`)
   - 按时间分组消息
   - 计算话题价值分数
   - 提取关键词和摘要

4. **HTMLGenerator** (`skills/chatlog_analyzer/html_generator.py`)
   - 生成美观的HTML报告
   - 响应式设计
   - 现代化样式

5. **ChatlogBatchAnalyzer** (`skills/chatlog_analyzer/chatlog_analyzer.py`)
   - 批量分析控制器
   - 协调各个模块
   - 生成最终报告

### 错误处理

- **API不可用**: 自动切换到模拟数据模式
- **文件不存在**: 清晰的错误提示
- **解析失败**: 详细错误信息
- **编码问题**: UTF-8编码支持

## 使用示例

### 示例1: 分析昨天的聊天记录

创建 `群聊清单.md`:
```markdown
# 工作群
- 日期: 昨天
- 格式: HTML

# 家庭群
- 日期: 昨天
- 格式: HTML
```

运行:
```bash
python run_chatlog.py
```

### 示例2: 分析指定日期

```markdown
# 产品团队
- 日期: 2024-12-01
- 格式: HTML

# 技术团队
- 日期: 2024-12-01
- 格式: HTML
```

### 示例3: 自定义输出目录

```bash
python run_chatlog.py -o /tmp/chat_reports
```

## 常见问题

### Q: 如何查看可用的群聊列表？

A: 群聊列表取决于你的chatlog MCP服务器配置。通常，群聊名称应该与微信群聊名称完全一致。

### Q: 如果API不可用会怎样？

A: 工具会自动切换到模拟数据模式，生成示例报告用于测试。

### Q: 支持哪些聊天平台？

A: 工具通过chatlog MCP获取数据，理论上支持任何MCP实现的聊天平台。

### Q: 如何自定义话题分析算法？

A: 可以修改 `ChatAnalyzer` 类中的 `calculate_topic_value` 方法来调整权重和评分逻辑。

## 开发信息

- **版本**: 1.0.0
- **Python要求**: 3.7+
- **依赖**: requests >= 2.28.0
- **许可证**: MIT

## 更新日志

### v1.0.0 (2024-12-10)
- 初始版本发布
- 支持批量群聊分析
- 智能话题提取
- 美观HTML报告生成
- 完整错误处理
- Claude Code集成
