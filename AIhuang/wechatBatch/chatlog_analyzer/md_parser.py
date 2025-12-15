"""
群聊清单Markdown解析模块
解析群聊清单.md文件，提取群聊名称和配置
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GroupChatConfig:
    """群聊配置"""
    name: str
    date: str  # 支持 'today', 'yesterday', 'YYYY-MM-DD' 等
    format: str = 'json'  # 默认JSON格式
    description: Optional[str] = None


class MarkdownParser:
    """Markdown清单解析器"""

    # 支持的配置键
    SUPPORTED_KEYS = {
        'date', 'format', '描述', 'description', '格式'
    }

    @classmethod
    def parse_group_chats(cls, file_path: str) -> List[GroupChatConfig]:
        """
        解析群聊清单Markdown文件

        Args:
            file_path: 清单文件路径

        Returns:
            群聊配置列表

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 格式错误
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"群聊清单文件不存在: {file_path}")

        # 按行分割并去除空行
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        group_chats = []
        current_group = None
        current_config = {}

        for line in lines:
            # 检查是否是群聊标题（以#开头）
            if line.startswith('#'):
                # 保存前一个群聊
                if current_group:
                    try:
                        group_chats.append(cls._build_config(current_group, current_config))
                    except ValueError as e:
                        raise ValueError(f"群聊 '{current_group}' 配置错误: {str(e)}")

                # 开始新群聊
                current_group = line.lstrip('#').strip()
                current_config = {}
                continue

            # 解析配置项 (key: value 或 key: value)
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                # 验证配置键
                if key in cls.SUPPORTED_KEYS or key in ['名称', 'name', '群聊', '群组']:
                    current_config[key] = value
            elif line.startswith('-'):
                # 支持无key的值（只指定日期）
                value = line.lstrip('- ').strip()
                if not current_config:
                    current_config['date'] = value

        # 处理最后一个群聊
        if current_group:
            try:
                group_chats.append(cls._build_config(current_group, current_config))
            except ValueError as e:
                raise ValueError(f"群聊 '{current_group}' 配置错误: {str(e)}")

        if not group_chats:
            raise ValueError("未找到任何群聊配置")

        return group_chats

    @classmethod
    def _build_config(cls, name: str, config: Dict[str, str]) -> GroupChatConfig:
        """
        构建群聊配置对象

        Args:
            name: 群聊名称
            config: 配置字典

        Returns:
            群聊配置对象
        """
        # 默认配置
        date = config.get('date', 'yesterday')
        format_type = config.get('format', 'json')
        description = config.get('description') or config.get('描述')

        # 验证日期格式
        if not cls._validate_date(date):
            raise ValueError(f"无效的日期格式: {date}")

        # 验证格式类型
        valid_formats = ['json', 'html', 'text']
        if format_type.lower() not in valid_formats:
            raise ValueError(f"无效的格式类型: {format_type}，支持: {', '.join(valid_formats)}")

        return GroupChatConfig(
            name=name,
            date=date,
            format=format_type.lower(),
            description=description
        )

    @classmethod
    def _validate_date(cls, date_str: str) -> bool:
        """
        验证日期格式

        Args:
            date_str: 日期字符串

        Returns:
            是否有效
        """
        # 支持 today, yesterday
        if date_str.lower() in ['today', 'yesterday']:
            return True

        # 支持 YYYY-MM-DD 格式
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False

        # 支持 YYYY年MM月DD日 格式
        if re.match(r'^\d{4}年\d{1,2}月\d{1,2}日$', date_str):
            try:
                datetime.strptime(date_str.replace('年', '-').replace('月', '-').replace('日', ''), '%Y-%m-%d')
                return True
            except ValueError:
                return False

        return False

    @classmethod
    def get_template(cls) -> str:
        """
        获取群聊清单模板

        Returns:
            Markdown模板字符串
        """
        return """# 群聊清单

请在下方列出需要分析的群聊及其配置：

## 群聊名称1
- date: yesterday
- format: json
- description: 这个群聊的描述

## 群聊名称2
- date: 2024-01-15
- format: json
- description: 另一个群聊

## 群聊名称3
- date: today
- format: html
"""
