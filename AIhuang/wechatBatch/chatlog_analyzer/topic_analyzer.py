"""
话题分析模块
对聊天记录进行智能分析，提取话题
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Set
from collections import defaultdict, Counter
import re
import statistics


class TopicAnalyzer:
    """话题分析器"""

    # 时间窗口（分钟）
    TIME_WINDOW = 30

    # 关键词权重
    KEYWORD_WEIGHTS = {
        'question': 2.0,  # 问题
        'answer': 1.5,    # 回答
        'help': 2.0,      # 帮助
        'issue': 2.5,     # 问题/问题
        'solution': 2.0,  # 解决方案
        'important': 1.8, # 重要
        'urgent': 2.2,    # 紧急
        'bug': 2.5,       # Bug
        'feature': 2.0,   # 功能
        'update': 1.5,    # 更新
        'release': 1.8,   # 发布
        'meeting': 2.2,   # 会议
        'plan': 1.7,      # 计划
        'decision': 2.3,  # 决策
    }

    def __init__(self):
        """初始化分析器"""
        self.time_window = self.TIME_WINDOW

    def analyze_chat_data(self, messages: List[Dict]) -> Dict:
        """
        分析聊天数据，提取话题

        Args:
            messages: 消息列表

        Returns:
            分析结果
        """
        if not messages:
            return {
                'topics': [],
                'total_messages': 0,
                'total_participants': 0,
                'time_range': None
            }

        # 预处理消息
        processed_messages = self._preprocess_messages(messages)

        # 按时间分组
        time_groups = self._group_by_time(processed_messages)

        # 提取话题
        topics = self._extract_topics(time_groups)

        # 计算统计信息
        stats = self._calculate_stats(messages, processed_messages)

        return {
            'topics': topics,
            'total_messages': len(messages),
            'total_participants': len(set(msg.get('user', '') for msg in messages)),
            'time_range': self._get_time_range(processed_messages),
            **stats
        }

    def _preprocess_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        预处理消息

        Args:
            messages: 原始消息列表

        Returns:
            预处理后的消息列表
        """
        processed = []

        for msg in messages:
            # 提取时间和用户
            timestamp = msg.get('timestamp') or msg.get('time') or msg.get('date')
            user = msg.get('user') or msg.get('sender') or msg.get('from', '')
            content = msg.get('content') or msg.get('message') or msg.get('text', '')

            # 跳过无效消息
            if not content or not timestamp:
                continue

            # 解析时间
            try:
                if isinstance(timestamp, str):
                    # 尝试多种时间格式
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M']:
                        try:
                            dt = datetime.strptime(timestamp, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # 无法解析时间，跳过
                        continue
                elif isinstance(timestamp, (int, float)):
                    dt = datetime.fromtimestamp(timestamp)
                else:
                    continue

                processed.append({
                    'timestamp': dt,
                    'user': user,
                    'content': content,
                    'original': msg
                })
            except Exception:
                continue

        # 按时间排序
        processed.sort(key=lambda x: x['timestamp'])

        return processed

    def _group_by_time(self, messages: List[Dict]) -> Dict[datetime, List[Dict]]:
        """
        按时间窗口分组消息

        Args:
            messages: 预处理后的消息列表

        Returns:
            时间窗口到消息列表的映射
        """
        groups = defaultdict(list)

        if not messages:
            return groups

        # 获取第一个消息的时间
        start_time = messages[0]['timestamp']

        for msg in messages:
            # 计算时间窗口
            time_diff = msg['timestamp'] - start_time
            window_index = int(time_diff.total_seconds() // (self.time_window * 60))

            # 创建窗口时间（窗口开始时间）
            window_time = start_time + timedelta(minutes=window_index * self.time_window)

            groups[window_time].append(msg)

        return groups

    def _extract_topics(self, time_groups: Dict[datetime, List[Dict]]) -> List[Dict]:
        """
        从时间组中提取话题

        Args:
            time_groups: 时间分组

        Returns:
            话题列表
        """
        topics = []

        for window_time, window_messages in time_groups.items():
            if len(window_messages) < 3:  # 跳过消息太少的时间窗口
                continue

            # 分析话题
            topic = self._analyze_window(window_time, window_messages)
            if topic:
                topics.append(topic)

        # 按价值评分排序，选择前3个
        topics.sort(key=lambda x: x['score'], reverse=True)

        return topics[:3]

    def _analyze_window(self, window_time: datetime, messages: List[Dict]) -> Dict:
        """
        分析单个时间窗口

        Args:
            window_time: 窗口时间
            messages: 窗口内的消息

        Returns:
            话题信息
        """
        # 提取关键词
        keywords = self._extract_keywords(messages)

        # 计算参与者
        participants = list(set(msg['user'] for msg in messages))

        # 生成标题
        title = self._generate_title(keywords, messages)

        # 生成摘要
        summary = self._generate_summary(messages)

        # 计算评分
        score = self._calculate_topic_score(messages, keywords, participants)

        return {
            'title': title,
            'summary': summary,
            'keywords': keywords,
            'start_time': window_time,
            'end_time': window_time + timedelta(minutes=self.time_window),
            'message_count': len(messages),
            'participant_count': len(participants),
            'participants': participants,
            'score': score,
            'messages': [msg['original'] for msg in messages]
        }

    def _extract_keywords(self, messages: List[Dict]) -> List[str]:
        """
        提取关键词

        Args:
            messages: 消息列表

        Returns:
            关键词列表
        """
        # 合并所有文本
        text = ' '.join(msg['content'] for msg in messages)

        # 清理文本
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).lower()

        # 分词
        words = text.split()

        # 过滤停用词和短词
        stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '得', '之', '与', '能', '下', '而', '为', '以', '他', '时', '用', '什', '么', '想', '她', '中', '么', '可', '我们', '他们', '她们', '它们', '这个', '那个', '这里', '那里'}
        words = [w for w in words if len(w) >= 2 and w not in stop_words]

        # 统计词频
        word_counts = Counter(words)

        # 获取高频词作为关键词
        keywords = [word for word, count in word_counts.most_common(5)]

        return keywords

    def _generate_title(self, keywords: List[str], messages: List[Dict]) -> str:
        """
        生成话题标题

        Args:
            keywords: 关键词列表
            messages: 消息列表

        Returns:
            话题标题
        """
        if not keywords:
            # 没有关键词，使用消息内容
            first_msg = messages[0]['content'][:30]
            return f"话题: {first_msg}..."

        # 使用前2-3个关键词组合成标题
        title_keywords = keywords[:3]
        title = ' · '.join(title_keywords)

        # 检查是否有问题或讨论
        question_indicators = ['?', '？', '怎么', '如何', '为什么', '什么', '?', 'how', 'why', 'what']
        content_text = ' '.join(msg['content'] for msg in messages).lower()

        if any(indicator in content_text for indicator in question_indicators):
            title = f"讨论: {title}"
        else:
            title = f"话题: {title}"

        return title

    def _generate_summary(self, messages: List[Dict]) -> str:
        """
        生成话题摘要

        Args:
            messages: 消息列表

        Returns:
            话题摘要
        """
        # 获取前3条和后3条消息
        summary_messages = messages[:3] + messages[-3:] if len(messages) > 6 else messages

        # 提取摘要文本
        summary_texts = []
        for msg in summary_messages:
            content = msg['content']
            # 限制每条消息长度
            if len(content) > 100:
                content = content[:100] + '...'
            summary_texts.append(f"{msg['user']}: {content}")

        return ' | '.join(summary_texts)

    def _calculate_topic_score(
        self,
        messages: List[Dict],
        keywords: List[str],
        participants: List[str]
    ) -> float:
        """
        计算话题价值评分

        Args:
            messages: 消息列表
            keywords: 关键词列表
            participants: 参与者列表

        Returns:
            评分（0-10）
        """
        score = 0.0

        # 消息数量评分（最多3分）
        msg_count = len(messages)
        score += min(msg_count / 10, 3)

        # 参与者数量评分（最多2分）
        participant_count = len(participants)
        score += min(participant_count / 5, 2)

        # 内容长度评分（最多2分）
        total_length = sum(len(msg['content']) for msg in messages)
        score += min(total_length / 500, 2)

        # 关键词评分（最多2分）
        keyword_score = sum(self.KEYWORD_WEIGHTS.get(kw, 1.0) for kw in keywords)
        score += min(keyword_score / 5, 2)

        # 互动性评分（最多1分）
        # 计算是否有来回对话
        unique_users = set(msg['user'] for msg in messages)
        if len(unique_users) >= 2:
            # 检查是否有至少2轮对话
            conversations = 0
            current_user = None
            for msg in messages:
                if msg['user'] != current_user:
                    conversations += 1
                    current_user = msg['user']
            score += min(conversations / 10, 1)

        return min(score, 10)

    def _calculate_stats(self, original_messages: List[Dict], processed_messages: List[Dict]) -> Dict:
        """
        计算统计信息

        Args:
            original_messages: 原始消息
            processed_messages: 预处理后的消息

        Returns:
            统计信息
        """
        if not processed_messages:
            return {}

        # 用户活跃度
        user_counts = Counter(msg['user'] for msg in processed_messages)
        most_active = user_counts.most_common(5)

        # 消息长度分布
        msg_lengths = [len(msg['content']) for msg in processed_messages]
        avg_length = statistics.mean(msg_lengths) if msg_lengths else 0

        return {
            'most_active_users': [{'user': user, 'count': count} for user, count in most_active],
            'average_message_length': round(avg_length, 2),
            'peak_hour': self._get_peak_hour(processed_messages)
        }

    def _get_time_range(self, messages: List[Dict]) -> Dict:
        """
        获取时间范围

        Args:
            messages: 预处理后的消息

        Returns:
            时间范围信息
        """
        if not messages:
            return {}

        start_time = messages[0]['timestamp']
        end_time = messages[-1]['timestamp']

        return {
            'start': start_time.strftime('%Y-%m-%d %H:%M'),
            'end': end_time.strftime('%Y-%m-%d %H:%M'),
            'duration_minutes': int((end_time - start_time).total_seconds() / 60)
        }

    def _get_peak_hour(self, messages: List[Dict]) -> int:
        """
        获取最活跃小时

        Args:
            messages: 预处理后的消息

        Returns:
            小时（0-23）
        """
        if not messages:
            return 0

        hour_counts = Counter(msg['timestamp'].hour for msg in messages)
        return hour_counts.most_common(1)[0][0]
