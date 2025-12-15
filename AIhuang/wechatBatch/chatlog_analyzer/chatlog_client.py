"""
Chatlog MCP API客户端
通过MCP协议获取聊天记录数据
"""

import json
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


class ChatlogMCPClient:
    """Chatlog MCP客户端"""

    def __init__(self, base_url: str = "http://127.0.0.1:5030"):
        """
        初始化客户端

        Args:
            base_url: MCP服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.sse_url = f"{base_url}/sse"

    def get_chat_messages(
        self,
        group_name: str,
        date: str = "yesterday",
        format_type: str = "json"
    ) -> List[Dict]:
        """
        获取指定群聊的消息

        Args:
            group_name: 群聊名称
            date: 日期 (today, yesterday, YYYY-MM-DD)
            format_type: 返回格式 (json, html, text)

        Returns:
            消息列表

        Raises:
            ConnectionError: 无法连接到MCP服务器
            ValueError: 响应数据无效
            TimeoutError: 请求超时
        """
        # 构建查询参数
        params = {
            "group": group_name,
            "format": format_type,
            "date": self._normalize_date(date)
        }

        try:
            # 通过SSE获取数据
            response = requests.get(
                self.sse_url,
                params=params,
                timeout=30,
                stream=True
            )
            response.raise_for_status()

            # 解析SSE响应
            messages = []
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                # SSE格式: data: {json}
                if line.startswith('data: '):
                    data_str = line[6:].strip()

                    # 检查是否是结束标记
                    if data_str == '[DONE]':
                        break

                    try:
                        data = json.loads(data_str)
                        messages.append(data)
                    except json.JSONDecodeError:
                        continue

            if not messages:
                raise ValueError(f"未找到群聊 '{group_name}' 在日期 '{date}' 的聊天记录")

            return messages

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"无法连接到Chatlog MCP服务器 ({self.sse_url})\n"
                "请确保MCP服务器正在运行: python chatlog_server.py"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f"获取群聊 '{group_name}' 的数据超时")
        except requests.exceptions.HTTPError as e:
            raise ConnectionError(f"HTTP错误: {str(e)}")

    def test_connection(self) -> bool:
        """
        测试MCP服务器连接

        Returns:
            连接是否成功
        """
        try:
            # 发送简单的测试请求
            response = requests.get(
                self.sse_url,
                params={"test": "ping"},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def _normalize_date(self, date_str: str) -> str:
        """
        标准化日期格式为YYYY-MM-DD

        Args:
            date_str: 输入日期

        Returns:
            标准化后的日期
        """
        date_str = date_str.lower().strip()

        if date_str == 'today':
            return datetime.now().strftime('%Y-%m-%d')
        elif date_str == 'yesterday':
            yesterday = datetime.now() - timedelta(days=1)
            return yesterday.strftime('%Y-%m-%d')
        elif re.match(r'^\d{4}年\d{1,2}月\d{1,2}日$', date_str):
            # 转换中文格式
            date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
            return date_str
        else:
            # 已经是标准格式或用户自定义
            return date_str

    def get_available_groups(self) -> List[str]:
        """
        获取可用的群聊列表

        Returns:
            群聊名称列表

        Note:
            需要MCP服务器支持群聊列表接口
        """
        try:
            response = requests.get(
                f"{self.base_url}/groups",
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('groups', [])
        except Exception:
            # 如果接口不支持，返回空列表
            return []

    def batch_get_messages(
        self,
        groups: List[Dict],
        delay: float = 0.5
    ) -> Dict[str, List[Dict]]:
        """
        批量获取多个群聊的消息

        Args:
            groups: 群聊配置列表
            delay: 请求间隔（秒）

        Returns:
            群聊名称到消息列表的映射
        """
        results = {}
        total = len(groups)

        for i, group in enumerate(groups, 1):
            group_name = group['name']
            print(f"[{i}/{total}] 正在获取群聊: {group_name}...")

            try:
                messages = self.get_chat_messages(
                    group_name,
                    group['date'],
                    group.get('format', 'json')
                )
                results[group_name] = messages
                print(f"  ✓ 获取到 {len(messages)} 条消息")
            except Exception as e:
                print(f"  ✗ 获取失败: {str(e)}")
                results[group_name] = []

            # 请求间隔，避免过频
            if i < total:
                time.sleep(delay)

        return results


# 导入re模块
import re
