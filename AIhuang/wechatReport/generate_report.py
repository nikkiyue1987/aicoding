#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一人公司启动孵化器群聊报告生成器 - 简化版
"""

import re
import requests
from datetime import datetime


def fetch_chatlog():
    """获取聊天记录"""
    print("[INFO] 正在获取聊天记录...")
    response = requests.get(
        "http://127.0.0.1:5030/api/v1/chatlog",
        params={
            "time": "2025-12-10",
            "talker": "48478008143@chatroom",
            "format": "text"
        },
        timeout=30
    )
    response.raise_for_status()
    return response.text


def parse_messages(content):
    """解析消息"""
    print("[INFO] 正在解析消息...")
    messages = []
    lines = content.strip().split('\n')

    current_msg = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 时间戳行
        if re.match(r'^\d{2}:\d{2}:\d{2}$', line):
            if current_msg:
                messages.append(current_msg)
            current_msg = {
                'time': f"2025-12-10T{line}",
                'sender': '',
                'content': ''
            }

        # 发送者行
        elif re.search(r'\(\w+\)\s+\d{2}:\d{2}:\d{2}$', line):
            match = re.match(r'^(.+?)\(([^)]+)\)\s+(\d{2}:\d{2}:\d{2})$', line)
            if match and current_msg:
                current_msg['sender'] = match.group(1)
                current_msg['time'] = f"2025-12-10T{match.group(3)}"

        # 系统消息
        elif line.startswith('系统消息'):
            if current_msg:
                messages.append(current_msg)
            current_msg = {
                'time': f"2025-12-10T00:00:00",
                'sender': '系统消息',
                'content': line
            }

        # 消息内容
        else:
            if current_msg:
                if current_msg['content']:
                    current_msg['content'] += '\n' + line
                else:
                    current_msg['content'] = line

    if current_msg:
        messages.append(current_msg)

    # 过滤空消息
    messages = [msg for msg in messages if msg['content'].strip()]
    print(f"[INFO] 成功解析 {len(messages)} 条消息")
    return messages


def analyze_topics(messages):
    """分析话题"""
    print("[INFO] 正在分析话题...")

    if not messages:
        return []

    # 简单按时间段分组
    topics = []
    current_topic = []

    for msg in messages:
        if not current_topic:
            current_topic = [msg]
        else:
            # 检查时间差
            try:
                last_time = datetime.fromisoformat(current_topic[-1]['time'].replace('Z', '+00:00'))
                current_time = datetime.fromisoformat(msg['time'].replace('Z', '+00:00'))
                diff_minutes = (current_time - last_time).total_seconds() / 60

                if diff_minutes <= 30:  # 30分钟内为同一话题
                    current_topic.append(msg)
                else:
                    if len(current_topic) >= 2:
                        topics.append(current_topic)
                    current_topic = [msg]
            except:
                current_topic.append(msg)

    if len(current_topic) >= 2:
        topics.append(current_topic)

    print(f"[INFO] 识别到 {len(topics)} 个话题")

    # 分析每个话题
    analyzed_topics = []
    for i, topic in enumerate(topics[:3], 1):  # 取前3个话题
        participants = set(msg['sender'] for msg in topic if msg['sender'])
        content_text = ' '.join(msg['content'] for msg in topic)

        # 提取关键词
        words = re.findall(r'\b\w{2,}\b', content_text.lower())
        stop_words = {'的', '了', '是', '在', '有', '和', '就', '都', '而', '及', '与', '或', '但', '不', '很', '也', '还', '要', '会', '能', '可', '我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', '这', '那', '这个', '那个', '什么', '怎么', '为什么', '哪里', '谁', '图片', '链接', '动画', '表情', '系统消息', '撤回', '加入', '邀请', '群聊'}
        keywords = [word for word in words if word not in stop_words and len(word) >= 2]
        keyword_counts = {}
        for word in keywords:
            keyword_counts[word] = keyword_counts.get(word, 0) + 1
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_keywords = [word for word, _ in top_keywords]

        # 生成摘要
        summary_parts = []
        for msg in topic[:3]:
            content = msg['content'][:60] + '...' if len(msg['content']) > 60 else msg['content']
            summary_parts.append(content)
        summary = ' | '.join(summary_parts)

        analyzed_topics.append({
            'rank': i,
            'score': round(len(topic) * 10 + len(participants) * 5, 2),
            'message_count': len(topic),
            'participant_count': len(participants),
            'keywords': top_keywords,
            'summary': summary,
            'start_time': topic[0]['time'],
            'end_time': topic[-1]['time'],
            'messages': topic
        })

    return analyzed_topics


def generate_html_report(group_name, total_messages, topics):
    """生成HTML报告"""
    print("[INFO] 正在生成HTML报告...")

    # 构建话题HTML
    topics_html = ""
    for topic in topics:
        messages_html = ""
        for msg in topic['messages']:
            try:
                time_str = datetime.fromisoformat(msg['time'].replace('Z', '+00:00')).strftime('%H:%M')
            except:
                time_str = msg['time']

            messages_html += f"""
            <div class="message-item">
                <div class="message-sender">{msg['sender']} <span class="message-time">{time_str}</span></div>
                <div class="message-content">{msg['content']}</div>
            </div>
            """

        topics_html += f"""
        <div class="topic-card">
            <div class="topic-header">
                <h2 class="topic-title">🏆 话题 {topic['rank']}</h2>
                <div class="topic-score">价值: {topic['score']}分</div>
            </div>
            <div class="topic-meta">
                <div class="meta-item">💬 {topic['message_count']} 条消息</div>
                <div class="meta-item">👥 {topic['participant_count']} 位参与者</div>
                <div class="meta-item">⏰ {topic['start_time'][11:16]} - {topic['end_time'][11:16]}</div>
            </div>
            <div class="summary">
                <strong>摘要:</strong> {topic['summary']}
            </div>
            <div class="keywords">
                <div class="keywords-title">🔑 关键词:</div>
                {''.join(f'<span class="keyword-tag">{kw}</span>' for kw in topic['keywords'])}
            </div>
            <div class="messages">
                <h3>💬 消息详情:</h3>
                {messages_html}
            </div>
        </div>
        """

    if not topics_html:
        topics_html = '<div class="topic-card"><p>未发现有效话题</p></div>'

    html = f"""
    <!DOCTYPE html>
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            color: #2d3748;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header .meta {{
            color: #718096;
            font-size: 1.1em;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            color: #718096;
            margin-top: 5px;
        }}

        .topics {{
            display: grid;
            gap: 25px;
        }}

        .topic-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}

        .topic-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
        }}

        .topic-title {{
            font-size: 1.8em;
            color: #2d3748;
            margin-bottom: 5px;
        }}

        .topic-score {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
        }}

        .topic-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .meta-item {{
            background: #f7fafc;
            padding: 8px 16px;
            border-radius: 10px;
            color: #4a5568;
            font-size: 0.9em;
        }}

        .keywords {{
            margin-bottom: 20px;
        }}

        .keywords-title {{
            color: #2d3748;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .keyword-tag {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            margin: 5px 5px 0 0;
            font-size: 0.85em;
        }}

        .summary {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
            color: #4a5568;
            line-height: 1.6;
        }}

        .messages {{
            margin-top: 20px;
        }}

        .message-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 3px solid #e2e8f0;
        }}

        .message-sender {{
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .message-time {{
            font-size: 0.8em;
            color: #a0aec0;
            margin-left: 10px;
        }}

        .message-content {{
            color: #4a5568;
            line-height: 1.5;
            white-space: pre-wrap;
        }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 {group_name}</h1>
                <div class="meta">分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{total_messages}</div>
                    <div class="stat-label">总消息数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(topics)}</div>
                    <div class="stat-label">精选话题</div>
                </div>
            </div>

            <div class="topics">
                {topics_html}
            </div>
        </div>
    </body>
    </html>
    """

    return html


def main():
    """主函数"""
    try:
        # 获取数据
        content = fetch_chatlog()

        # 解析消息
        messages = parse_messages(content)

        # 分析话题
        topics = analyze_topics(messages)

        # 生成报告
        html_content = generate_html_report('一人公司启动孵化器', len(messages), topics)

        # 保存文件
        output_path = '/E/myProject/aicoding/AIhuang/wechatReport/一人公司启动孵化器_今日报告.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n[SUCCESS] 报告已生成: {output_path}")
        print(f"[INFO] 总消息数: {len(messages)}")
        print(f"[INFO] 话题数: {len(topics)}")

    except Exception as e:
        print(f"[ERROR] 生成报告失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
