#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一人公司启动孵化器群聊分析工具
"""

import re
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter


class ChatlogAnalyzer:
    """聊天记录分析器"""

    def __init__(self):
        self.time_window = 30  # 30分钟时间窗口
        self.min_messages_per_topic = 2  # 每个话题最少消息数

    def parse_chatlog(self, content: str) -> List[Dict]:
        """解析聊天记录文本"""
        messages = []
        lines = content.strip().split('\n')

        current_msg = {
            'timestamp': '',
            'sender': '',
            'content': ''
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测时间戳行 (HH:MM:SS)
            if re.match(r'^\d{2}:\d{2}:\d{2}$', line):
                # 保存上一条消息
                if current_msg['sender'] or current_msg['content']:
                    messages.append(current_msg)

                # 开始新消息
                current_msg = {
                    'timestamp': f"2025-12-10T{line}",
                    'sender': '',
                    'content': ''
                }

            # 检测发送者行 (姓名(wxid_xxx) HH:MM:SS)
            elif re.search(r'\(\w+\)\s+\d{2}:\d{2}:\d{2}$', line):
                match = re.match(r'^(.+?)\(([^)]+)\)\s+(\d{2}:\d{2}:\d{2})$', line)
                if match:
                    sender_name = match.group(1)
                    current_msg['sender'] = sender_name
                    current_msg['timestamp'] = f"2025-12-10T{match.group(3)}"

            # 检测系统消息行
            elif line.startswith('系统消息'):
                if current_msg['sender'] or current_msg['content']:
                    messages.append(current_msg)

                current_msg = {
                    'timestamp': current_msg['timestamp'] or f"2025-12-10T00:00:00",
                    'sender': '系统消息',
                    'content': line
                }
                messages.append(current_msg)
                current_msg = {
                    'timestamp': '',
                    'sender': '',
                    'content': ''
                }

            # 普通消息内容
            else:
                if current_msg['content']:
                    current_msg['content'] += '\n' + line
                else:
                    current_msg['content'] = line

        # 添加最后一条消息
        if current_msg['sender'] or current_msg['content']:
            messages.append(current_msg)

        # 过滤空消息
        messages = [msg for msg in messages if msg['content'].strip()]

        print(f"[INFO] 成功解析 {len(messages)} 条消息")
        return messages

    def group_messages_by_time(self, messages: List[Dict]) -> List[List[Dict]]:
        """按时间窗口分组消息"""
        if not messages:
            return []

        # 按时间戳排序
        sorted_messages = sorted(messages, key=lambda x: x.get('timestamp', ''))

        groups = []
        current_group = []

        for msg in sorted_messages:
            if not current_group:
                current_group.append(msg)
                continue

            # 检查时间差
            try:
                last_msg_time = datetime.fromisoformat(current_group[-1]['timestamp'].replace('Z', '+00:00'))
                current_msg_time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))

                time_diff = (current_msg_time - last_msg_time).total_seconds() / 60  # 分钟

                if time_diff <= self.time_window:
                    current_group.append(msg)
                else:
                    if current_group:
                        groups.append(current_group)
                    current_group = [msg]
            except:
                # 如果时间解析失败，将消息加入当前组
                current_group.append(msg)

        # 添加最后一组
        if current_group:
            groups.append(current_group)

        return groups

    def calculate_topic_value(self, topic_messages: List[Dict]) -> float:
        """计算话题价值分数"""
        if not topic_messages:
            return 0

        score = 0

        # 消息数量权重 (40%)
        msg_count = len(topic_messages)
        score += (msg_count / 10) * 40  # 假设10条消息为满分

        # 平均消息长度权重 (30%)
        total_chars = sum(len(msg.get('content', '')) for msg in topic_messages)
        avg_length = total_chars / msg_count if msg_count > 0 else 0
        score += min(avg_length / 100, 1) * 30  # 100字符为满分

        # 参与者数量权重 (20%)
        participants = set(msg.get('sender', '') for msg in topic_messages if msg.get('sender'))
        participant_count = len(participants)
        score += min(participant_count / 5, 1) * 20  # 5个参与者为满分

        # 关键词权重 (10%)
        keywords = self.extract_keywords(topic_messages)
        keyword_score = min(len(keywords) / 10, 1) * 10  # 10个关键词为满分
        score += keyword_score

        return score

    def extract_keywords(self, messages: List[Dict]) -> List[str]:
        """提取话题关键词"""
        all_text = ' '.join(msg.get('content', '') for msg in messages)

        # 简单关键词提取
        words = re.findall(r'\b\w{2,}\b', all_text.lower())

        # 过滤常见词
        stop_words = {'的', '了', '是', '在', '有', '和', '就', '都', '而', '及', '与', '或', '但', '不', '很', '也', '还', '要', '会', '能', '可', '我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', '这', '那', '这个', '那个', '什么', '怎么', '为什么', '哪里', '谁', '图片', '链接', '动画', '表情', '系统消息', '撤回', '加入', '邀请', '群聊'}

        keywords = [word for word in words if word not in stop_words and len(word) >= 2]

        # 返回频率最高的10个词
        counter = Counter(keywords)
        return [word for word, _ in counter.most_common(10)]

    def generate_topic_summary(self, topic_messages: List[Dict]) -> str:
        """生成话题摘要"""
        if not topic_messages:
            return "无内容"

        # 取前3条消息的开头作为摘要
        summary_parts = []
        for msg in topic_messages[:3]:
            content = msg.get('content', '').strip()
            if content:
                # 截取前80个字符
                summary_parts.append(content[:80] + ('...' if len(content) > 80 else ''))

        return ' | '.join(summary_parts) if summary_parts else "无有效内容"

    def analyze(self, chatlog_content: str) -> Dict[str, Any]:
        """分析聊天记录"""
        try:
            # 解析消息
            messages = self.parse_chatlog(chatlog_content)

            if not messages:
                return {
                    'group_name': '一人公司启动孵化器',
                    'error': '未找到聊天记录',
                    'topics': []
                }

            # 按时间分组
            print(f"[INFO] 按{self.time_window}分钟时间窗口分组...")
            time_groups = self.group_messages_by_time(messages)
            print(f"[INFO] 识别到 {len(time_groups)} 个话题")

            # 计算每个话题的价值
            topic_scores = []
            for group in time_groups:
                if len(group) >= self.min_messages_per_topic:
                    score = self.calculate_topic_value(group)
                    topic_scores.append((score, group))

            # 按价值排序，取前3个
            topic_scores.sort(key=lambda x: x[0], reverse=True)
            top_topics = topic_scores[:3]

            # 生成话题详情
            topics = []
            for i, (score, group) in enumerate(top_topics, 1):
                topic = {
                    'rank': i,
                    'score': round(score, 2),
                    'message_count': len(group),
                    'participant_count': len(set(msg.get('sender', '') for msg in group if msg.get('sender'))),
                    'keywords': self.extract_keywords(group),
                    'summary': self.generate_topic_summary(group),
                    'start_time': group[0].get('timestamp', ''),
                    'end_time': group[-1].get('timestamp', ''),
                    'messages': group
                }
                topics.append(topic)

            return {
                'group_name': '一人公司启动孵化器',
                'total_messages': len(messages),
                'total_topics': len(time_groups),
                'analyzed_topics': len(topics),
                'analysis_date': datetime.now().isoformat(),
                'topics': topics
            }

        except Exception as e:
            return {
                'group_name': '一人公司启动孵化器',
                'error': f"分析失败: {str(e)}",
                'topics': []
            }


class HTMLReportGenerator:
    """HTML报告生成器"""

    def __init__(self):
        self.base_style = """
        <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            color: #2d3748;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header .meta {
            color: #718096;
            font-size: 1.1em;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stat-label {
            color: #718096;
            margin-top: 5px;
        }

        .topics {
            display: grid;
            gap: 25px;
        }

        .topic-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .topic-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
        }

        .topic-title {
            font-size: 1.8em;
            color: #2d3748;
            margin-bottom: 5px;
        }

        .topic-score {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }

        .topic-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .meta-item {
            background: #f7fafc;
            padding: 8px 16px;
            border-radius: 10px;
            color: #4a5568;
            font-size: 0.9em;
        }

        .keywords {
            margin-bottom: 20px;
        }

        .keywords-title {
            color: #2d3748;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .keyword-tag {
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            margin: 5px 5px 0 0;
            font-size: 0.85em;
        }

        .summary {
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
            color: #4a5568;
            line-height: 1.6;
        }

        .messages {
            margin-top: 20px;
        }

        .message-item {
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 3px solid #e2e8f0;
        }

        .message-sender {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }

        .message-time {
            font-size: 0.8em;
            color: #a0aec0;
            margin-left: 10px;
        }

        .message-content {
            color: #4a5568;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        .error {
            background: #fed7d7;
            color: #c53030;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            .topic-header {
                flex-direction: column;
                gap: 15px;
            }
        }
        </style>
        """

    def generate_report(self, analysis_result: Dict[str, Any], output_path: str):
        """生成HTML报告"""
        html_content = self._build_html(analysis_result)

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"[SUCCESS] 报告已生成: {output_path}")
        except Exception as e:
            print(f"[ERROR] 生成报告失败: {str(e)}")

    def _build_html(self, data: Dict[str, Any]) -> str:
        """构建HTML内容"""
        if 'error' in data:
            return self._build_error_html(data)

        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>群聊分析报告 - {data['group_name']}</title>
            {self.base_style}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 {data['group_name']}</h1>
                    <div class="meta">分析时间: {self._format_datetime(data['analysis_date'])}</div>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{data['total_messages']}</div>
                        <div class="stat-label">总消息数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{data['total_topics']}</div>
                        <div class="stat-label">话题数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{data['analyzed_topics']}</div>
                        <div class="stat-label">精选话题</div>
                    </div>
                </div>

                <div class="topics">
                    {self._build_topics_html(data['topics'])}
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _build_topics_html(self, topics: List[Dict]) -> str:
        """构建话题HTML"""
        if not topics:
            return '<div class="topic-card"><p>未发现有效话题</p></div>'

        topics_html = []
        for topic in topics:
            topic_html = f"""
            <div class="topic-card">
                <div class="topic-header">
                    <div>
                        <h2 class="topic-title">🏆 话题 {topic['rank']}</h2>
                    </div>
                    <div class="topic-score">价值: {topic['score']}分</div>
                </div>

                <div class="topic-meta">
                    <div class="meta-item">💬 {topic['message_count']} 条消息</div>
                    <div class="meta-item">👥 {topic['participant_count']} 位参与者</div>
                    <div class="meta-item">⏰ {self._format_datetime(topic['start_time'])} - {self._format_datetime(topic['end_time'])}</div>
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
                    {self._build_messages_html(topic['messages'])}
                </div>
            </div>
            """
            topics_html.append(topic_html)

        return '\n'.join(topics_html)

    def _build_messages_html(self, messages: List[Dict]) -> str:
        """构建消息HTML"""
        if not messages:
            return '<p>无消息内容</p>'

        messages_html = []
        for msg in messages:
            msg_html = f"""
            <div class="message-item">
                <div class="message-sender">
                    {msg.get('sender', '未知用户')}
                    <span class="message-time">{self._format_datetime(msg.get('timestamp', ''))}</span>
                </div>
                <div class="message-content">{msg.get('content', '')}</div>
            </div>
            """
            messages_html.append(msg_html)

        return '\n'.join(messages_html)

    def _build_error_html(self, data: Dict[str, Any]) -> str:
        """构建错误HTML"""
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>群聊分析报告 - {data['group_name']}</title>
            {self.base_style}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 {data['group_name']}</h1>
                </div>
                <div class="error">
                    <h2>❌ {data['error']}</h2>
                </div>
            </div>
        </body>
        </html>
        """

    def _format_datetime(self, dt_str: str) -> str:
        """格式化日期时间"""
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%m-%d %H:%M')
        except:
            return dt_str


def main():
    """主函数"""
    # 读取聊天记录数据
    print("[INFO] 正在读取聊天记录...")
    import requests

    try:
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
        chatlog_content = response.text
    except Exception as e:
        print(f"[ERROR] 读取聊天记录失败: {e}")
        return

    # 分析聊天记录
    print("[INFO] 开始分析聊天记录...")
    analyzer = ChatlogAnalyzer()
    result = analyzer.analyze(chatlog_content)

    # 生成HTML报告
    print("[INFO] 生成HTML报告...")
    generator = HTMLReportGenerator()
    output_path = "/E/myProject/aicoding/AIhuang/wechatReport/一人公司启动孵化器_报告.html"
    generator.generate_report(result, output_path)

    print(f"\n[COMPLETE] 分析完成！")
    print(f"[SUCCESS] 报告已保存到: {output_path}")


if __name__ == '__main__':
    main()
