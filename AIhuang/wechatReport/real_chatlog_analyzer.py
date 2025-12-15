#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量群聊分析工具 - 使用真实chatlog MCP
"""

import os
import sys
import json
import re
import argparse
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter


class ChatlogMCPClient:
    """Chatlog MCP客户端"""

    def __init__(self, mcp_url="http://127.0.0.1:5030/sse"):
        self.mcp_url = mcp_url

    def get_chatlog(self, group_name: str, date: str) -> List[Dict]:
        """从MCP获取聊天记录"""
        try:
            # 构建请求
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "get_chatlog",
                "params": {
                    "group_name": group_name,
                    "date": date
                }
            }

            print(f"[MCP] 请求聊天记录: {group_name} - {date}")

            # 发送请求
            response = requests.post(
                self.mcp_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    messages = data["result"]
                    print(f"[MCP] 成功获取 {len(messages)} 条消息")
                    return messages
                elif "error" in data:
                    print(f"[MCP] 错误: {data['error']}")
                    return []
            else:
                print(f"[MCP] HTTP错误: {response.status_code}")
                return []

        except requests.exceptions.ConnectionError:
            print(f"[MCP] 连接失败: 无法连接到 {self.mcp_url}")
            print("[MCP] 请确保chatlog MCP服务器正在运行")
            return []
        except Exception as e:
            print(f"[MCP] 异常: {str(e)}")
            return []

        return []


class MarkdownParser:
    """Markdown清单解析器"""

    def __init__(self):
        self.group_pattern = re.compile(r'^\s*-\s*([^\s:]+)\s*:\s*(.+)$', re.MULTILINE)

    def parse(self, file_path: str) -> List[Dict[str, str]]:
        """解析群聊清单MD文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            groups = []
            current_group = None
            lines = content.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 检测群组开始（以#开头的标题）
                if line.startswith('#'):
                    if current_group:
                        groups.append(current_group)
                    current_group = {
                        'name': line.lstrip('#').strip(),
                        'config': {}
                    }
                elif line.startswith('-') and current_group:
                    # 解析配置项
                    match = self.group_pattern.match(line)
                    if match:
                        key, value = match.groups()
                        current_group['config'][key.strip()] = value.strip()

            # 添加最后一个群组
            if current_group:
                groups.append(current_group)

            return groups

        except FileNotFoundError:
            raise Exception(f"找不到清单文件: {file_path}")
        except Exception as e:
            raise Exception(f"解析MD文件失败: {str(e)}")


