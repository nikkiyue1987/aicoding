"""
批量群聊分析工具
通过Chatlog MCP获取聊天记录并进行智能分析
"""

__version__ = '1.0.0'
__author__ = 'Claude Code'

from .batch_analyzer import BatchAnalyzer
from .md_parser import MarkdownParser, GroupChatConfig
from .chatlog_client import ChatlogMCPClient
from .topic_analyzer import TopicAnalyzer
from .html_generator import HTMLGenerator

__all__ = [
    'BatchAnalyzer',
    'MarkdownParser',
    'GroupChatConfig',
    'ChatlogMCPClient',
    'TopicAnalyzer',
    'HTMLGenerator'
]
