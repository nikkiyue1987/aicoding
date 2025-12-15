#!/usr/bin/env python3
"""
API处理模块 - 与chatlog MCP通信（修复版）
修复了API端点和参数格式问题
"""

import requests
import json
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class ChatlogAPIHandler:
    """chatlog MCP API处理器（修复版）"""

    def __init__(self, api_url: str = "http://127.0.0.1:5030"):
        """初始化API处理器

        Args:
            api_url: API基础URL
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        self._chatrooms_cache = None  # 缓存群聊列表

    def get_chats(self) -> List[str]:
        """获取所有群聊列表

        Returns:
            群聊名称列表
        """
        try:
            url = f"{self.api_url}/api/v1/chatroom"
            logger.debug(f"请求: GET {url}")
            response = self.session.get(url)
            response.raise_for_status()

            # 解析表格格式的响应
            lines = response.text.strip().split('\n')

            chatrooms = []
            for line in lines[1:]:  # 跳过标题行
                if not line.strip():
                    continue

                # 解析CSV格式：ID, Remark, NickName, Owner, UserCount
                parts = line.split(',')
                if len(parts) >= 3:
                    chat_id = parts[0].strip()
                    remark = parts[1].strip()
                    nick_name = parts[2].strip()

                    # 使用Remark作为群聊名称，如果没有则使用NickName
                    name = remark if remark else nick_name

                    if name:
                        chatrooms.append(name)

            logger.info(f"获取到 {len(chatrooms)} 个群聊")
            return chatrooms

        except requests.RequestException as e:
            logger.error(f"获取群聊列表失败: {e}")
            raise

    def get_chatroom_list(self) -> List[Dict[str, str]]:
        """获取详细的群聊列表

        Returns:
            群聊信息列表，包含ID、名称、备注等
        """
        if self._chatrooms_cache is not None:
            return self._chatrooms_cache

        try:
            # 从chatroom API获取基本信息
            url = f"{self.api_url}/api/v1/chatroom"
            response = self.session.get(url)
            response.raise_for_status()

            lines = response.text.strip().split('\n')
            chatrooms_by_id = {}

            for line in lines[1:]:  # 跳过标题行
                if not line.strip():
                    continue

                parts = line.split(',')
                if len(parts) >= 1:
                    chat_id = parts[0].strip()
                    chatrooms_by_id[chat_id] = {
                        'id': chat_id,
                        'remark': parts[1].strip() if len(parts) > 1 else '',
                        'nick_name': parts[2].strip() if len(parts) > 2 else '',
                        'owner': parts[3].strip() if len(parts) > 3 else '',
                        'user_count': parts[4].strip() if len(parts) > 4 else '0',
                        'name': ''  # 待填充
                    }

            # 从session API获取群聊名称
            try:
                session_url = f"{self.api_url}/api/v1/session"
                session_response = self.session.get(session_url)
                session_lines = session_response.text.strip().split('\n')

                for line in session_lines:
                    line = line.strip()
                    if not line:
                        continue

                    # 格式：群聊名称(群聊ID) 时间戳 [最后消息]
                    match = re.match(r'^(.+?)\(([^)]+@chatroom)\)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', line)
                    if match:
                        chat_name = match.group(1).strip()
                        chat_id = match.group(2).strip()

                        if chat_id in chatrooms_by_id:
                            chatrooms_by_id[chat_id]['name'] = chat_name

            except Exception as e:
                logger.warning(f"获取会话信息失败: {e}")

            # 转换为列表
            chatrooms = list(chatrooms_by_id.values())

            # 如果仍然没有名称，使用ID作为名称
            for chat in chatrooms:
                if not chat['name']:
                    chat['name'] = chat['id'].split('@')[0]

            self._chatrooms_cache = chatrooms
            logger.info(f"获取到 {len(chatrooms)} 个群聊详情")
            return chatrooms

        except requests.RequestException as e:
            logger.error(f"获取群聊详情失败: {e}")
            return []

    def find_chatroom_by_name(self, name: str) -> Optional[str]:
        """根据群聊名称查找群聊ID

        Args:
            name: 群聊名称

        Returns:
            群聊ID，如果未找到则返回None
        """
        chatrooms = self.get_chatroom_list()

        # 精确匹配
        for chat in chatrooms:
            if chat['name'] == name or chat['remark'] == name:
                return chat['id']

        # 模糊匹配
        for chat in chatrooms:
            if name in chat['name'] or name in chat['remark']:
                logger.info(f"模糊匹配: '{name}' -> '{chat['name']}' (ID: {chat['id']})")
                return chat['id']

        logger.warning(f"未找到群聊: {name}")
        return None

    def get_chat_messages(
        self,
        chat_name: str,
        date: str,
        format: str = 'json'
    ) -> List[Dict[str, Any]]:
        """获取指定群聊的聊天消息

        Args:
            chat_name: 群聊名称
            date: 日期 (YYYY-MM-DD) 或日期范围 (YYYY-MM-DD~YYYY-MM-DD)
            format: 返回格式 ('json', 'text')

        Returns:
            消息列表
        """
        try:
            # 查找群聊ID
            chat_id = self.find_chatroom_by_name(chat_name)

            if not chat_id:
                logger.warning(f"未找到群聊 '{chat_name}' 的ID")
                return []

            # 构建API URL和参数
            url = f"{self.api_url}/api/v1/chatlog"
            params = {
                'talker': chat_id,
                'time': date,
                'format': format
            }

            logger.debug(f"请求: GET {url}?talker={chat_id}&time={date}&format={format}")
            response = self.session.get(url, params=params)
            response.raise_for_status()

            messages = self._parse_messages(response.text)

            logger.info(f"获取群聊 '{chat_name}' (ID: {chat_id}) 在 {date} 的 {len(messages)} 条消息")
            return messages

        except requests.RequestException as e:
            logger.error(f"获取群聊消息失败: {e}")
            return []
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return []

    def _parse_messages(self, content: str) -> List[Dict[str, Any]]:
        """解析消息内容

        Args:
            content: 原始消息内容

        Returns:
            解析后的消息列表
        """
        messages = []
        lines = content.strip().split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # 尝试匹配跨行格式：时间在行内任意位置
            if re.search(r'\d{1,2}:\d{2}:\d{2}', line):
                # 这是一个包含时间的行
                time_line = line
                content_line = ''

                # 查看下一行是否是内容
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # 如果下一行包含引号或明显的内容，则认为是消息内容
                    if next_line and ('"' in next_line or '说' in next_line or '发' in next_line):
                        content_line = next_line
                        i += 1  # 跳过下一行

                # 组合完整消息
                full_message = f"{time_line} {content_line}"

                # 解析消息
                message = self._parse_message_line(full_message)
                if message:
                    messages.append(message)
            else:
                # 单行消息
                message = self._parse_message_line(line)
                if message:
                    messages.append(message)

            i += 1

        return messages

    def _parse_message_line(self, line: str) -> Optional[Dict[str, Any]]:
        """解析单行消息

        Args:
            line: 消息行

        Returns:
            解析后的消息字典，如果解析失败则返回None
        """
        # 支持多种格式：
        # 1. 时间 发送者 消息内容 - 例如：15:58:33 张三 今天天气不错
        # 2. 发送者 时间 消息内容 - 例如：系统消息 15:58:33 撤回了一条消息

        # 格式2：发送者 时间 [消息内容]
        # 例如：系统消息 15:58:33 或 系统消息 15:58:33 "张三" 撤回了一条消息
        match = re.match(r'^(.+?)\s+(\d{1,2}:\d{2}:\d{2})\s*(.+)?$', line)
        if match:
            sender = match.group(1).strip()
            time_str = match.group(2)
            content = match.group(3).strip() if match.group(3) else ''

            # 提取真实发送者（如果是撤回消息）
            if '撤回了一条消息' in content:
                # 格式："发送者" 撤回了一条消息
                sender_match = re.match(r'^"(.+?)"\s+撤回了一条消息$', content)
                if sender_match:
                    actual_sender = sender_match.group(1)
                    content = f'"{actual_sender}" 撤回了一条消息'
                else:
                    # 保持原有格式
                    pass

            return {
                'timestamp': self._convert_time_to_datetime(time_str),
                'user': sender,
                'content': content
            }

        # 格式1：时间 发送者 消息内容
        match = re.match(r'^(\d{1,2}:\d{2}:\d{2})\s+(.+?)\s+(.+)$', line)
        if match:
            time_str = match.group(1)
            sender = match.group(2)
            content = match.group(3)

            return {
                'timestamp': self._convert_time_to_datetime(time_str),
                'user': sender,
                'content': content
            }

        return None

    def _convert_time_to_datetime(self, time_str: str) -> str:
        """将时间字符串转换为ISO格式

        Args:
            time_str: HH:MM:SS

        Returns:
            ISO格式的时间字符串
        """
        # 使用今天的日期作为基准
        today = datetime.now().strftime('%Y-%m-%d')
        datetime_str = f"{today}T{time_str}"

        try:
            # 验证时间格式
            dt = datetime.fromisoformat(datetime_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()

    def search_messages(
        self,
        chat_name: str,
        keyword: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索群聊消息

        Args:
            chat_name: 群聊名称
            keyword: 搜索关键词
            date_from: 开始日期
            date_to: 结束日期

        Returns:
            匹配的消息列表
        """
        try:
            # 查找群聊ID
            chat_id = self.find_chatroom_by_name(chat_name)
            if not chat_id:
                logger.warning(f"未找到群聊: {chat_name}")
                return []

            # 构建时间范围
            time_range = date_from
            if date_from and date_to:
                time_range = f"{date_from}~{date_to}"
            elif date_from:
                time_range = date_from

            # 构建API URL和参数
            url = f"{self.api_url}/api/v1/chatlog"
            params = {
                'talker': chat_id,
                'keyword': keyword
            }

            if time_range:
                params['time'] = time_range

            logger.debug(f"搜索消息: keyword={keyword}, time={time_range}")
            response = self.session.get(url, params=params)
            response.raise_for_status()

            messages = self._parse_messages(response.text)

            logger.info(f"在群聊 '{chat_name}' 中找到 {len(messages)} 条匹配消息")
            return messages

        except requests.RequestException as e:
            logger.error(f"搜索消息失败: {e}")
            return []

    def health_check(self) -> bool:
        """检查API是否可用

        Returns:
            API是否可用
        """
        try:
            url = f"{self.api_url}/health"
            response = self.session.get(url, timeout=5)
            is_healthy = response.status_code == 200
            logger.info(f"API健康检查: {'✓' if is_healthy else '✗'}")
            return is_healthy

        except Exception as e:
            logger.error(f"API不可用: {e}")
            return False

    def get_chat_info(self, chat_name: str) -> Dict[str, Any]:
        """获取群聊信息

        Args:
            chat_name: 群聊名称

        Returns:
            群聊信息
        """
        try:
            chatrooms = self.get_chatroom_list()
            chat_id = self.find_chatroom_by_name(chat_name)

            if not chat_id:
                return {}

            # 查找匹配的群聊
            for chat in chatrooms:
                if chat['id'] == chat_id:
                    return chat

            return {}

        except Exception as e:
            logger.error(f"获取群聊信息失败: {e}")
            return {}
