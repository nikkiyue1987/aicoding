"""
HTML生成模块 - 生成现代化的HTML报告
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """HTML报告生成器"""

    def generate(self, analysis_result: Dict[str, Any]) -> str:
        """生成HTML报告

        Args:
            analysis_result: 分析结果字典

        Returns:
            HTML字符串
        """
        chat_name = analysis_result.get('name', '未知群聊')
        date = analysis_result.get('date', '')
        topics = analysis_result.get('topics', [])
        total_messages = analysis_result.get('total_messages', 0)
        error = analysis_result.get('error')

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chat_name} - 聊天分析报告 ({date})</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        /* 页面头部 */
        .header {{
            background: white;
            border-radius: 12px 12px 0 0;
            padding: 40px 30px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            font-size: 28px;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .header .meta {{
            display: flex;
            gap: 30px;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .meta-label {{
            font-weight: 600;
            color: #333;
        }}

        /* 错误提示 */
        .error-box {{
            background: #fff5f5;
            border-left: 4px solid #f56565;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
            color: #c53030;
        }}

        /* 内容区域 */
        .content {{
            background: white;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .topics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}

        /* 话题卡片 */
        .topic-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
            border: 1px solid rgba(102, 126, 234, 0.1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}

        .topic-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
            border-color: rgba(102, 126, 234, 0.3);
        }}

        .topic-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        }}

        .topic-order {{
            display: inline-block;
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 14px;
        }}

        .topic-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 12px;
            word-break: break-word;
        }}

        .topic-summary {{
            font-size: 14px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
            max-height: 80px;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .topic-keywords {{
            margin-bottom: 15px;
        }}

        .keyword {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 8px;
            margin-bottom: 6px;
            font-weight: 500;
        }}

        .topic-stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            border-top: 1px solid rgba(102, 126, 234, 0.2);
            padding-top: 12px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 16px;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-label {{
            font-size: 12px;
            color: #999;
            margin-top: 4px;
        }}

        /* 消息列表 */
        .messages {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            max-height: 300px;
            overflow-y: auto;
        }}

        .message {{
            margin-bottom: 12px;
            padding: 10px;
            background: rgba(102, 126, 234, 0.05);
            border-radius: 4px;
            border-left: 3px solid #667eea;
        }}

        .message-user {{
            font-weight: 600;
            color: #667eea;
            font-size: 12px;
        }}

        .message-content {{
            font-size: 13px;
            color: #666;
            margin-top: 4px;
            word-break: break-word;
        }}

        .message-time {{
            font-size: 11px;
            color: #999;
            margin-top: 4px;
        }}

        /* 页面底部 */
        .footer {{
            background: white;
            border-radius: 0 0 12px 12px;
            padding: 20px 30px;
            text-align: center;
            color: #999;
            font-size: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-top: 1px solid #eee;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            .header {{
                padding: 25px 20px;
            }}

            .header h1 {{
                font-size: 22px;
            }}

            .header .meta {{
                flex-direction: column;
                gap: 15px;
            }}

            .content {{
                padding: 20px;
            }}

            .topics-grid {{
                grid-template-columns: 1fr;
            }}

            .topic-stats {{
                grid-template-columns: repeat(3, 1fr);
            }}

            body {{
                padding: 10px;
            }}
        }}

        /* 打印样式 */
        @media print {{
            body {{
                background: white;
            }}

            .container {{
                box-shadow: none;
            }}

            .topic-card {{
                break-inside: avoid;
            }}
        }}

        /* 空状态 */
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }}

        .empty-state-icon {{
            font-size: 48px;
            margin-bottom: 20px;
        }}

        .empty-state-text {{
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{chat_name}</h1>
            <div class="meta">
                <div class="meta-item">
                    <span class="meta-label">📅 日期：</span>
                    <span>{date}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">💬 消息总数：</span>
                    <span>{total_messages}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">🔍 话题数：</span>
                    <span>{len(topics)}</span>
                </div>
            </div>
        </div>

        <div class="content">
"""

        if error:
            html += f"""            <div class="error-box">
                ⚠️ {error}
            </div>
"""

        if not topics:
            html += """            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <div class="empty-state-text">暂无话题数据</div>
            </div>
"""
        else:
            html += """            <div class="topics-grid">
"""
            for topic in topics:
                html += self._generate_topic_card(topic)

            html += """            </div>
"""

        html += """        </div>

        <div class="footer">
            <p>聊天分析报告 | 生成时间：""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>使用批量群聊分析工具生成</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    @staticmethod
    def _generate_topic_card(topic: Dict[str, Any]) -> str:
        """生成单个话题卡片的HTML

        Args:
            topic: 话题数据

        Returns:
            HTML字符串
        """
        title = topic.get('title', '未命名话题')
        summary = topic.get('summary', '')
        keywords = topic.get('keywords', [])
        stats = topic.get('stats', {})
        messages = topic.get('messages', [])
        time_range = topic.get('time_range', {})
        order = topic.get('order', 1)

        keywords_html = ""
        for keyword in keywords:
            keywords_html += f'<span class="keyword">{keyword}</span>\n'

        messages_html = ""
        for msg in messages[:3]:  # 只显示前3条消息
            user = msg.get('user', '匿名用户')
            content = msg.get('content', '').replace('<', '&lt;').replace('>', '&gt;')
            timestamp = msg.get('timestamp', '')

            messages_html += f"""                <div class="message">
                    <div class="message-user">{user}</div>
                    <div class="message-content">{content}</div>
                    <div class="message-time">{timestamp}</div>
                </div>
"""

        return f"""                <div class="topic-card">
                    <div class="topic-order">{order}</div>
                    <div class="topic-title">{title}</div>
                    <div class="topic-summary">{summary}</div>
                    <div class="topic-keywords">
{keywords_html}                    </div>
                    <div class="topic-stats">
                        <div class="stat">
                            <div class="stat-value">{stats.get('message_count', 0)}</div>
                            <div class="stat-label">消息数</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{stats.get('unique_speakers', 0)}</div>
                            <div class="stat-label">参与者</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{stats.get('score', 0)}</div>
                            <div class="stat-label">评分</div>
                        </div>
                    </div>
                    <div class="messages">
{messages_html}                    </div>
                </div>
"""
