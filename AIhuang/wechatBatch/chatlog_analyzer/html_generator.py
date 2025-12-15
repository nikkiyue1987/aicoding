"""
HTML报告生成器
生成现代化的响应式HTML报告
"""

from typing import Dict, List
from datetime import datetime
import os


class HTMLGenerator:
    """HTML报告生成器"""

    @staticmethod
    def generate_report(
        group_name: str,
        analysis_result: Dict,
        output_path: str
    ) -> str:
        """
        生成HTML报告

        Args:
            group_name: 群聊名称
            analysis_result: 分析结果
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        html_content = HTMLGenerator._build_html(group_name, analysis_result)

        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    @staticmethod
    def _build_html(group_name: str, analysis_result: Dict) -> str:
        """
        构建HTML内容

        Args:
            group_name: 群聊名称
            analysis_result: 分析结果

        Returns:
            HTML字符串
        """
        # 提取数据
        topics = analysis_result.get('topics', [])
        total_messages = analysis_result.get('total_messages', 0)
        total_participants = analysis_result.get('total_participants', 0)
        time_range = analysis_result.get('time_range', {})
        stats = analysis_result.get('most_active_users', [])
        avg_length = analysis_result.get('average_message_length', 0)
        peak_hour = analysis_result.get('peak_hour', 0)

        # 生成话题卡片
        topic_cards = HTMLGenerator._generate_topic_cards(topics)

        # 生成活跃用户列表
        active_users = HTMLGenerator._generate_active_users(stats)

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>群聊分析报告 - {group_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}

        .header h1 {{
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 16px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }}

        .stat-card .number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .stat-card .label {{
            color: #666;
            font-size: 14px;
        }}

        .section {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        }}

        .section-title {{
            color: #667eea;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .topic-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s;
        }}

        .topic-card:hover {{
            transform: translateX(5px);
        }}

        .topic-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }}

        .topic-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            flex: 1;
        }}

        .topic-score {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }}

        .topic-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 14px;
            color: #666;
        }}

        .topic-meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .keywords {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }}

        .keyword-tag {{
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 13px;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }}

        .topic-summary {{
            background: rgba(255, 255, 255, 0.6);
            padding: 15px;
            border-radius: 10px;
            font-size: 14px;
            line-height: 1.6;
            color: #555;
            border-left: 3px solid #667eea;
        }}

        .messages-preview {{
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
        }}

        .message-item {{
            background: rgba(255, 255, 255, 0.5);
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            font-size: 13px;
        }}

        .message-user {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .message-content {{
            color: #555;
            line-height: 1.5;
        }}

        .user-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}

        .user-item {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}

        .user-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}

        .user-count {{
            color: #666;
            font-size: 14px;
        }}

        .time-range {{
            background: rgba(102, 126, 234, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: #667eea;
            font-weight: 500;
        }}

        .footer {{
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            padding: 20px;
            font-size: 14px;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 24px;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .topic-header {{
                flex-direction: column;
                gap: 10px;
            }}

            .topic-meta {{
                flex-direction: column;
                gap: 10px;
            }}
        }}

        .scroll-indicator {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px 20px;
            border-radius: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            font-size: 14px;
            color: #667eea;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="scroll-indicator">
        群聊分析报告
    </div>

    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>📊 {group_name}</h1>
            <p class="subtitle">群聊智能分析报告 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="number">{total_messages}</div>
                <div class="label">总消息数</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_participants}</div>
                <div class="label">参与人数</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(topics)}</div>
                <div class="label">热门话题</div>
            </div>
            <div class="stat-card">
                <div class="number">{avg_length:.0f}</div>
                <div class="label">平均消息长度</div>
            </div>
        </div>

        <!-- 时间范围 -->
        {HTMLGenerator._generate_time_range(time_range)}

        <!-- 热门话题 -->
        <div class="section">
            <h2 class="section-title">🔥 热门话题分析</h2>
            {topic_cards if topic_cards else '<p style="color: #999; text-align: center; padding: 40px;">暂无话题数据</p>'}
        </div>

        <!-- 活跃用户 -->
        <div class="section">
            <h2 class="section-title">👥 活跃用户排行</h2>
            {active_users if active_users else '<p style="color: #999; text-align: center; padding: 40px;">暂无用户数据</p>'}
        </div>

        <!-- 页脚 -->
        <div class="footer">
            <p>🤖 由 AI 批量群聊分析工具生成 | 分析时间窗口: 30分钟</p>
        </div>
    </div>

    <script>
        // 添加滚动效果
        document.addEventListener('DOMContentLoaded', function() {{
            // 为话题卡片添加滚动动画
            const cards = document.querySelectorAll('.topic-card');
            cards.forEach((card, index) => {{
                card.style.animationDelay = `${{index * 0.1}}s`;
            }});

            // 添加回到顶部按钮
            const scrollTop = document.createElement('div');
            scrollTop.innerHTML = '⬆️';
            scrollTop.style.cssText = `
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 50px;
                height: 50px;
                background: rgba(102, 126, 234, 0.9);
                color: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 20px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s;
                z-index: 1000;
            `;
            scrollTop.onmouseover = function() {{
                this.style.transform = 'scale(1.1)';
            }};
            scrollTop.onmouseout = function() {{
                this.style.transform = 'scale(1)';
            }};
            scrollTop.onclick = function() {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }};
            document.body.appendChild(scrollTop);
        }});
    </script>
</body>
</html>"""
        return html

    @staticmethod
    def _generate_topic_cards(topics: List[Dict]) -> str:
        """生成话题卡片HTML"""
        if not topics:
            return ""

        cards = []
        for i, topic in enumerate(topics, 1):
            # 格式化时间
            start_time = topic.get('start_time')
            if hasattr(start_time, 'strftime'):
                time_str = start_time.strftime('%H:%M')
            else:
                time_str = str(start_time)

            # 生成关键词标签
            keywords_html = ''.join(
                f'<span class="keyword-tag">{kw}</span>'
                for kw in topic.get('keywords', [])
            )

            # 生成消息预览
            messages = topic.get('messages', [])[:5]  # 只显示前5条
            messages_html = ''.join(
                f'''<div class="message-item">
                    <div class="message-user">{msg.get('user', 'Unknown')}</div>
                    <div class="message-content">{msg.get('content', '')[:200]}</div>
                </div>'''
                for msg in messages
            )

            card = f"""
            <div class="topic-card">
                <div class="topic-header">
                    <div class="topic-title">{topic.get('title', '未知话题')}</div>
                    <div class="topic-score">★ {topic.get('score', 0):.1f}</div>
                </div>

                <div class="topic-meta">
                    <span>🕐 {time_str}</span>
                    <span>💬 {topic.get('message_count', 0)} 条消息</span>
                    <span>👥 {topic.get('participant_count', 0)} 人参与</span>
                </div>

                <div class="keywords">
                    {keywords_html}
                </div>

                <div class="topic-summary">
                    📝 {topic.get('summary', '暂无摘要')}
                </div>

                <div class="messages-preview">
                    {messages_html}
                </div>
            </div>
            """
            cards.append(card)

        return ''.join(cards)

    @staticmethod
    def _generate_active_users(stats: List[Dict]) -> str:
        """生成活跃用户列表HTML"""
        if not stats:
            return ""

        users_html = ''.join(
            f'''<div class="user-item">
                <div class="user-name">{user.get('user', 'Unknown')}</div>
                <div class="user-count">{user.get('count', 0)} 条消息</div>
            </div>'''
            for user in stats
        )

        return f'<div class="user-list">{users_html}</div>'

    @staticmethod
    def _generate_time_range(time_range: Dict) -> str:
        """生成时间范围HTML"""
        if not time_range:
            return ""

        start = time_range.get('start', '')
        end = time_range.get('end', '')
        duration = time_range.get('duration_minutes', 0)

        return f"""
        <div class="time-range">
            ⏰ 分析时间范围: {start} ~ {end} (持续 {duration} 分钟)
        </div>
        """