class ChatlogAnalyzer:
    """聊天记录分析器"""

    def __init__(self):
        self.time_window = 30  # 30分钟时间窗口
        self.min_messages_per_topic = 3  # 每个话题最少消息数
        self.mcp_client = ChatlogMCPClient()

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
        stop_words = {'的', '了', '是', '在', '有', '和', '就', '都', '而', '及', '与', '或', '但', '不', '很', '也', '还', '要', '会', '能', '可', '我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', '这', '那', '这个', '那个', '什么', '怎么', '为什么', '哪里', '谁'}

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
                # 截取前50个字符
                summary_parts.append(content[:50] + ('...' if len(content) > 50 else ''))

        return ' | '.join(summary_parts) if summary_parts else "无有效内容"

    def analyze_group_chat(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个群聊"""
        try:
            # 获取群聊名称和配置
            group_name = group_data['name']
            config = group_data['config']

            print(f"[INFO] 开始分析群聊: {group_name}")

            # 解析日期配置
            date_str = self._parse_date_config(config.get('date', '昨天'))

            # 从chatlog MCP获取数据
            print(f"[INFO] 正在获取 {date_str} 的聊天记录...")
            messages = self.mcp_client.get_chatlog(group_name, date_str)

            if not messages:
                return {
                    'group_name': group_name,
                    'error': f'未找到 {date_str} 的聊天记录',
                    'topics': []
                }

            print(f"[INFO] 获取到 {len(messages)} 条消息")

            # 按时间分组
            print(f"[INFO] 按30分钟时间窗口分组...")
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
                'group_name': group_name,
                'total_messages': len(messages),
                'total_topics': len(time_groups),
                'analyzed_topics': len(topics),
                'analysis_date': datetime.now().isoformat(),
                'topics': topics
            }

        except Exception as e:
            return {
                'group_name': group_data['name'],
                'error': f"分析失败: {str(e)}",
                'topics': []
            }

    def _parse_date_config(self, date_config: str) -> str:
        """解析日期配置"""
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        if date_config == '昨天':
            return yesterday.strftime('%Y-%m-%d')
        elif date_config == '今天':
            return today.strftime('%Y-%m-%d')
        else:
            # 尝试解析具体日期
            try:
                datetime.strptime(date_config, '%Y-%m-%d')
                return date_config
            except:
                return yesterday.strftime('%Y-%m-%d')


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


class BatchChatlogAnalyzer:
    """批量群聊分析器"""

    def __init__(self):
        self.md_parser = MarkdownParser()
        self.analyzer = ChatlogAnalyzer()
        self.html_generator = HTMLReportGenerator()

    def analyze(self, config_file: str, output_dir: str = None):
        """执行批量分析"""
        try:
            # 解析配置
            print(f"[INFO] 正在解析清单文件: {config_file}")
            groups = self.md_parser.parse(config_file)

            if not groups:
                print("[ERROR] 未找到群聊配置")
                return

            print(f"[SUCCESS] 找到 {len(groups)} 个群聊配置")

            # 设置输出目录
            if not output_dir:
                date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = f"chatlog_reports_{date_str}"

            os.makedirs(output_dir, exist_ok=True)

            # 分析每个群聊
            results = []
            for i, group in enumerate(groups, 1):
                print(f"\n[ANALYZING] 正在分析群聊 {i}/{len(groups)}: {group['name']}")
                print(f"   配置: {group['config']}")

                # 分析群聊
                result = self.analyzer.analyze_group_chat(group)

                # 生成报告
                safe_name = re.sub(r'[^\w\s-]', '', group['name']).strip()
                safe_name = re.sub(r'[-\s]+', '-', safe_name)
                report_path = os.path.join(output_dir, f"{safe_name}_report.html")

                self.html_generator.generate_report(result, report_path)
                results.append(result)

            # 生成汇总报告
            self._generate_summary_report(results, output_dir)

            print(f"\n[COMPLETE] 分析完成！所有报告已保存到: {output_dir}")
            print(f"[SUCCESS] 请打开以下文件查看报告:")
            print(f"  - 汇总报告: {os.path.join(output_dir, 'summary.html')}")
            for result in results:
                if 'error' not in result:
                    safe_name = re.sub(r'[^\w\s-]', '', result['group_name']).strip()
                    safe_name = re.sub(r'[-\s]+', '-', safe_name)
                    print(f"  - {result['group_name']}: {os.path.join(output_dir, f'{safe_name}_report.html')}")

        except Exception as e:
            print(f"[ERROR] 分析失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def _generate_summary_report(self, results: List[Dict], output_dir: str):
        """生成汇总报告"""
        summary_path = os.path.join(output_dir, "summary.html")

        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>群聊分析汇总报告</title>
            {self.html_generator.base_style}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 群聊分析汇总报告</h1>
                    <div class="meta">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">{len(results)}</div>
                        <div class="stat-label">分析群聊数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{sum(r.get('total_messages', 0) for r in results)}</div>
                        <div class="stat-label">总消息数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{sum(r.get('analyzed_topics', 0) for r in results)}</div>
                        <div class="stat-label">总话题数</div>
                    </div>
                </div>

                <div class="topics">
                    {self._build_summary_topics_html(results)}
                </div>
            </div>
        </body>
        </html>
        """

        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"[SUCCESS] 汇总报告已生成: {summary_path}")

    def _build_summary_topics_html(self, results: List[Dict]) -> str:
        """构建汇总话题HTML"""
        topics_html = []

        for result in results:
            if 'error' in result:
                topic_html = f"""
                <div class="topic-card">
                    <h2 class="topic-title">{result['group_name']}</h2>
                    <div class="error">❌ {result['error']}</div>
                </div>
                """
            else:
                topics_html_list = []
                for topic in result['topics']:
                    topics_html_list.append(f"""
                    <div class="topic-card" style="margin: 10px 0;">
                        <h3>🏆 {result['group_name']} - 话题 {topic['rank']}</h3>
                        <div class="topic-meta">
                            <div class="meta-item">价值: {topic['score']}分</div>
                            <div class="meta-item">{topic['message_count']} 条消息</div>
                            <div class="meta-item">{topic['participant_count']} 位参与者</div>
                        </div>
                        <div class="summary">{topic['summary']}</div>
                        <div class="keywords">
                            {''.join(f'<span class="keyword-tag">{kw}</span>' for kw in topic['keywords'][:5])}
                        </div>
                    </div>
                    """)

                topics_html.append('\n'.join(topics_html_list))

        return '\n'.join(topics_html)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量群聊分析工具')
    parser.add_argument('config', nargs='?', default='群聊清单.md', help='群聊清单MD文件路径')
    parser.add_argument('-o', '--output', help='输出目录路径')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()

    analyzer = BatchChatlogAnalyzer()
    analyzer.analyze(args.config, args.output)


if __name__ == '__main__':
    main()
