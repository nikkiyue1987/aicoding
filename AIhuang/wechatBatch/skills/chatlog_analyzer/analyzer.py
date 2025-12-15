"""
分析模块 - 智能话题提取和分析
"""

import logging
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class ChatAnalyzer:
    """聊天数据分析器"""

    # 常见的停用词（中文）
    STOPWORDS = {
        '的', '一', '是', '在', '不', '了', '有', '和', '人', '这',
        '中', '大', '为', '上', '个', '国', '我', '以', '要', '他',
        '时', '来', '用', '们', '生', '到', '作', '地', '于', '出',
        '就', '分', '对', '成', '会', '可', '主', '发', '年', '动',
        '同', '工', '也', '能', '下', '过', '民', '前', '面', '都',
        '好', '自', '高', '产', '起', '电', '意', '见', '提', '公',
        '开', '它', '们', '还', '进', '热', '战', '等', '把', '那',
        '你', '她', '最', '或', '劳', '动', '其', '如', '很', '把',
        '只', '手', '把', '进', '行', '么', '又', '很', '啊', '呢',
    }

    def group_messages_by_time(
        self,
        messages: List[Dict[str, Any]],
        interval_minutes: int = 30
    ) -> List[List[Dict[str, Any]]]:
        """按时间间隔分组消息

        Args:
            messages: 消息列表
            interval_minutes: 时间间隔（分钟）

        Returns:
            分组的消息列表
        """
        if not messages:
            return []

        # 确保消息按时间排序
        sorted_messages = sorted(
            messages,
            key=lambda m: self._get_message_time(m)
        )

        groups = []
        current_group = []
        last_time = None

        for msg in sorted_messages:
            msg_time = self._get_message_time(msg)

            if last_time is None:
                current_group = [msg]
                last_time = msg_time
            else:
                # 检查时间差是否超过间隔
                time_diff = (msg_time - last_time).total_seconds() / 60
                if time_diff <= interval_minutes:
                    current_group.append(msg)
                else:
                    # 开始新的分组
                    if current_group:
                        groups.append(current_group)
                    current_group = [msg]
                    last_time = msg_time

        # 添加最后一个分组
        if current_group:
            groups.append(current_group)

        logger.info(f"将 {len(sorted_messages)} 条消息分组为 {len(groups)} 个话题")
        return groups

    def extract_topics(
        self,
        message_groups: List[List[Dict[str, Any]]],
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """从消息分组提取话题

        Args:
            message_groups: 分组的消息列表
            top_n: 返回的话题数量

        Returns:
            话题列表（包含标题、摘要、关键词等）
        """
        # 计算每个分组的分数
        scored_groups = []

        for i, group in enumerate(message_groups):
            score = self._score_group(group)
            scored_groups.append((i, group, score))

        # 按分数排序，获取前top_n
        top_groups = sorted(scored_groups, key=lambda x: x[2], reverse=True)[:top_n]

        topics = []
        for idx, (original_idx, group, score) in enumerate(top_groups):
            topic = {
                'order': idx + 1,
                'original_index': original_idx,
                'messages': group,
                'title': self._generate_title(group),
                'summary': self._generate_summary(group),
                'keywords': self._extract_keywords(group),
                'stats': {
                    'message_count': len(group),
                    'unique_speakers': len(set(m.get('user', 'unknown') for m in group)),
                    'char_count': sum(len(m.get('content', '')) for m in group),
                    'score': round(score, 2)
                },
                'time_range': self._get_time_range(group)
            }
            topics.append(topic)

        logger.info(f"提取了 {len(topics)} 个话题")
        return topics

    def _score_group(self, group: List[Dict[str, Any]]) -> float:
        """计算消息分组的分数

        基于：
        - 消息数量（权重：0.3）
        - 总文本长度（权重：0.3）
        - 参与者多样性（权重：0.2）
        - 关键词数量（权重：0.2）

        Args:
            group: 消息分组

        Returns:
            分数（0-100）
        """
        if not group:
            return 0

        # 消息数量分数 (最多10条为满分)
        message_score = min(len(group) / 10, 1.0) * 30

        # 文本长度分数 (最多500字为满分)
        total_chars = sum(len(m.get('content', '')) for m in group)
        length_score = min(total_chars / 500, 1.0) * 30

        # 参与者多样性分数
        speakers = set(m.get('user', 'unknown') for m in group)
        diversity_score = min(len(speakers) / 5, 1.0) * 20

        # 关键词分数
        keywords = self._extract_keywords(group)
        keyword_score = min(len(keywords) / 5, 1.0) * 20

        return message_score + length_score + diversity_score + keyword_score

    def _generate_title(self, group: List[Dict[str, Any]]) -> str:
        """生成话题标题

        Args:
            group: 消息分组

        Returns:
            话题标题
        """
        # 从关键词生成标题
        keywords = self._extract_keywords(group)

        if keywords:
            return f"话题：{' · '.join(keywords[:2])}"

        # 如果没有关键词，从第一条消息提取
        if group and 'content' in group[0]:
            content = group[0]['content']
            # 取前30个字符
            title = content[:30]
            if len(group[0]['content']) > 30:
                title += '...'
            return title

        return "话题讨论"

    def _generate_summary(self, group: List[Dict[str, Any]]) -> str:
        """生成话题摘要

        Args:
            group: 消息分组

        Returns:
            话题摘要
        """
        if not group:
            return ""

        # 合并所有消息内容
        contents = []
        for msg in group:
            if 'content' in msg:
                content = msg['content'].strip()
                if content:
                    contents.append(content)

        if not contents:
            return ""

        # 将所有内容合并并截断到150字
        summary = " ".join(contents)

        if len(summary) > 150:
            summary = summary[:147] + "..."

        return summary

    def _extract_keywords(
        self,
        group: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[str]:
        """提取话题关键词

        Args:
            group: 消息分组
            top_n: 返回的关键词数量

        Returns:
            关键词列表
        """
        # 合并所有文本
        all_text = " ".join(m.get('content', '') for m in group)

        # 分词（简单方式：按空格和标点符号分割）
        # 对于真实应用，应该使用专业的中文分词库如jieba
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', all_text)

        # 过滤停用词和短词
        keywords = [
            w for w in words
            if w not in self.STOPWORDS and len(w) >= 2
        ]

        # 计算词频
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1

        # 按频率排序，返回前top_n
        sorted_keywords = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        return [word for word, _ in sorted_keywords]

    def _get_time_range(self, group: List[Dict[str, Any]]) -> Dict[str, str]:
        """获取消息分组的时间范围

        Args:
            group: 消息分组

        Returns:
            {'start': '时间', 'end': '时间'} 字典
        """
        if not group:
            return {'start': '', 'end': ''}

        times = [self._get_message_time(m) for m in group]
        start_time = min(times)
        end_time = max(times)

        return {
            'start': start_time.strftime('%H:%M:%S'),
            'end': end_time.strftime('%H:%M:%S')
        }

    @staticmethod
    def _get_message_time(message: Dict[str, Any]) -> datetime:
        """从消息字典中提取时间

        Args:
            message: 消息字典

        Returns:
            datetime对象
        """
        # 支持多种时间字段名
        time_fields = ['timestamp', 'time', 'created_at', 'date']

        for field in time_fields:
            if field in message:
                time_value = message[field]

                if isinstance(time_value, datetime):
                    return time_value
                elif isinstance(time_value, str):
                    # 尝试解析ISO格式
                    try:
                        return datetime.fromisoformat(time_value)
                    except:
                        pass

                    # 尝试解析其他常见格式
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%H:%M:%S']:
                        try:
                            return datetime.strptime(time_value, fmt)
                        except:
                            pass

        # 如果没有找到时间字段，返回当前时间
        return datetime.now()
