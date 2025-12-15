# 批量群聊分析工具

一个全自动的群聊数据分析和HTML报告生成工具，集成 chatlog MCP 的强大功能。

## 功能特性

✨ **核心功能：**
- 📖 解析Markdown清单文件，配置多个群聊
- 🔍 通过 chatlog MCP 查询指定日期的聊天数据
- 🧠 智能话题提取（按30分钟时间分组，选取最有价值的3个话题）
- 📊 自动生成高质量HTML报告
- 📦 批量输出按日期组织的报告文件

🎨 **报告特性：**
- 现代化UI设计（渐变背景、卡片布局）
- 响应式设计，支持移动端
- 话题标题、摘要、关键词自动生成
- 详细统计信息（消息数、参与者、评分）
- 打印友好的样式

## 项目结构

```
skills/chatlog_analyzer/
├── chatlog_analyzer.py      # 主程序入口
├── api_handler.py           # chatlog MCP API处理
├── md_parser.py             # Markdown清单解析
├── analyzer.py              # 智能分析引擎
├── html_generator.py        # HTML报告生成
├── __init__.py             # 包初始化
└── requirements.txt        # 依赖项

群聊清单.md                   # 群聊配置清单（用户编辑）
.claude/commands/chatlog.md  # Claude Code 斜杠命令
```

## 安装

### 1. 安装依赖

```bash
cd skills/chatlog_analyzer
pip install -r requirements.txt
```

### 2. 配置群聊清单

编辑项目根目录的 `群聊清单.md` 文件，添加要分析的群聊：

```markdown
### 群聊名称
- 日期：昨天
- 格式：JSON

### 另一个群聊
- 日期：3 days ago
- 格式：JSON
```

### 3. 确保 chatlog MCP 运行

chatlog MCP 服务需要在本地运行，监听 5030 端口：
```bash
http://127.0.0.1:5030
```

## 使用方法

### 方法一：Claude Code 斜杠命令（推荐）

```
/chatlog
```

这将自动：
1. 读取 `群聊清单.md`
2. 查询所有配置的群聊数据
3. 进行智能分析
4. 生成HTML报告到 `reports/YYYY-MM-DD/` 目录

### 方法二：命令行

```bash
# 基础用法
python skills/chatlog_analyzer/chatlog_analyzer.py 群聊清单.md

# 指定输出目录
python skills/chatlog_analyzer/chatlog_analyzer.py 群聊清单.md -o reports/custom

# 指定 API 地址
python skills/chatlog_analyzer/chatlog_analyzer.py 群聊清单.md --api http://localhost:5030

# 详细输出
python skills/chatlog_analyzer/chatlog_analyzer.py 群聊清单.md -v
```

## 配置说明

### 日期格式

支持多种日期格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| `yesterday` | `yesterday` | 昨天 |
| `today` | `today` | 今天 |
| `N days ago` | `3 days ago` | N天前 |
| ISO日期 | `2024-12-09` | 具体日期 |
| 短日期 | `12-09` | 本年该日期 |

### API 端点

chatlog MCP 提供以下端点：

- `GET /api/chats` - 获取所有群聊列表
- `GET /api/chat/{name}/messages?date=YYYY-MM-DD` - 获取特定日期的消息
- `GET /api/chat/{name}/search?keyword=xxx` - 搜索消息
- `GET /api/chat/{name}/info` - 获取群聊信息
- `GET /health` - 健康检查

## 分析算法

### 时间分组
消息按30分钟的时间窗口分组，相邻时间窗口内的消息为一个话题。

### 话题评分
话题分数基于四个指标：

| 指标 | 权重 | 说明 |
|------|------|------|
| 消息数量 | 30% | 最多10条为满分 |
| 文本长度 | 30% | 最多500字为满分 |
| 参与者多样性 | 20% | 最多5个参与者为满分 |
| 关键词数量 | 20% | 最多5个关键词为满分 |

### 关键词提取
- 使用简单的基于词频的方法
- 自动过滤常见停用词
- 支持中文和英文
- 返回频率最高的 N 个词

## 输出示例

生成的HTML报告包含：

1. **页面头部** - 群聊名称、日期、消息总数
2. **话题卡片** - 包含：
   - 话题序号
   - 自动生成的标题
   - 摘要内容
   - 关键词标签
   - 统计信息（消息数、参与者、评分）
   - 样本消息展示

3. **页面底部** - 生成时间和工具标识

## 错误处理

工具包含完整的错误处理：

- API 连接失败 → 记录错误并继续处理其他群聊
- Markdown 格式错误 → 输出警告并使用默认配置
- 没有聊天数据 → 显示友好的空状态提示
- 时间解析失败 → 使用当前时间作为默认值

## 日志输出

默认日志级别为 INFO，可通过 `-v` 标志提升为 DEBUG：

```bash
python chatlog_analyzer.py 群聊清单.md -v
```

日志包含：
- 清单解析进度
- API 请求状态
- 分析过程信息
- 文件生成路径

## 性能特性

- 📊 **消息分组** - O(n log n) 时间复杂度
- 🔍 **话题提取** - 并行处理多个群聊
- ⚡ **速率限制** - 每个群聊间隔1秒请求，避免服务压力
- 💾 **内存高效** - 流式处理消息，不一次性加载所有数据

## 扩展开发

### 添加自定义分析

修改 `analyzer.py` 中的 `_score_group()` 方法调整评分算法。

### 修改 HTML 样式

编辑 `html_generator.py` 中的 CSS 部分，定制页面外观。

### 支持新的 API

在 `api_handler.py` 中添加新的方法，例如：

```python
def get_chat_stats(self, chat_name: str) -> Dict:
    """获取群聊统计信息"""
    # 实现逻辑
```

## 故障排除

### 问题：API 连接失败

```
Error: API不可用: Connection refused
```

**解决：** 确保 chatlog MCP 服务已启动并监听 5030 端口

### 问题：找不到清单文件

```
FileNotFoundError: 清单文件不存在: 群聊清单.md
```

**解决：** 创建 `群聊清单.md` 文件，或指定正确的文件路径

### 问题：生成的HTML内容为空

```
暂无话题数据
```

**解决：**
- 检查群聊名称是否正确
- 确认该日期有聊天数据
- 查看详细日志：`python chatlog_analyzer.py 群聊清单.md -v`

## 许可证

MIT License

## 支持

如有问题或建议，欢迎提出 Issue 或 Pull Request。
